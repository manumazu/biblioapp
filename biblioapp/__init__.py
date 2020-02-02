from flask import Flask, render_template, request, abort, flash, redirect, json, escape, session, url_for
from flask_bootstrap import Bootstrap
import flask_login, hashlib
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_object("config")

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

Bootstrap(app)

from biblioapp import db, tools, models

global arduino_name, user_login

def initApp():
  user_login = False
  if(flask_login.current_user.is_authenticated):
    user_login = flask_login.current_user.name  
    arduino_map = db.get_arduino_map(flask_login.current_user.id, session['app_id'])
    arduino_name = arduino_map['arduino_name']
  else:
    user_login = False
    arduino_map = None
    arduino_name = None
  return {'user_login':user_login,'arduino_map':arduino_map,'arduino_name':arduino_name}

@app.route("/", methods=['GET', 'POST'])
def selectArduino():
  if(flask_login.current_user.is_authenticated):
    modules = db.get_arduino_for_user(flask_login.current_user.id)
    if request.method == 'POST' and request.form.get('module_id'):
      session['app_id'] = request.form.get('module_id')
      session['app_name'] = request.form.get('module_name')
      flash('Bookshelf "{}"selected'.format(request.form.get('module_name')))
      return redirect(url_for('myBookShelf', _scheme='https', _external=True))# _scheme='https',
    return render_template('index.html', user_login=flask_login.current_user.name, modules=modules, biblio_name=session.get('app_name'))
  return redirect(url_for('login', _scheme='https', _external=True))#_scheme='https',

@app.route('/authors/')
def listAuthors():
  globalVars = initApp()
  if(globalVars['user_login']==False):
    return redirect('/login')
  return render_template('authors.html', user_login=globalVars['user_login'], db=db, user_id=globalVars['arduino_map']['user_id'], \
    biblio_name=globalVars['arduino_map']['arduino_name'])

@app.route('/categories/')
def listCategories():
  globalVars = initApp()
  if(globalVars['user_login']==False):
    return redirect('/login')
  categories = db.get_categories_for_user(globalVars['arduino_map']['user_id'])
  return render_template('categories.html', user_login=globalVars['user_login'], categories=categories, \
    biblio_name=globalVars['arduino_map']['arduino_name'])

@app.route("/ajax_positions_inline/", methods=['GET'])
@app.route("/app/")
def myBookShelf():
  globalVars = initApp()
  if(globalVars['user_login']==False):
    return redirect('/login')
    
  if request.method == 'GET' and request.args.get('row'):
    row = request.args.get('row')
  else:
    row = None
  tidybooks = db.get_tidy_books(globalVars['arduino_map']['id'], row) #books with addresses
  bookstorange = db.get_books_to_range(globalVars['arduino_map']['user_id']) #books with position
  #search requested books in tidy books 
  requested_books = db.get_request(globalVars['arduino_map']['id'])
  if requested_books:
   for requested in requested_books:
     if requested['row'] in tidybooks:
       if requested['column'] in tidybooks[requested['row']]:
         tidybooks[requested['row']][requested['column']]['requested']=True
  if request.method == 'GET' and request.args.get('row'):
    response = app.response_class(
      response=json.dumps(tidybooks[int(row)]),
      mimetype='application/json'
    )
    return response
  else:
    return render_template('bookshelf.html',user_login=globalVars['user_login'], tidybooks=tidybooks, \
      bookstorange=bookstorange, biblio_nb_rows=globalVars['arduino_map']['nb_lines'], \
      biblio_name=globalVars['arduino_map']['arduino_name'])

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

@app.route('/ajax_del_position/', methods=['POST'])
@flask_login.login_required
def ajaxDelPosition():
  if request.method == 'POST' and session.get('app_id'):
    for elem in request.form:
       book = elem.split('_')
       if db.del_item_position(session.get('app_id'), book):
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
    biblio_name=globalVars['arduino_map']['arduino_name'], author=tag['tag'])  

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
    led_column = request.form.get('led_column')  
    if 'remove_request' in request.form:
      action = 'remove'

  '''get params from arduino'''      
  if (request.method == 'GET') and ('token' in request.args):
    app_id = request.args.get('app_id')
    column = request.args.get('column')
    row = request.args.get('row')
    book_id = request.args.get('book_id')
    leds_range = request.args.get('range')
    led_column = request.args.get('led_column')
    address = {}
    address['range'] = leds_range
    address['led_column'] = led_column
    address['position'] = column
    address['row'] = row
    if 'remove_request' in request.args:
      action = 'remove'

  if action == 'remove':
    db.del_request(app_id, column, row)
    retMsg = 'Location removed for book {}'.format(book_id)
  else: 
    db.set_request(app_id, row, column, leds_range, led_column)
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
    return redirect('/authors')
  return redirect('/app')

@app.route('/locate_for_tag/<tag_id>')  
@flask_login.login_required
def locateBooksForTag(tag_id):
  globalVars = initApp()
  nodes = db.get_node_for_tag(tag_id, globalVars['arduino_map']['user_id'])

  if('uuid' in request.args):
    module = db.get_app_for_uuid(request.args.get('uuid'))
  else:
    module = db.get_app_for_uuid(globalVars['arduino_map']['id_ble'])
  #app_modules = db.get_arduino_for_user(flask_login.current_user.id)

  ret = []
  action = 'add'
  if('action' in request.args):#for add or remove
    action = request.args.get('action')

  mode = ''
  if('mode' in request.args):
    mode = request.args.get('mode')

  #for module in app_modules:
  if(mode!='toggle'):
    db.clean_request(module['id'])#clean all module's request

  for node in nodes:
    address = db.get_position_for_book(module['id'], node['id_node'])
    if address:
      book = db.get_book(node['id_node'], globalVars['arduino_map']['user_id'])
      if(action=='add'):#add request for tag's nodes
        led_column = db.set_request(module['id'], address['row'], address['position'], address['range'], address['led_column'])
      if(action=='remove'):#delete request for tag's nodes
        db.del_request(module['id'], address['position'], address['row'])
      ret.append({'item':book['title'],'action':action,'address':address})
  #send json when token mode
  if('token' in request.args):
    response = app.response_class(
      response=json.dumps(ret),
      mimetype='application/json'
    )
    return response
  for book_title in ret:
    flash('Location requested for book {}'.format(book_title['item']))
  return redirect('/authors')


#get request from arduino for current arduino_name
@app.route('/request/<uuid>/')
def getRequestForModule(uuid):
  user_app = db.get_app_for_uuid(uuid)
  if(user_app):
    data = db.get_request(user_app['id'])
    response = app.response_class(
          response=json.dumps(data),
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
    return render_template('booksearch.html', user_login=globalVars['user_login'], data=data, req=request.form)

  '''get detail on api'''
  if request.method == 'GET' and request.args.get('ref'):
    ref = request.args.get('ref')
    r = requests.get("https://www.googleapis.com/books/v1/volumes/"+ref)
    data = r.json()
    #print(data['volumeInfo'])
    return render_template('booksearch.html', user_login=globalVars['user_login'], book=data['volumeInfo'], ref=ref)
  else:
    return render_template('booksearch.html', user_login=globalVars['user_login'])

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
    return redirect('/')
  return render_template('bookreferencer.html', user_login=globalVars['user_login'])


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
        return redirect('/protected')

      return 'Bad login'

@app.route('/protected')
@flask_login.login_required
def protected():
  flash('Logged in as: ' + flask_login.current_user.name)
  return redirect('/')

@app.route('/logout')
def logout():
    flask_login.logout_user()
    flash('Logged out')
    return redirect('/login')

if __name__ == "__main__":
    app.run(debug=True)
