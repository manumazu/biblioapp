from flask import Flask, render_template, request, abort, flash, redirect, json, escape, session, url_for, jsonify, Response
from flask_bootstrap import Bootstrap
import flask_login, hashlib, base64, math, time
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from flask_session import Session

app = Flask(__name__)
app.config.from_object("config")
mail = Mail(app)
#Session(app)
sess = Session()
sess.init_app(app)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

bootstrap = Bootstrap(app)

from biblioapp import db, tools, models

global arduino_name, user_login

def initApp():
  user_login = False
  if(flask_login.current_user.is_authenticated):
    user_login = flask_login.current_user.name  
    #prevent empty session for module : select first one
    if 'app_id' not in session:
      modules = db.get_arduino_for_user(flask_login.current_user.id) 
      if modules:   
        for module in modules:
          session['app_id'] = module['id']
          session['app_name'] = module['arduino_name']
          flash('Bookshelf "{}"selected'.format(module['arduino_name']))
          break
    arduino_map = db.get_arduino_map(flask_login.current_user.id, session['app_id'])
    arduino_name = arduino_map['arduino_name']     
  else:
    arduino_map = None
    arduino_name = None  
  return {'user_login':user_login,'arduino_map':arduino_map,'arduino_name':arduino_name}

@app.route("/")
def presentation():
  userName = ""
  if flask_login.current_user.is_authenticated:
    userName=flask_login.current_user.name
  return render_template('index.html', user_login=userName)

@app.route("/modules", methods=['GET', 'POST'])
@flask_login.login_required
def selectArduino():
  modules = db.get_arduino_for_user(flask_login.current_user.id)
  if request.method == 'POST':
    if 'action' in request.form and request.form.get('action')=='select':
      session['app_id'] = request.form.get('module_id')
      session['app_name'] = request.form.get('module_name')
      if request.form.get('numshelf') and int(request.form.get('numshelf'))>0:
        session['app_numshelf'] = int(request.form.get('numshelf'))
      flash('Bookshelf "{}"selected'.format(request.form.get('module_name')))
      return redirect(url_for('myBookShelf', _scheme='https', _external=True))
  return render_template('modules.html', user_login=flask_login.current_user.name, modules=modules)

@app.route("/module/<app_id>", methods=['GET', 'POST'])
@flask_login.login_required
def editArduino(app_id):
  globalVars = initApp()
  module = globalVars['arduino_map']
  if module:
    session['app_id'] = module['id']
    session['app_name'] = module['arduino_name']
    if request.method == 'POST':
      if 'module_name' in request.form:
        if db.set_module(request.form):
          return redirect(url_for('editArduino', _scheme='https', _external=True, app_id=request.form.get('module_id')))
      if request.is_json:
        mode = request.args.get('mode')
        if mode == 'preview':
          db.clean_request(app_id) #clean request for preview
        data = request.get_json()
        for numrow in data:
          positions = data[numrow]
          for i in range(len(positions)):
            pos = i+1        
            if mode == 'save': 
              db.set_position(app_id, pos, pos, numrow, 1, 'static', positions[i])            
            if mode == 'preview': #set distant request for preview
              db.set_request(app_id, pos, numrow, pos, 1, positions[i], 'static', 'server', 'add')
            #suppr static when position is reseted to 0
            if int(positions[i]) == 0:
              db.del_item_position(int(app_id), pos, 'static', numrow)            
    return render_template('module.html', user_login=flask_login.current_user.name, module=module, db=db, shelf_infos=globalVars['arduino_map'])
  abort(404)

#get module infos from arduino for current arduino_name
@app.route('/module/<uuid>/')
def getModule(uuid):
  uuid = tools.uuid_decode(uuid)
  if uuid:
    user_app = db.get_app_for_uuid(uuid)
    user = db.get_user_for_uuid(uuid)
    if(user_app):
      data = {}
      data = user_app
      data['total_leds'] = user_app['nb_lines']*user_app['nb_cols']
      data['token'] = models.get_token('guest',user['email'])
      response = app.response_class(
            response=json.dumps(data),
            mimetype='application/json'
      )
      return response
  abort(404)  


@app.route("/adminmodule/", defaults={'app_id': None}, methods=['GET', 'POST'])
@app.route("/adminmodule/<app_id>/", methods=['GET', 'POST'])
@flask_login.login_required
def newArduino(app_id = None):
  globalVars = initApp()
  if flask_login.current_user.id == 'emmanuel.mazurier@gmail.com':
    if app_id is not None:
      module = db.get_module(app_id)
    else:
      module = {}
    user_id = globalVars['arduino_map']['user_id']
    if request.method == 'POST':
      #print(request.form)
      data = {}
      data['action'] = request.form.get('action')
      data['module_name'] = request.form.get('module_name')
      data['nb_lines'] = request.form.get('nb_lines')
      data['strip_length'] = request.form.get('striplength')
      ledspermeter = request.form.get('ledspermeter')
      leds_interval = (100/int(ledspermeter)) 
      nb_cols = round((float(data['strip_length'])/leds_interval)+0.5) # nb_leds per strip
      data['leds_interval'] = math.floor(leds_interval*100)/100 # interval btw leds in mm
      data['nb_cols'] = nb_cols
      #don't erease current BLE gatt 
      if request.form.get('module_id'):
        data['module_id'] = request.form.get('module_id')
        data['id_ble'] = module['id_ble']
      else:
        data['id_ble'] = "xxxx" #set empty id_ble
      #save module, set user_app, and set id_ble
      module = db.set_module(data)
      if 'id' in module:
          module = db.get_module(module['id'])
          db.set_user_app(module['id_user'], module['id'])
          if module['id_ble']=='xxxx':
            id_ble = tools.set_id_ble(module)
            db.update_id_ble(module['id'], id_ble)
          return redirect(url_for('newArduino', _scheme='https', _external=True, app_id=module['id']))
    if request.args.get('module_id'):
      module = db.get_module(request.args.get('module_id'))
    return render_template('module_admin.html', user_login=flask_login.current_user.name, module=module, \
      shelf_infos=globalVars['arduino_map'])
  abort(404)

@app.route('/categories', methods=['GET'])
@flask_login.login_required
def listCategories():
  globalVars = initApp()
  #for mobile app
  if('uuid' in request.args):
    categories = db.get_categories_for_app(session['app_id'])
    data = {}
    data['list_title'] = session['app_name']
    token = models.get_token('guest',flask_login.current_user.id)
    if categories:
      for i in range(len(categories)):
        hasRequest = db.get_request_for_tag(session['app_id'], categories[i]['id'])
        categories[i]['url'] = url_for('locateBooksForTag',tag_id=categories[i]['id'])
        categories[i]['token'] = token
        categories[i]['hasRequest'] = hasRequest
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
      return ('', 204)
  #for web
  else:
    if globalVars['arduino_map'] != None:
      user_id = globalVars['arduino_map']['user_id']
      categories = db.get_categories_for_user(user_id)    
      return render_template('categories.html', user_login=globalVars['user_login'], categories=categories, \
      shelf_infos=globalVars['arduino_map'])
    abort(404)

@app.route("/app/")
@flask_login.login_required
def myBookShelf():
  globalVars = initApp()
  if globalVars['arduino_map'] != None:
    app_id = globalVars['arduino_map']['id']
    if 'app_numshelf' not in session:
      session['app_numshelf'] = 1
    shelfs = range(1,globalVars['arduino_map']['nb_lines']+1)
    elements = {}
    stats = {}
    statics = {}
    for shelf in shelfs:
      books = db.get_books_for_row(app_id, shelf) 
      statics[shelf] = db.get_static_positions(app_id, shelf)     
      if books:
        statBooks = db.stats_books(app_id, shelf)
        statPositions = db.stats_positions(app_id, shelf)
        positionRate = 0
        if statPositions['totpos'] != None:
          positionRate = round((statPositions['totpos']/globalVars['arduino_map']['nb_cols'])*100)
        stats[shelf] = {'nbbooks':statBooks['nbbooks'], 'positionRate':positionRate}        
        element = {}
        for row in books:     
          element[row['led_column']] = {'item_type':row['item_type'],'id':row['id'], \
      'title':row['title'], 'author':row['author'], 'position':row['position'], 'range':row['range'], \
      'borrowed':row['borrowed'], 'url':'/book/'+str(row['id'])}
          requested = db.get_request_for_position(app_id, row['position'], shelf) #get requested elements from server (mobile will be set via SSE)
          if requested:
            element[row['led_column']]['requested']=True
        if statics[shelf]:
          for static in statics[shelf]:
            element[static['led_column']] = {'item_type':static['item_type'],'id':None, 'position':static['position']}
        elements[shelf] = sorted(element.items())
    bookstorange = db.get_books_to_range(globalVars['arduino_map']['user_id']) #books without position
    return render_template('bookshelf.html',user_login=globalVars['user_login'], tidybooks=elements, \
        bookstorange=bookstorange, lines=shelfs, shelf_infos=globalVars['arduino_map'], \
        nb_lines=globalVars['arduino_map']['nb_lines'], max_cols=globalVars['arduino_map']['nb_cols'], \
        session=session, stats=stats, json_statics = statics)
  abort(404)

@app.route("/ajax_set_bookshelf/", methods=['GET'])
@flask_login.login_required
def ajaxSetShelf(): 
  globalVars = initApp()
  if request.method == 'GET' and request.args.get('rownum'):
    session['app_numshelf'] = int(request.args.get('rownum'))
  response = app.response_class(
      response=json.dumps(session['app_numshelf']),
      mimetype='application/json'
  )
  return response

@app.route("/ajax_positions_inline/", methods=['GET'])
@flask_login.login_required
def jsonBookshelf(): 
  globalVars = initApp()
  app_id = globalVars['arduino_map']['id']  
  if request.method == 'GET' and request.args.get('row'):
    numrow = request.args.get('row')
    books = db.get_books_for_row(app_id, numrow)
    element = {}    
    if books:
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
    #save order for bookshelf
    if 'row' in request.form :
      current_row = request.form['row'] 
      book_ids = request.form.getlist('book[]')
      sortable = db.sort_items(session.get('app_id'), globalVars['arduino_map']['user_id'], book_ids, current_row, \
        globalVars['arduino_map']['leds_interval'])
    #save order for customcodes
    if 'customcode' in request.form:
      code_ids = request.form.getlist('code[]')
      sortable = db.sort_customcodes(globalVars['arduino_map']['user_id'], session.get('app_id'), code_ids)
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
    #leds_range = request.form.get('range')
    #update book width
    book = db.get_book(book_id, globalVars['arduino_map']['user_id'])
    book_width = request.form.get('new_book_width')
    book['width'] = round(float(book_width))
    db.set_book(book, globalVars['arduino_map']['user_id'])
    leds_range = tools.led_range(book, globalVars['arduino_map']['leds_interval'])
    #update position
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
      book = elem.split('_') #vars book_[id]
      item_id = book[1]
      item_type = book[0]
      #clean all position for books
      position = db.get_position_for_book(session.get('app_id'), item_id)
      sortable = []
      if position:
        db.del_item_position(session.get('app_id'), item_id, item_type, position['row'])
        has_request = db.get_request_for_position(session.get('app_id'), position['position'], position['row'])
        #remove request
        if has_request:
          db.del_request(session.get('app_id'), position['led_column'], position['row'])
        #get list for remaining items and sort them again
        items = db.get_positions_for_row(session.get('app_id'), position['row'])
        if items:
          sortable = db.sort_items(session.get('app_id'), globalVars['arduino_map']['user_id'], items, position['row'], \
            globalVars['arduino_map']['leds_interval'])
  response = app.response_class(
        response=json.dumps(sortable),
        mimetype='application/json'
  )
  return response

@app.route('/tag/<tag_id>')
@flask_login.login_required
def listNodesForTag(tag_id):
  globalVars = initApp()
  if globalVars['arduino_map'] != None:
    nodes = db.get_node_for_tag(tag_id, globalVars['arduino_map']['user_id'])
    tag = db.get_tag_by_id(tag_id)
    data = {}
    data['list_title'] = tag['tag']
    client = 'server'
    if('token' in request.args):
      client = 'mobile'
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
                if tag['color'] is not None:
                  books[i]['color'] = tag['color']
        data['items'] = books
    #send json when token mode
    if('token' in request.args):
      response = app.response_class(
        response=json.dumps(data),
        mimetype='application/json'
      )
      return response     
    return render_template('tag.html', books=books, user_login=globalVars['user_login'], \
      shelf_infos=globalVars['arduino_map'], tag=tag)
  abort(404)

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
  if globalVars['arduino_map'] != None:
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
          shelf_infos=globalVars['arduino_map'], biblio_nb_rows=globalVars['arduino_map']['nb_lines'])
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
  if request.method == 'GET' and 'token' in request.args:
    app_id = session['app_id']
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
  positions = []

  '''get form request params'''
  if (request.method == 'POST'):
    client = 'server'
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
    client = 'mobile'
    app_id = session['app_id']
    book_id = request.args.get('book_id')
    color = request.args.get('color')
    address = db.get_position_for_book(app_id, book_id)    
    if 'remove_request' in request.args:
      action = 'remove'

  #store request
  if action == 'remove':
    retMsg = 'Location removed for book {}'.format(book_id)
  else: 
    retMsg = 'Location requested for book {}'.format(book_id)

  #manage request
  db.set_request(app_id, book_id, address['row'], address['position'], address['range'], address['led_column'], \
    'book', client, action)

  #send data for mobile
  if('token' in request.args):
    data = {'action':action, 'row':address['row'], 'start':address['led_column'], 'interval':address['range'], \
      'id_node':book_id, 'borrowed':address['borrowed']}
    if color != None :
      data.update({'color':color})
    positions.append(data) 
    response = app.response_class(
      response=json.dumps(positions),
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

  action = 'add'
  if('action' in request.args):#for add or remove
    action = request.args.get('action')

  client = 'server'
  if('token' in request.args):
    client = 'mobile'

  positions = []
  for node in nodes:
    address = db.get_position_for_book(session['app_id'], node['id_node'])
    if address:
      book = db.get_book(node['id_node'], globalVars['arduino_map']['user_id'])
    
      #manage request
      db.set_request(session['app_id'], node['id_node'], address['row'], address['position'], address['range'], \
        address['led_column'], 'book', client, action, tag_id, tag['color'])

      if tag['color'] is None:
        tag['color'] = ''

      positions.append({'item':book['title'], 'action':action, 'row':address['row'], 'led_column':address['led_column'], \
        'interval':address['range'], 'id_tag':tag_id, 'color':tag['color'], 'id_node':node['id_node'], 'client':client})

  '''get elements for block build'''
  positions.sort(key=tools.sortPositions)
  blocks = tools.build_block_position(positions, action)
  #print(blocks)

  #send json when token mode
  if('token' in request.args):
    response = app.response_class(
      response=json.dumps(blocks),
      mimetype='application/json'
    )
    return response
  for i, book in enumerate(positions):
    flash('Location requested for book {}'.format(book['item']))
  return redirect(url_for('listAuthors', _scheme='https', _external=True))

#get request from arduino for current arduino_name
@app.route('/request', methods=['GET'])
@flask_login.login_required
def getRequestForModule():
  globalVars = initApp()
  if globalVars['arduino_map'] != None:  

    #get request for distant mobile app
    #if('uuid' in request.args):
    source = 'server'
    if 'uuid' in request.args and 'token' in request.args:
      source = 'mobile'
      
    positions_add = []
    blocks = []
    datas_add = db.get_request(session['app_id'], 'add')
    if datas_add:      
      for data in datas_add:
        #send display request only for server (for mobile, leds are already displayed)
        if (source == 'mobile' and data['client']=='server') or (source == 'server'):
          positions_add.append({'action':data['action'], 'row':data['row'], 'led_column':data['led_column'], \
        'interval':data['range'], 'id_tag':data['id_tag'], 'color':data['color'], 'id_node':data['id_node'], \
        'client':data['client']})

      positions_add.sort(key=tools.sortPositions)
      blocks = tools.build_block_position(positions_add, 'add')

    positions_remove = []
    datas_remove = db.get_request(session['app_id'], 'remove')
    resp = "event: ping\n"
    if datas_remove:
      #soft remove   
      for data in datas_remove:
        if (source == 'mobile' and data['client']=='server') or (source == 'server'):
          positions_remove.append({'action':data['action'], 'row':data['row'], 'led_column':data['led_column'], \
        'interval':data['range'], 'id_tag':'', 'color':'', 'id_node':data['id_node'], 'client':data['client']})

      positions_remove.sort(key=tools.sortPositions)
      blocks += tools.build_block_position(positions_remove, 'remove')

      #hard remove 
      for data in datas_remove:
        diff = tools.seconds_between_now(data['date_add'])
        #wait for other clients before remove
        if diff > 3:
          db.del_request(session['app_id'], data['led_column'], data['row'])      
        
    #print(blocks)

    #set message for SSE
    resp = "event: ping\n"
    if len(blocks) > 0:        
      json_dump = json.dumps(blocks)
      resp += "data: "+json_dump
      resp += "\nid: "+hashlib.md5(json_dump.encode("utf-8")).hexdigest()
      resp += "\nretry: 2000"
    else:
      resp += "\ndata: {}"
      resp +="\nid: 0"
      resp += "\nretry: 5000"
    resp += "\n\n"
    return Response(resp, mimetype='text/event-stream')    
  #abort(404)

#remove all request from arduino for current module
@app.route('/reset', methods=['GET'])
@flask_login.login_required
def setResetForModule():
  globalVars = initApp()  
  if globalVars['arduino_map'] != None:
    data = db.clean_request(session['app_id'])#clean all module's request
    response = app.response_class(
          response=json.dumps(data),
          mimetype='application/json'
    )
    return response
  abort(404)


#get authors liste from arduino 
@app.route('/authors', methods=['GET'])
@flask_login.login_required
def listAuthors():
  globalVars = initApp()  
  if globalVars['arduino_map'] != None:
    #for mobile app 
    if('uuid' in request.args):
      data = {}
      token = models.get_token('guest',flask_login.current_user.id)
      data['list_title'] = session['app_name']
      data['elements']=[]
      alphabet = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]
      for j in range(len(alphabet)):
        '''data['elements'][j]={}
        data['elements'][j]['initial']=alphabet[j]'''
        #print(data)
        items = db.get_authors_for_app(session['app_id'], alphabet[j])
        if items:
          '''set url for authenticate requesting location from app'''
          for i in range(len(items)):
            items[i]['url'] = url_for('locateBooksForTag',tag_id=items[i]['id'])
            items[i]['token'] = token
            hasRequest = db.get_request_for_tag(session['app_id'], items[i]['id'])
            items[i]['hasRequest'] = hasRequest
          #data['elements'][j]['items'] = items
        data['elements'].append({'initial':alphabet[j],'items':items})
      response = app.response_class(
            response=json.dumps(data),
            mimetype='application/json'
      )
      return response
    #for web
    else:
      return render_template('authors.html', user_login=flask_login.current_user.name, db=db, \
          user_id=globalVars['arduino_map']['user_id'], \
        shelf_infos=globalVars['arduino_map'])    
  abort(404)    

@app.route('/booksearch/', methods=['GET', 'POST'])
@flask_login.login_required
def searchBookReference():
  import requests
  globalVars = initApp()
  if globalVars['arduino_map'] != None:
    data={}

    '''Search books with google api'''  
    url = "https://www.googleapis.com/books/v1/volumes"
    query = "?key=AIzaSyBVwKgWVqNaLwgceI_b3lSJJAGLw_uCDos&q="
    '''search on api for form'''
    if request.method == 'POST':
      if 'isbn' in request.form and request.form['isbn']:
        query += "ISBN:\""+request.form['isbn']+"\"&"
      if 'inauthor' in request.form and request.form['inauthor']:
        query += "inauthor:"+request.form['inauthor']+"+"
      if 'intitle' in request.form and request.form['intitle']:
        query += "intitle:"+request.form['intitle']
      if 'query' in request.form:
        query += request.form['query']
      r = requests.get(url + query)
      data = r.json()
      return render_template('booksearch.html', user_login=globalVars['user_login'], data=data, req=request.form, \
        shelf_infos=globalVars['arduino_map'])

    '''display classic form for edition'''
    if request.method == 'GET' and request.args.get('ref'):
      ref = request.args.get('ref')
      book = {}
      if ref != 'new':
        r = requests.get("https://www.googleapis.com/books/v1/volumes/"+ref)
        data = r.json()
        book = data['volumeInfo']    
      return render_template('booksearch.html', user_login=globalVars['user_login'], book=book, ref=ref, \
          shelf_infos=globalVars['arduino_map'])

    '''manage infos from mobile app'''
    if request.method == 'GET' and request.args.get('token') and request.args.get('isbn'):
      res = []
      '''Search books with googleapis api'''
      if request.args.get('search_api')=='googleapis':
        query += "ISBN:\""+request.args.get('isbn')+"\""
        print(url + query)
        r = requests.get(url + query)
        data = r.json() 
        if 'items' in data:
          for item in data['items']:
            res.append(tools.formatBookApi('googleapis', item, request.args.get('isbn')))

      '''Search books with openlibrary api'''
      if request.args.get('search_api')=='openlibrary':
        url = "https://openlibrary.org/api/books?format=json&jscmd=data&bibkeys="
        query = "ISBN:"+request.args.get('isbn')
        r = requests.get(url + query)
        data = r.json()
        #print(data)      
        if query in data:
          res = [tools.formatBookApi('openlibrary', data[query], request.args.get('isbn'))]  

      #print(res)
      response = app.response_class(
          response=json.dumps(res),
          mimetype='application/json'
      )
      return response           
    else:
      return render_template('booksearch.html', user_login=globalVars['user_login'], \
        shelf_infos=globalVars['arduino_map']) 
  abort(404)

@app.route('/bookreferencer/', methods=['POST', 'GET'])
@flask_login.login_required
def bookReferencer():
  globalVars = initApp()

  '''save classic data from form'''
  if request.method == 'POST':
    book = tools.formatBookApi('localform', request.form, request.form['isbn'])  
    if 'id' in request.form:
      book['id'] = request.form['id']
    bookSave(book, globalVars['arduino_map']['user_id'], request.form['tags'])
    return redirect(url_for('myBookShelf', _scheme='https', _external=True))
    #return render_template('bookreferencer.html', user_login=globalVars['user_login'])    

  '''save book from mobile app'''
  if request.method == 'GET' and request.args.get('token') and request.args.get('save_bookapi'):
    import requests
    ref = request.args.get('ref')
    isbn = request.args.get('isbn')
    source_api = request.args.get('save_bookapi')

    '''resume detail on api before saving'''
    if source_api=='googleapis':
      r = requests.get("https://www.googleapis.com/books/v1/volumes/"+ref)
      data = r.json()
      book = tools.formatBookApi('googleapis', data, isbn) 
    if source_api=='openlibrary':
      r = requests.get("https://openlibrary.org/api/volumes/brief/isbn/"+isbn+".json")
      data = r.json()
      book = tools.formatBookApi('openlibrary', data['records'][ref]['data'], isbn)

    book_width = request.args.get('book_width')
    book['width'] = round(float(book_width))
    #print(book)

    #save process
    bookId = db.get_bookapi(isbn, globalVars['arduino_map']['user_id'])
    message = {}  

    if bookId:
      message = {'result':'error', 'message':'This book is already in your shelfs'}
    #add new book
    else:
      bookId = bookSave(book, globalVars['arduino_map']['user_id'])
      #force position in current app
      forcePosition = request.args.get('forcePosition')
      if forcePosition == 'true':
        lastPos = db.get_last_saved_position(session.get('app_id'))
        newInterval = tools.led_range(book, globalVars['arduino_map']['leds_interval'])
        if lastPos:
          newPos = lastPos['position']+1
          newRow = lastPos['row']
          newLedNum = lastPos['led_column']+lastPos['range']
          #adjust new led column with static element
          statics = db.get_static_positions(session.get('app_id'),lastPos['row']) 
          if statics:         
            for static in statics:
             if int(newLedNum) == int(static['led_column']):
              newLedNum += static['range']
        else:
          newPos = 1
          newRow = 1
          newLedNum = 0        
        led_column = db.set_position(session.get('app_id'), bookId['id'], newPos, newRow, newInterval, 'book', newLedNum)
        address = db.get_position_for_book(session.get('app_id'), bookId['id'])
      #confirm message
      if bookId:
        message['result'] = 'success'
        message['message'] = 'Book added with id '+str(bookId['id'])
        if forcePosition == 'true' and newLedNum != None:
          message['message'] += ' at position n°' +str(newPos)+ ' and LED n° ' + str(int(newLedNum)+1) + ' in row n°'+str(newRow)
          message['address'] = [{'action':'add', 'row':address['row'], 'start':address['led_column'], 'interval':address['range'], \
      'id_node':bookId['id'], 'borrowed':address['borrowed']}]
      else:
        message = {'result':'error', 'message':'Error saving book'}

    response = app.response_class(
      response=json.dumps(message),
      mimetype='application/json'
    )
    return response

def bookSave(book, user_id, tags = None):
  bookId = db.set_book(book, user_id)
  #manage tags + taxonomy
  #author tags
  authorTags = tools.getLastnameFirstname(book['authors'])
  authorTagids = db.set_tags(authorTags,'Authors')
  if len(authorTagids)>0:
    db.set_tag_node(bookId, authorTagids)
  #categories
  if tags is not None :  
    db.clean_tag_for_node(bookId['id'], 1) #clean tags categories  before update
    catTagIds = db.set_tags(tags.split(','),'Categories')
    if len(catTagIds)>0:
      db.set_tag_node(bookId, catTagIds)
  return bookId


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


@app.route('/customcodes', methods=['GET', 'POST'])
@flask_login.login_required
def customCodes():
  globalVars = initApp()
  if globalVars['arduino_map'] != None:
    #print(codes)
    #send json when token mode
    if('token' in request.args):
      codes = db.get_customcodes(globalVars['arduino_map']['user_id'], session['app_id'], True)
      data = {}
      data['list_title'] = 'Your codes for ' + session['app_name']
      token = models.get_token('guest',flask_login.current_user.id)
      for i in range(len(codes)):
        codes[i]['url'] = url_for('customCode',code_id=codes[i]['id'])
        codes[i]['token'] = token
      data['elements']= codes
      response = app.response_class(
        response=json.dumps(data),
        mimetype='application/json'
      )
      return response  
    if request.args.get('saved'):
      flash('Your code is saved')  
    #manage post data from json request
    if request.method == 'POST':
      if request.is_json:
          jsonr = request.get_json()
          #print(json)
          db.set_customcode(globalVars['arduino_map']['user_id'], session['app_id'], None, jsonr['title'], jsonr['description'], \
            jsonr['published'], json.dumps(jsonr['customvars']), jsonr['customcode'])
          #print(request.data.decode())
    codes = db.get_customcodes(globalVars['arduino_map']['user_id'], session['app_id'])
    maxLeds = globalVars['arduino_map']['nb_cols']*globalVars['arduino_map']['nb_lines']      
    return render_template('customcodes.html', user_login=globalVars['user_login'], customcodes=codes, json=json, \
      max_leds=maxLeds, shelf_infos=globalVars['arduino_map'])
  abort(404)

@app.route('/customcode/<code_id>', methods=['GET', 'POST'])
@flask_login.login_required
def customCode(code_id):
  globalVars = initApp()
  if globalVars['arduino_map'] != None:
    #manage post data from json request
    if request.method == 'POST':
      if request.is_json:
          jsonr = request.get_json()
          db.set_customcode(globalVars['arduino_map']['user_id'], session['app_id'], code_id, jsonr['title'], jsonr['description'], \
           jsonr['published'], json.dumps(jsonr['customvars']), jsonr['customcode'])

    data = db.get_customcode(globalVars['arduino_map']['user_id'], session['app_id'], code_id)
    customvars = ''
    if data and len(data['customvars'])>0:
      customvars = json.loads(data['customvars'])
      #send json when token mode
      if('token' in request.args):
        response = app.response_class(
          response=json.dumps(data['customcode'].decode()),
          mimetype='application/json'
        )
        return response
      maxLeds = globalVars['arduino_map']['nb_cols']*globalVars['arduino_map']['nb_lines']
      return render_template('customcode.html', user_login=globalVars['user_login'], customcode=data['customcode'].decode(), \
        customvars=customvars, data=data, max_leds=maxLeds, effects=tools.get_leds_effects(), \
        shelf_infos=globalVars['arduino_map'])
  abort(404)

@app.route('/customcodedelete/', methods=['POST'])
@flask_login.login_required
def customCodeDelete():
  globalVars = initApp()
  code_id = request.form['id']
  customcode = db.get_customcode(globalVars['arduino_map']['user_id'], session['app_id'], code_id)
  if customcode: 
    db.del_customcode(code_id, globalVars['arduino_map']['user_id'])
    flash('Code "{}" is deleted'.format(customcode['title']))
    return redirect(url_for('customCodes', _scheme='https', _external=True))  

@app.route('/ajax_customcodetemplate/<template>')
@flask_login.login_required
def customCodeTemplate(template):
  globalVars = initApp()
  if template=='timer':
    return render_template('_customcode_timer.html')
  if template=='sample':
    return render_template('_customcode_sample.html')
  if template=='wait':
    return render_template('_customcode_wait.html') 
  if template=='effect':
    effects = tools.get_leds_effects()
    return render_template('_customcode_effect.html', effects=effects)        
  abort(404)

@app.route('/customeffects')
@flask_login.login_required
def customEffects():
  globalVars = initApp()
  if globalVars['arduino_map'] != None:
    if('token' in request.args):
      effects = tools.get_leds_effects()
      data = {}
      data['list_title'] = 'Effects for ' + session['app_name']
      token = models.get_token('guest',flask_login.current_user.id)
      data['elements']= effects
      response = app.response_class(
        response=json.dumps(data),
        mimetype='application/json'
      )
      return response
  abort(404) 

@app.route('/ajax_search/')
@flask_login.login_required
def ajaxSearch():
  globalVars = initApp()
  results = db.search_book(session['app_id'], request.args.get('term'))
  term = request.args.get('term')
  data = {}
  if len(term) > 2:
    #search for mobile app
    if request.method == 'GET' and request.args.get('token'):
      books = []    
      if results:
          #for node in nodes:
          for i in range(len(results)):
              book = db.get_book(results[i]['id'], globalVars['arduino_map']['user_id'])
              books.append(book)
              app_modules = db.get_arduino_for_user(flask_login.current_user.id)
              for module in app_modules:
                address = db.get_position_for_book(module['id'], book['id'])
                if address:
                  books[i]['address'] = address
          data['list_title'] = str(len(results)) 
          data['list_title'] += " books " if len(results) > 1 else " book "
          data['list_title'] += "for \""+request.args.get('term')+"\""
      else:
        data['list_title'] = "No result for \""+request.args.get('term')+"\""
      data['items'] = books
    #autcomplete for book permutation
    else:
      data = []
      if results:
        for result in results:
          data.append({'id':result['id'], 'label':result['author']+' - '+result['title'], \
            'value':result['title']})

  response = app.response_class(
    response=json.dumps(data),
    mimetype='application/json'
  )
  return response  

@app.route('/ajax_permute_position/')
@flask_login.login_required
def ajaxPermutePosition():
  globalVars = initApp()
  from_id = request.args.get('from_id')
  dest_id = request.args.get('dest_id')
  pos_from = db.get_position_for_book(session['app_id'], from_id)
  pos_dest = db.get_position_for_book(session['app_id'], dest_id)
  #test interval equality before permutation
  if pos_from['range'] != pos_dest['range']:
    message = {'success':False, 'dest_range':pos_dest['range']}
  else:
    #clean old positions
    db.del_item_position(session.get('app_id'), from_id, 'book', pos_from['row'])
    db.del_item_position(session.get('app_id'), dest_id, 'book', pos_dest['row'])
    #add new position for first book 
    led_column_1 = db.set_position(session.get('app_id'), from_id, pos_dest['position'], pos_dest['row'], \
      pos_dest['range'], 'book', pos_dest['led_column'])
    #add new position for destination book 
    led_column_2 = db.set_position(session.get('app_id'), dest_id, pos_from['position'], pos_from['row'], \
      pos_from['range'], 'book', pos_from['led_column'])
    message = {'success':True, from_id:led_column_1, dest_id:led_column_2}

  response = app.response_class(
    response=json.dumps(message),
    mimetype='application/json'
  )
  return response

'''
Reset Password
'''
@app.route("/forgot_password", methods=['GET', 'POST'])
def forgotPassword():
  hasRequest = False
  if flask_login.current_user.is_authenticated:
    return redirect(url_for('selectArduino', _scheme='https', _external=True))
  if request.method == 'POST':
    hasRequest = True
    email=request.form.get('uemail')
    exist = db.get_user(email)
    if exist != None:
      token = models.get_token('auth',exist['email'])
      msg = Message('[Biblioapp] Reset Your Password', recipients = [exist['email']])
      msg.body=render_template('email/reset_password.txt', user=exist, token=token)
      msg.html=render_template('email/reset_password.html',user=exist, token=token)
      mail.send(msg)
      #return "Sent"  
  return render_template('forgot_password.html', hasRequest=hasRequest)

@app.route("/reset_password", methods=['GET', 'POST'])
def resetPassword():
  #verify token and display form
  if 'token' in request.args:
    token = request.args.get('token')
    #token was verified by request_loader
    if flask_login.current_user.is_authenticated:
      email = flask_login.current_user.id
    else:
      abort(403)
  if request.method == 'POST':
    password = request.form.get('upassword')
    cpassword = request.form.get('cpassword')
    token = request.args.get('token')
    if password == cpassword and email != None:
      hashed = generate_password_hash(password)
      db.set_user_pwd(email, hashed)
      flash('Your password has been reset.')
      return redirect(url_for('login', _scheme='https', _external=True))
    else:
      flash('Password confirm is different.')
      return redirect(url_for('resetPassword', _scheme='https', _external=True, token=token))
  return render_template('reset_password.html', token=token)      

'''
Authentication
'''
@app.route('/signup', methods=['GET', 'POST'])
def signUp():
  if request.method == 'POST':
    firstname=request.form.get('ufirstname')
    lastname=request.form.get('ulastname')
    email=request.form.get('uemail')
    password=request.form.get('upassword')
    #manage save errors, check if email already exists
    message={'success':False}
    exist = db.get_user(email)
    if exist is not None:
      message = {'success':False, 'field':'uemail', 'message':'Email already exists'}
    else:
      #hash pwd and save user 
      hashed = generate_password_hash(password)
      test = db.set_user(email, firstname, lastname, hashed)
      if test is not None:
        message = {'success':True, 'redirect':url_for('login')}
    response = app.response_class(
      response=json.dumps(message),
      mimetype='application/json'
    )
    return response
  return render_template('signup.html')

@app.route('/ajax_recaptcha/', methods=['GET', 'POST'])
def verifRecaptcha():
  import requests
  recaptcha_response = request.form.get('token')
  secretKey = "6Lc6WKMZAAAAAP-S1aHiuQzM_K3T8PGH5rMC_XZh"
  r = requests.post("https://www.google.com/recaptcha/api/siteverify?secret="+secretKey+"&response="+recaptcha_response)
  data = r.json()
  if 'success' in data:
    if data['score'] >= 0.5: 
      return "ok"
  return "ko"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
      if request.args.get('saved'):
        flash('Congratulation, your account is saved! You can login now')  
      return render_template('login.html')

    email = request.form['email']
    exists = db.get_user(email)
    if exists is not None:
      #hash = generate_password_hash(exists['password'])
      if check_password_hash(exists['password'],request.form['password']):

        user = models.User()
        user.id = email
        user.name = exists['firstname'] 
        flask_login.login_user(user)
        return redirect(url_for('selectArduino', _scheme='https', _external=True))

    return 'Bad login'

@app.route('/logout')
def logout():
    session.clear()
    flask_login.logout_user()
    flash('Logged out')
    return redirect(url_for('login', _scheme='https', _external=True))

if __name__ == "__main__":
    app.run(debug=True)
