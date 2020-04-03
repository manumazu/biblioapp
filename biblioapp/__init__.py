from flask import Flask, render_template, request, abort, flash, redirect, json, escape, session, url_for
from flask_bootstrap import Bootstrap
import flask_login, hashlib, base64
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_object("config")

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

bootstrap = Bootstrap(app)

from biblioapp import db, tools, models

global arduino_name, user_login

def initApp():
  user_login = False
  if(flask_login.current_user.is_authenticated):
    #prevent empty session for module : select first one
    if 'app_id' not in session:
      modules = db.get_arduino_for_user(flask_login.current_user.id)
      for module in modules:
        session['app_id'] = module['id']
        session['app_name'] = module['arduino_name']
        flash('Bookshelf "{}"selected'.format(module['arduino_name']))
        break
    user_login = flask_login.current_user.name  
    arduino_map = db.get_arduino_map(flask_login.current_user.id, session['app_id'])
    arduino_name = arduino_map['arduino_name']
  else:
    user_login = False
    arduino_map = None
    arduino_name = None
  return {'user_login':user_login,'arduino_map':arduino_map,'arduino_name':arduino_name}

@app.route("/", methods=['GET', 'POST'])
@flask_login.login_required
def selectArduino():
  if(flask_login.current_user.is_authenticated):
    modules = db.get_arduino_for_user(flask_login.current_user.id)
    if request.method == 'POST':
      if 'action' in request.form and request.form.get('action')=='select':
        session['app_id'] = request.form.get('module_id')
        session['app_name'] = request.form.get('module_name')
        flash('Bookshelf "{}"selected'.format(request.form.get('module_name')))
        return redirect(url_for('myBookShelf', _scheme='https', _external=True))
    return render_template('index.html', user_login=flask_login.current_user.name, modules=modules, biblio_name=session.get('app_name'))

@app.route("/module/<app_id>", methods=['GET', 'POST'])
@flask_login.login_required
def editArduino(app_id):
  if(flask_login.current_user.is_authenticated):
    module = db.get_arduino_map(flask_login.current_user.id, app_id)
    session['app_id'] = module['id']
    session['app_name'] = module['arduino_name']
    if request.method == 'POST':
      if request.is_json:
        data = request.get_json()
        for numrow in data:
          positions = data[numrow]
          for i in range(len(positions)):
            pos = i+1
            db.set_position(app_id, pos, pos, numrow, 1, 'static', positions[i])
    return render_template('module.html', user_login=flask_login.current_user.name, module=module, db=db)

@app.route('/authors/')
@flask_login.login_required
def listAuthors():
  globalVars = initApp()
  return render_template('authors.html', user_login=globalVars['user_login'], db=db, user_id=globalVars['arduino_map']['user_id'], \
    biblio_name=globalVars['arduino_map']['arduino_name'])

@app.route('/categories/')
@app.route('/categories/<uuid>/')
def listCategories(uuid = None):
  if(flask_login.current_user.is_authenticated):
    globalVars = initApp()
    user_id = globalVars['arduino_map']['user_id']
    categories = db.get_categories_for_user(user_id)
  elif uuid is None:
      return redirect(url_for('login', _scheme='https', _external=True))
  if uuid is not None:
    user_app = db.get_app_for_uuid(uuid)
    user = db.get_user_for_uuid(uuid)
    user_id = user['id']
    categories = db.get_categories_for_app(user_app['id'])
    data = {}
    data['list_title'] = user_app['arduino_name']
    hashmail = hashlib.md5(user['email'].encode('utf-8')).hexdigest()
    for i in range(len(categories)):
      categories[i]['url'] = url_for('locateBooksForTag',tag_id=categories[i]['id'])
      categories[i]['token'] = hashmail
      if categories[i]['color'] is not None:
        colors = categories[i]['color'].split(",")
        categories[i]['red'] = colors[0]
        categories[i]['green'] = colors[1]
        categories[i]['blue'] = colors[2]
    data['elements']=categories
    response = app.response_class(
      response=json.dumps(data),
      mimetype='application/json'
    )
    return response
  else:
    return render_template('categories.html', user_login=globalVars['user_login'], categories=categories, \
    biblio_name=globalVars['arduino_map']['arduino_name'])


@app.route("/app/")
@flask_login.login_required
def myBookShelf():
  globalVars = initApp()
  app_id = globalVars['arduino_map']['id']
  if request.method == 'GET' and request.args.get('rownum'):
    shelfs = [int(request.args.get('rownum'))]
  else:
    shelfs = range(1,globalVars['arduino_map']['nb_lines']+1)
  elements = {}
  for shelf in shelfs:
    books = db.get_books_for_row(app_id, shelf)
    if books:
      statics = db.get_static_positions(app_id, shelf)
      element = {}
      for row in books:     
        element[row['led_column']] = {'item_type':row['item_type'],'id':row['id'], \
    'title':row['title'], 'author':row['author'], 'position':row['position'], 'borrowed':row['borrowed'], \
    'url':'/book/'+str(row['id'])}
        requested = db.get_request_for_position(app_id, row['position'], shelf)
        if requested:
          element[row['led_column']]['requested']=True
      if statics:
        for static in statics:
          element[static['led_column']] = {'item_type':static['item_type'],'id':None, 'position':static['position']}
      elements[shelf] = sorted(element.items())
  bookstorange = db.get_books_to_range(globalVars['arduino_map']['user_id']) #books without position
  return render_template('bookshelf.html',user_login=globalVars['user_login'], tidybooks=elements, \
      bookstorange=bookstorange, lines=shelfs, \
      biblio_name=globalVars['arduino_map']['arduino_name'])


@app.route("/ajax_positions_inline/", methods=['GET'])
@flask_login.login_required
def jsonBookshelf(): 
  globalVars = initApp()
  app_id = globalVars['arduino_map']['id']  
  if request.method == 'GET' and request.args.get('row'):
    numrow = request.args.get('row')
    books = db.get_books_for_row(app_id, numrow)
    element = {}
    for row in books:
      element[row['led_column']] = {'item_type':row['item_type'],'id':row['id'], \
    'title':row['title'], 'author':row['author'], 'position':row['position'], 'url':'/book/'+str(row['id'])}
      requested = db.get_request_for_position(app_id, row['position'], numrow)
      if requested:
        element[row['led_column']]['requested']=True
    element = sorted(element.items())
    response = app.response_class(
      response=json.dumps(element),
      mimetype='application/json'
    )
    return response


@app.route('/ajax_sort/', methods=['POST'])
@flask_login.login_required
def ajaxSort():
  globalVars = initApp()
  if request.method == 'POST' and session.get('app_id'):
    current_row = request.form['row'] 
    book_ids = request.form.getlist('book[]')
    sortable = db.sort_items(session.get('app_id'), globalVars['arduino_map']['user_id'], book_ids, current_row)
    response = app.response_class(
        response=json.dumps(sortable),
        mimetype='application/json'
    )
  return response

@app.route('/ajax_set_position/', methods=['POST'])
@flask_login.login_required
def ajaxSetPosition():
  globalVars = initApp()
  if request.method == 'POST' and session.get('app_id'):
    book_id = request.form.get('book_id')
    leds_range = request.form.get('range')
    column = request.form.get('column');
    row = request.form.get('row')
    led_column = db.set_position(session.get('app_id'), book_id, column, row, leds_range, 'book')
    ret={'led_column':int(led_column)}
    response = app.response_class(
          response=json.dumps(ret),
          mimetype='application/json'
    )
    return response

@app.route('/ajax_del_position/', methods=['POST'])
@flask_login.login_required
def ajaxDelPosition():
  globalVars = initApp()
  if request.method == 'POST' and session.get('app_id'):
    for elem in request.form:
       book = elem.split('_')
       if db.del_item_position(session.get('app_id'), book, globalVars['arduino_map']['user_id']):
         ret={'success':True}
       else:
         ret={'success':False}
  response = app.response_class(
        response=json.dumps(ret),
        mimetype='application/json'
  )
  return response

@app.route('/tag/<tag_id>')
@flask_login.login_required
def listNodesForTag(tag_id):
  globalVars = initApp()
  nodes = db.get_node_for_tag(tag_id, globalVars['arduino_map']['user_id'])
  tag = db.get_tag_by_id(tag_id)
  data = {}
  data['list_title'] = tag['tag']
  if nodes:
      books = []
      #for node in nodes:
      for i in range(len(nodes)):
          book = db.get_book(nodes[i]['id_node'], globalVars['arduino_map']['user_id'])
          books.append(book)
          app_modules = db.get_arduino_for_user(flask_login.current_user.id)
          for module in app_modules:
            address = db.get_position_for_book(module['id'], book['id'])
            if address:
              hasRequest = db.get_request_for_position(module['id'], address['position'], address['row'])
              books[i]['address'] = address
              books[i]['arduino_name'] = module['arduino_name']
              books[i]['app_id'] = module['id']
              books[i]['app_uuid'] = module['uuid']
              books[i]['app_mac'] = module['mac']
              books[i]['hasRequest'] = hasRequest
      data['items'] = books
  #send json when token mode
  if('token' in request.args):
    response = app.response_class(
      response=json.dumps(data),
      mimetype='application/json'
    )
    return response     
  return render_template('tag.html', books=books, user_login=globalVars['user_login'], \
    biblio_name=globalVars['arduino_map']['arduino_name'], tag=tag)

@app.route('/ajax_tag_color/<tag_id>', methods=['POST'])
@flask_login.login_required
def ajaxTagColor(tag_id):
  if request.method == 'POST':
    red = request.form['red'] 
    green = request.form['green'] 
    blue = request.form['blue']
    color = red+','+green+','+blue
    result = False
    if db.set_color_for_tag(tag_id, color):
      result = True
    response = app.response_class(
      response=json.dumps(result),
      mimetype='application/json'
    )
    return response


@app.route('/book/<book_id>')
@flask_login.login_required
def getBook(book_id):
  globalVars = initApp()
  book = db.get_book(book_id, globalVars['arduino_map']['user_id'])
  if book:
    book['address']=None
    book['hasRequest']=None
    book['categories'] = []
    tags = db.get_tag_for_node(book['id'], 1)#book tags for taxonomy categories
    if tags:
      for i in range(len(tags)):
        book['categories'].append(tags[i]['tag'])
    app_modules = db.get_arduino_for_user(flask_login.current_user.id)
    for module in app_modules:
      address = db.get_position_for_book(module['id'], book['id'])
      if address:
        hasRequest = db.get_request_for_position(module['id'], address['position'], address['row'])
        book['address'] = address
        book['arduino_name'] = module['arduino_name']
        book['app_id'] = module['id']
        book['hasRequest'] = hasRequest
    #send json when token mode
    if('token' in request.args):
      response = app.response_class(
        response=json.dumps(book),
        mimetype='application/json'
      )
      return response      
    return render_template('book.html', user_login=globalVars['user_login'], book=book, \
        biblio_name=globalVars['arduino_map']['arduino_name'], biblio_nb_rows=globalVars['arduino_map']['nb_lines'])
  abort(404)

@app.route('/ajax_categories/')
@flask_login.login_required
def ajaxCategories():
  globalVars = initApp()
  user_taxo = []
  other_categ = db.get_categories_for_term(request.args.get('term'))
  if other_categ:
    for i in range(len(other_categ)):
      user_taxo.append(other_categ[i]['tag'])
  response = app.response_class(
    response=json.dumps(user_taxo),
    mimetype='application/json'
  )
  return response

#post request from app
@app.route('/borrow/', methods=['GET'])
@flask_login.login_required
def borrowBook():
  globalVars = initApp()
  ret = []
  if (request.method == 'GET') and ('token' in request.args):
    app_id = request.args.get('app_id')
    book_id = request.args.get('book_id')
    action = request.args.get('action')
    db.set_borrow_book(app_id, book_id, action)
    address = db.get_position_for_book(app_id, book_id)
  if('token' in request.args):
    ret.append({'item':book_id,'action':'borrow','address':address}) 
    response = app.response_class(
      response=json.dumps(ret),
      mimetype='application/json'
    )
    return response    

#post request from app
@app.route('/locate/', methods=['GET', 'POST'])
@flask_login.login_required
def locateBook():
  globalVars = initApp()
  action = 'add'
  ret = []

  '''get form request params'''
  if (request.method == 'POST'):
    app_id = request.form.get('app_id')
    column = request.form.get('column')
    row = request.form.get('row')
    book_id = request.form.get('book_id')
    leds_range = request.form.get('range')
    address = db.get_position_for_book(app_id, book_id)
    led_column = db.set_position(app_id, book_id, column, row, leds_range, 'book')
    #led_column = request.form.get('led_column')
    if 'remove_request' in request.form:
      action = 'remove'

  '''get params from arduino'''      
  if (request.method == 'GET') and ('token' in request.args):
    app_id = request.args.get('app_id')
    book_id = request.args.get('book_id')
    address = db.get_position_for_book(app_id, book_id)    
    if 'remove_request' in request.args:
      action = 'remove'

  if action == 'remove':
    db.del_request(app_id, address['position'], address['row'])
    retMsg = 'Location removed for book {}'.format(book_id)
  else: 
    db.set_request(app_id, address['row'], address['position'], address['range'], address['led_column'])
    retMsg = 'Location requested for book {}'.format(book_id)

  if('token' in request.args):
    ret.append({'item':book_id,'action':action,'address':address})    
    response = app.response_class(
      response=json.dumps(ret),
      mimetype='application/json'
    )
    return response
    
  flash(retMsg)
  if(request.referrer and 'tag' in request.referrer):
    return redirect(url_for('listAuthors', _scheme='https', _external=True))
  return redirect(url_for('myBookShelf', _scheme='https', _external=True))

@app.route('/locate_for_tag/<tag_id>')  
@flask_login.login_required
def locateBooksForTag(tag_id):
  globalVars = initApp()
  nodes = db.get_node_for_tag(tag_id, globalVars['arduino_map']['user_id'])
  tag = db.get_tag_by_id(tag_id)
  if tag['color'] is not None:
    colors = tag['color'].split(",")
    tag['red'] = colors[0]
    tag['green'] = colors[1]
    tag['blue'] = colors[2]

  if('uuid' in request.args):
    module = db.get_app_for_uuid(request.args.get('uuid'))
  else:
    module = db.get_app_for_uuid(globalVars['arduino_map']['id_ble'])
  #app_modules = db.get_arduino_for_user(flask_login.current_user.id)

  action = 'add'
  if('action' in request.args):#for add or remove
    action = request.args.get('action')

  mode = ''
  if('mode' in request.args):
    mode = request.args.get('mode')

  #for module in app_modules:
  if(mode!='toggle'):
    db.clean_request(module['id'])#clean all module's request

  element = {}
  for node in nodes:
    address = db.get_position_for_book(module['id'], node['id_node'])
    if address:
      book = db.get_book(node['id_node'], globalVars['arduino_map']['user_id'])
      if(action=='add'):#add request for tag's nodes
        db.set_request(module['id'], address['row'], address['position'], address['range'], address['led_column'])
      if(action=='remove'):#delete request for tag's nodes
        db.del_request(module['id'], address['position'], address['row'])
      keysort = str(address['position'])+'00'+str(address['row'])
      element[int(keysort)] = {'item':book['title'],'action':action,'address':address,'tag':tag}      
  if(action=='remove'):
    element = sorted(element.items(), reverse = True)
  else:
    element = sorted(element.items())

  ret = []
  for elem in element:
    if elem[1] is not None:
      ret.append(elem[1])
  #send json when token mode
  if('token' in request.args):
    response = app.response_class(
      response=json.dumps(ret),
      mimetype='application/json'
    )
    return response
  for book_title in ret:
    flash('Location requested for book {}'.format(book_title['item']))
  return redirect(url_for('listAuthors', _scheme='https', _external=True))

#get request from arduino for current arduino_name
@app.route('/request/<uuid>/')
def getRequestForModule(uuid):
  user_app = db.get_app_for_uuid(uuid)
  if(user_app):
    element = {}
    datas = db.get_request(user_app['id'])
    if datas:
      for data in datas:
        keysort = str(data['column'])+'00'+str(data['row'])
        element[int(keysort)] = {'action':'add','address':data}
      element = sorted(element.items())

      #format array for json output (remove key)
      ret = []
      for elem in element:
        if elem[1] is not None:
          ret.append(elem[1])

      response = app.response_class(
            response=json.dumps(ret),
            mimetype='application/json'
      )
      return response
  abort(404)

#remove all request from arduino for current module
'''todo : must be protected'''
@app.route('/reset/<uuid>/')
def setResetForModule(uuid):
  user_app = db.get_app_for_uuid(uuid)
  if(user_app):
    data = db.clean_request(user_app['id'])#clean all module's request
    response = app.response_class(
          response=json.dumps(data),
          mimetype='application/json'
    )
    return response
  abort(404)  

#get module infos from arduino for current arduino_name
@app.route('/module/<uuid>/')
def getModule(uuid):
  user_app = db.get_app_for_uuid(uuid)
  if(user_app):
    data = user_app
    response = app.response_class(
          response=json.dumps(data),
          mimetype='application/json'
    )
    return response
  abort(404)  

#get authors liste from arduino for current arduino_name
@app.route('/authors/<uuid>/')
def listAuthorsForModule(uuid):
  user_app = db.get_app_for_uuid(uuid)
  user = db.get_user_for_uuid(uuid)
  data = {}
  if(user_app):
    data['list_title'] = user_app['arduino_name']
    data['elements']=[]
    alphabet = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]
    for j in range(len(alphabet)):
      '''data['elements'][j]={}
      data['elements'][j]['initial']=alphabet[j]'''
      #print(data)
      items = db.get_authors_for_app(user_app['id'], alphabet[j])
      if items:
        '''set url for authenticate requesting location from app'''
        for i in range(len(items)):
          hashmail = hashlib.md5(user['email'].encode('utf-8')).hexdigest()
          items[i]['url'] = url_for('locateBooksForTag',tag_id=items[i]['id'])
          items[i]['token'] = hashmail
        #data['elements'][j]['items'] = items
      data['elements'].append({'initial':alphabet[j],'items':items})

    response = app.response_class(
          response=json.dumps(data),
          mimetype='application/json'
    )
    return response
  abort(404)    

@app.route('/booksearch/', methods=['GET', 'POST'])
@flask_login.login_required
def searchBookReference():
  import requests
  globalVars = initApp()
  '''search on api'''
  if request.method == 'POST':
    query = "key=AIzaSyBVwKgWVqNaLwgceI_b3lSJJAGLw_uCDos&q="
    if 'isbn' in request.form and request.form['isbn']:
      query += "ISBN:\""+request.form['isbn']+"\"&"
    if 'inauthor' in request.form and request.form['inauthor']:
      query += "inauthor:"+request.form['inauthor']+"+"
    if 'intitle' in request.form and request.form['intitle']:
      query += "intitle:"+request.form['intitle']
    if 'query' in request.form:
      query += request.form['query']
    url = "https://www.googleapis.com/books/v1/volumes?"+query
    r = requests.get(url)
    data = r.json()
    #print(url)
    return render_template('booksearch.html', user_login=globalVars['user_login'], data=data, req=request.form, \
      biblio_name=globalVars['arduino_map']['arduino_name'])

  '''get detail on api'''
  if request.method == 'GET' and request.args.get('ref'):
    ref = request.args.get('ref')
    book = {}
    if ref != 'new':
      r = requests.get("https://www.googleapis.com/books/v1/volumes/"+ref)
      data = r.json()
      book = data['volumeInfo']
    #print(data['volumeInfo'])
    return render_template('booksearch.html', user_login=globalVars['user_login'], book=book, ref=ref, \
      biblio_name=globalVars['arduino_map']['arduino_name'])
  else:
    return render_template('booksearch.html', user_login=globalVars['user_login'], \
      biblio_name=globalVars['arduino_map']['arduino_name'])

@app.route('/bookreferencer/', methods=['POST'])
@flask_login.login_required
def bookReferencer():
  globalVars = initApp()
  if request.method == 'POST':
    authors = request.form.getlist('authors[]')
    bookapi={}
    bookapi['author'] = ', '.join(authors)
    bookapi['title'] = request.form['title']
    bookapi['reference'] = request.form['reference']
    bookapi['isbn'] = request.form['isbn']
    bookapi['description'] = request.form['description']
    bookapi['editor'] = request.form['editor']
    bookapi['pages'] = request.form['pages']
    bookapi['year'] = request.form['year']
    if 'id' in request.form:
      bookapi['id'] = request.form['id']
    bookId = db.set_book(bookapi, globalVars['arduino_map']['user_id'])
    '''manage tags + taxonomy'''
    authorTags = tools.getLastnameFirstname(authors)
    authorTagids = db.set_tags(authorTags,'Authors')
    if len(authorTagids)>0:
      db.set_tag_node(bookId, authorTagids)    
    db.clean_tag_for_node(bookId['id'], 1) #clean tags categories  before update
    categ = request.form['tags']
    if len(categ)>0:
      catTagIds = db.set_tags(categ.split(','),'Categories')
      if len(catTagIds)>0:
        db.set_tag_node(bookId, catTagIds)
    return redirect(url_for('myBookShelf', _scheme='https', _external=True))
  return render_template('bookreferencer.html', user_login=globalVars['user_login'])


@app.route('/bookdelete/', methods=['POST'])
@flask_login.login_required
def bookDelete():
  globalVars = initApp()
  book_id = request.form['id']
  book = db.get_book(book_id, globalVars['arduino_map']['user_id'])
  if book: 
    db.clean_tag_for_node(book_id, 1)#clean tags for categories
    db.clean_tag_for_node(book_id, 2)#clean tags for authors
    db.del_book(book_id, globalVars['arduino_map']['user_id'])
    flash('Book "{}" is deleted'.format(book['title']))
    return redirect(url_for('myBookShelf', _scheme='https', _external=True))


@app.route('/customcodes/', methods=['GET', 'POST'])
@flask_login.login_required
def customCodes():
  globalVars = initApp()
  if request.method == 'POST':
    if request.is_json:
        json_customcode = request.get_json()
        db.set_customcode(globalVars['arduino_map']['user_id'], session['app_id'], None, None, json_customcode)
        #print(json_customcode)
        #print(request.data.decode())
  return render_template('customcodes.html', user_login=globalVars['user_login'])

@app.route('/customcode/<code_id>')
@flask_login.login_required
def customCode(code_id):
  globalVars = initApp()
  data = db.get_customcode(globalVars['arduino_map']['user_id'], session['app_id'], code_id)
  return render_template('customcode.html', user_login=globalVars['user_login'], customcode=data['customcode'].decode())

'''
Authentication
'''
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    email = request.form['email']
    exists = db.get_user(email)
    if exists is not None:
      #hash = generate_password_hash(exists['password'])
      if check_password_hash(exists['password'],request.form['password']):

        user = models.User()
        user.id = email
        user.name = exists['name'] 
        flask_login.login_user(user)
        return redirect(url_for('selectArduino', _scheme='https', _external=True))

      return 'Bad login'

@app.route('/logout')
def logout():
    flask_login.logout_user()
    flash('Logged out')
    return redirect(url_for('login', _scheme='https', _external=True))

if __name__ == "__main__":
    app.run(debug=True)
