from flask import Flask, render_template, request, abort, flash, redirect, json, escape, session, url_for, jsonify, \
Response, send_from_directory
import flask_login, hashlib, os
from PIL import Image
from werkzeug.utils import secure_filename

'''
Manage bookshelf, books, tags, search in shelves
'''
def set_routes_for_books(app):

  from biblioapp import db, models, tools

  @app.route("/api/bookshelf")
  @app.route("/app/")
  @flask_login.login_required
  def myBookShelf():
    globalVars = tools.initApp()
    apiCall = False

    if globalVars['arduino_map'] != None:
      app_id = globalVars['arduino_map']['id']

      if 'api' in request.path and 'uuid' in request.args:
        apiCall = True

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

      #return Json for API
      if apiCall:
        results = {'shelfInfos': globalVars['arduino_map'], 'storedBooks':elements, 'statsBooks':stats}
        response = app.response_class(
          response=json.dumps(results),
          mimetype='application/json'
        )
        return response

      #return html    
      return render_template('bookshelf.html',user_login=globalVars['user_login'], tidybooks=elements, \
          bookstorange=bookstorange, lines=shelfs, shelf_infos=globalVars['arduino_map'], \
          nb_lines=globalVars['arduino_map']['nb_lines'], max_cols=globalVars['arduino_map']['nb_cols'], \
          session=session, stats=stats, json_statics = statics)
    abort(404)

  @app.route("/ajax_set_bookshelf/", methods=['GET'])
  @flask_login.login_required
  def ajaxSetShelf(): 
    globalVars = tools.initApp()
    if request.method == 'GET' and request.args.get('rownum'):
      session['app_numshelf'] = int(request.args.get('rownum'))
    response = app.response_class(
        response=json.dumps(session['app_numshelf']),
        mimetype='application/json'
    )
    return response


  @app.route('/categories', methods=['GET'])
  @app.route('/api/categories', methods=['GET'])
  @flask_login.login_required
  def listCategories():
    globalVars = tools.initApp()
    #for mobile app
    if('api' in request.path and 'uuid' in request.args):
      categories = db.get_categories_for_app(globalVars['arduino_map']['user_id'], session['app_id'])
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
        shelf_infos=globalVars['arduino_map'], uuid_encode=tools.uuid_encode(globalVars['arduino_map']['id_ble']))
      abort(404)

  @app.route('/ajax_categories/')
  @flask_login.login_required
  def ajaxCategories():
    globalVars = tools.initApp()
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

  @app.route('/tag/<tag_id>')
  @app.route('/api/tag/<tag_id>')
  @flask_login.login_required
  def listNodesForTag(tag_id):
    globalVars = tools.initApp()
    if globalVars['arduino_map'] != None:
      nodes = db.get_node_for_tag(tag_id, session.get('app_id'))
      tag = db.get_tag_by_id(tag_id, globalVars['arduino_map']['user_id'])   
      data = {}
      books = []
      data['list_title'] = tag['tag']
      client = 'server'
      if('token' in request.args):
        client = 'mobile'
      if nodes:
          #for node in nodes:
          for i in range(len(nodes)):
              book = db.get_book(nodes[i]['id_node'], session.get('app_id'), globalVars['arduino_map']['user_id'])
              books.append(book)
              app_modules = db.get_arduino_for_user(flask_login.current_user.id)
              for module in app_modules:
                address = db.get_position_for_book(module['id'], book['id'])
                if address:
                  hasRequest = db.get_request_for_position(module['id'], address['position'], address['row'])
                  books[i]['address'] = address
                  books[i]['arduino_name'] = module['arduino_name']
                  books[i]['uuid_encode'] = tools.uuid_encode(module['id_ble'])
                  books[i]['app_id'] = module['id']
                  books[i]['app_uuid'] = module['uuid']
                  books[i]['app_mac'] = module['mac']
                  books[i]['hasRequest'] = hasRequest
                  if tag['color'] is not None:
                    books[i]['color'] = tag['color']
          data['items'] = books
      #send json when token mode
      if('api' in request.path and 'token' in request.args):
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
    globalVars = tools.initApp()
    if globalVars['arduino_map'] != None:  
      if request.method == 'POST':
        red = request.form['red'] 
        green = request.form['green'] 
        blue = request.form['blue']
        color = red+','+green+','+blue
        result = False
        if db.set_color_for_tag(globalVars['arduino_map']['user_id'], tag_id, color):
          result = True
        response = app.response_class(
          response=json.dumps(result),
          mimetype='application/json'
        )
        return response

  # get book info from shelf list
  @app.route('/book/<book_id>')
  @app.route('/api/book/<book_id>')
  @flask_login.login_required
  def getBook(book_id):
    globalVars = tools.initApp()
    if globalVars['arduino_map'] != None:
      book = db.get_book(book_id, session.get('app_id'), globalVars['arduino_map']['user_id'])
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
        if('api' in request.path and 'token' in request.args):
          response = app.response_class(
            response=json.dumps(book),
            mimetype='application/json'
          )
          return response      
        return render_template('book.html', user_login=globalVars['user_login'], book=book, \
            shelf_infos=globalVars['arduino_map'], biblio_nb_rows=globalVars['arduino_map']['nb_lines'])
    abort(404)  

  #get list of borrowed books
  @app.route('/borrowed')
  @app.route('/api/borrowed')
  @flask_login.login_required
  def borrowedBooks():
    globalVars = tools.initApp()
    if globalVars['arduino_map'] != None:
      addresses = db.get_borrowed_books(session.get('app_id'))
      data = {}
      data['list_title'] = "Borrowed books"
      books = []
      if addresses:
          #for address in addresses:
          for i in range(len(addresses)):
            book = db.get_book(addresses[i]['id_item'], session.get('app_id'), globalVars['arduino_map']['user_id'])
            books.append(book)
            hasRequest = db.get_request_for_position(session.get('app_id'), addresses[i]['position'], addresses[i]['row'])
            books[i]['address'] = addresses[i]
            books[i]['hasRequest'] = hasRequest
            books[i]['arduino_name'] = globalVars['arduino_map']['arduino_name']
            books[i]['app_id'] = session.get('app_id')     
            books[i]['color'] = '255,0,0'
      data['items'] = books
      #send json when token mode
      if('api' in request.path and 'token' in request.args):
        response = app.response_class(
          response=json.dumps(data),
          mimetype='application/json'
        )
        return response     
      return render_template('borrowed.html', books=books, user_login=globalVars['user_login'], \
        shelf_infos=globalVars['arduino_map'])
    abort(404)

  #post request from app
  @app.route('/borrow/', methods=['GET'])
  @app.route('/api/borrow/', methods=['GET'])
  @flask_login.login_required
  def borrowBook():
    globalVars = tools.initApp()
    ret = []
    if('api' in request.path and 'token' in request.args):
      app_id = session['app_id']
      book_id = request.args.get('book_id')
      action = request.args.get('action')
      db.set_borrow_book(app_id, book_id, action)
      address = db.get_position_for_book(app_id, book_id)
      ret.append({'item':book_id,'action':'borrow','address':address}) 
      response = app.response_class(
        response=json.dumps(ret),
        mimetype='application/json'
      )
      return response    



  #get authors liste from arduino 
  @app.route('/authors', methods=['GET'])
  @app.route('/api/authors', methods=['GET'])
  @flask_login.login_required
  def listAuthors():
    globalVars = tools.initApp()  
    if globalVars['arduino_map'] != None:
      #for mobile app 
      if('api' in request.path and 'uuid' in request.args):
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
            user_id=globalVars['arduino_map']['user_id'], shelf_infos=globalVars['arduino_map'], 
            uuid_encode=tools.uuid_encode(globalVars['arduino_map']['id_ble'])) 
    abort(404)    

  @app.route('/booksearch/', methods=['GET', 'POST'])
  @app.route('/api/booksearch/', methods=['GET', 'POST'])
  @flask_login.login_required
  async def searchBookReference():

    globalVars = tools.initApp()
    if globalVars['arduino_map'] != None:   
      # search on api for form
      query = ""
      if request.method == 'POST':
        if 'isbn' in request.form and request.form['isbn']:
          query += "ISBN:\""+request.form['isbn']+"\"&"
        if 'inauthor' in request.form and request.form['inauthor']:
          query += "inauthor:"+request.form['inauthor']+"+"
        if 'intitle' in request.form and request.form['intitle']:
          query += "intitle:"+request.form['intitle']
        if 'query' in request.form:
          query += request.form['query']
        #for bibliocli request
        if request.is_json and 'title' in request.json:
          query += "intitle:"+request.json['title']
        
        data = tools.searchBookApi(query, 'googleapis')
        #print(data)

        #set response for api
        if 'api' in request.path and request.is_json:
          res = []          
          if 'items' in data:
            for item in data['items']:
              book = tools.formatBookApi('googleapis', item, None, True)
              #print(book)
              res.append(book)
          response = app.response_class(
              response=json.dumps(res),
              mimetype='application/json'
          )
          #print(res)
          # return first result only for ocr search html render, for other case return json array
          if 'search_origin' in request.json and request.json['search_origin'] == 'ocr':
            book = res[0] if len(res) > 0 else None 
            return render_template('_book_search_result.html', book=book, numbook=request.json['numbook'], search=request.json['title'], numshelf=request.json['numshelf'], img_num=request.json['img_num'])
          else:
            return response
        return render_template('booksearch.html', user_login=globalVars['user_login'], data=data, req=request.form, \
          shelf_infos=globalVars['arduino_map'], tools=tools)

      '''display classic form for edition'''
      if request.method == 'GET' and request.args.get('ref'):
        ref = request.args.get('ref')
        # get book reference informations
        book = {}
        if ref != 'new':
          data = tools.searchBookApi(None, 'googleapis', ref)
          book = tools.formatBookApi('googleapis', data, None, True)
          #print(book)
          if 'imageLinks' in data['volumeInfo']:
            book['imageLinks'] = data['volumeInfo']['imageLinks']
          if 'categories' in data['volumeInfo']:
            book['categories'] = data['volumeInfo']['categories']  
        return render_template('booksearch.html', user_login=globalVars['user_login'], book=book, ref=ref, \
            shelf_infos=globalVars['arduino_map'])

      '''manage infos from mobile app'''
      if 'api' in request.path and request.args.get('token') and request.args.get('isbn'):
        res = []
        '''Search books with googleapis api'''
        if request.args.get('search_api')=='googleapis':
          query = "ISBN:\""+request.args.get('isbn')+"\""
          data = tools.searchBookApi(query, 'googleapis')
          #print(data)
          if 'items' in data:
            for item in data['items']:
              res.append(tools.formatBookApi('googleapis', item, request.args.get('isbn'), True))

        '''Search books with openlibrary api'''
        if request.args.get('search_api')=='openlibrary':
          query = "ISBN:"+request.args.get('isbn')
          data = tools.searchBookApi(query, 'openlibrary')
          #print(data)      
          if query in data:
            res = [tools.formatBookApi('openlibrary', data[query], request.args.get('isbn'), True)]  

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
  @app.route('/api/bookreferencer/', methods=['POST', 'GET'])
  @flask_login.login_required
  def bookReferencer():
    globalVars = tools.initApp()
    '''save classic data from form'''
    if request.method == 'POST':
      book = tools.formatBookApi('localform', request.form, request.form['isbn'], False) 
      if 'id' in request.form:
        book['id'] = request.form['id']
      tags = request.form['tags'] if 'tags' in request.form else None
      db.bookSave(book, globalVars['arduino_map']['user_id'], session.get('app_id'), tags)
      return redirect(url_for('myBookShelf', _scheme='https', _external=True))
      
    '''save book from mobile app or ocr search '''
    if 'api' in request.path and request.args.get('token') and request.args.get('save_bookapi'):
      ref = request.args.get('ref')
      isbn = request.args.get('isbn')
      source_api = request.args.get('save_bookapi')
      numshelf = int(request.args.get('numshelf'))
      forcePosition = request.args.get('forcePosition')
      bookId = False
      if 'id_book' in request.args:
        bookId = request.args.get('id_book')
      message = {}

      # when id_book is sent, retrieve book info in bdd
      if bookId:
        book = db.get_book(bookId, session.get('app_id'), globalVars['arduino_map']['user_id'])
        bookId = {}
        bookId['id'] = book['id']
        #app.logger.info('book exists %s', book)
      # use apis to get book info before saving it
      else:
        # resume detail on api before saving book
        if source_api=='googleapis':
          data = tools.searchBookApi(None, 'googleapis', ref)
          book = tools.formatBookApi('googleapis', data, isbn, True) 
        if source_api=='openlibrary':
          import requests
          r = requests.get("https://openlibrary.org/api/volumes/brief/isbn/"+isbn+".json")
          data = r.json()
          book = tools.formatBookApi('openlibrary', data['records'][ref]['data'], isbn, True)
        if 'book_width' in request.args:
          book_width = request.args.get('book_width')
          book['width'] = round(float(book_width))
        # force width if not found or not set
        elif 'width' not in book:
          book['width'] = round(tools.set_book_width(book['pages']))

        #save process
        bookId = db.get_bookapi(isbn, ref, globalVars['arduino_map']['user_id'])
        if bookId and forcePosition == 'false':
          message = {'result':'error', 'message':'This book is already in your shelfs'}
        #add new book
        else:
          bookId = db.bookSave(book, globalVars['arduino_map']['user_id'], session.get('app_id'), None)
        book['id'] = bookId['id']
        
      #force position in current app
      if forcePosition == 'true':
        # force new position 
        address = db.force_new_position(session.get('app_id'), book, numshelf, globalVars)
        
      #confirm message
      if bookId:
        message['result'] = 'success'
        message['message'] = 'Book added with id '+str(bookId['id'])
        message['book'] = {'id_book':bookId['id']}
        if forcePosition == 'true' and address:
          message['message'] += ' at position n°' +str(address['position'])+ ' and LED n° ' + str(int(address['led_column'])+1) + ' in row n°'+str(address['row'])
          message['address'] = [{'action':'add', 'row':address['row'], 'start':address['led_column'], 'interval':address['range'], \
          'id_node':bookId['id'], 'borrowed':address['borrowed']}]
      else:
        message = {'result':'error', 'message':'Error saving book'}

      response = app.response_class(
        response=json.dumps(message),
        mimetype='application/json'
      )
      return response

  @app.route('/bookdelete/', methods=['POST'])
  @flask_login.login_required
  def bookDelete():
    globalVars = tools.initApp()
    book_id = request.form['id']
    book = db.get_book_not_ranged(book_id, globalVars['arduino_map']['user_id'])
    if book: 
      db.clean_tag_for_node(book_id, 1)#clean tags for categories
      db.clean_tag_for_node(book_id, 2)#clean tags for authors
      db.del_book(book_id, globalVars['arduino_map']['user_id'])
      flash('Book "{}" is deleted'.format(book['title']), 'warning')
      return redirect(url_for('myBookShelf', _scheme='https', _external=True))

  @app.route('/ajax_search/')
  @app.route('/api/ajax_search/')
  @flask_login.login_required
  def ajaxSearch():
    globalVars = tools.initApp()
    term = request.args.get('term')
    data = {}
    if len(term) > 2:
      results = db.search_book(session['app_id'], term)
      #search for mobile app
      if request.method == 'GET' and request.args.get('token'):
        books = []   
        #when results
        if results:

          #search for tag
          tag_id = None
          tag_color = None        
          tag = db.get_tag(term)
          if tag:
            tag_id = tag['id']
            tag_color = tag['color']

          for i in range(len(results)):
            book = db.get_book(results[i]['id'], session.get('app_id'), globalVars['arduino_map']['user_id'])
            books.append(book)
            app_modules = db.get_arduino_for_user(flask_login.current_user.id)
            for module in app_modules:
              address = db.get_position_for_book(module['id'], book['id'])
              if address:
                books[i]['address'] = address
                books[i]['hasRequest'] = False
                #for display mode, force set request 
                if 'display' in request.args and int(request.args.get('display'))==1:
                  db.set_request(session['app_id'], book['id'], address['row'], address['position'], \
                    address['range'], address['led_column'], 'book', 'server', 'add', tag_id, tag_color)
                  books[i]['hasRequest'] = True

            data['list_title'] = str(len(results)) 
            data['list_title'] += " books " if len(results) > 1 else " book "
            data['list_title'] += "for \""+request.args.get('term')+"\""
        #no result
        else:
          data['list_title'] = "No result for \""+request.args.get('term')+"\""
        data['items'] = books

      #autcomplete for book permutation for server
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

  #upload users's  bookshelves pictures and start OCR with IA on it
  @app.route('/bookindexer', methods=['GET', 'POST'])
  @flask_login.login_required
  def bookIndexerAI():
    globalVars = tools.initApp()
    #print(globalVars)
    
    if request.method == 'GET':

        # display uploaded pictures for current bookshelf and shelf number
        if 'numshelf' in request.args: 
          numshelf = request.args.get('numshelf')
          upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'users', str(globalVars['arduino_map']['user_id']), str(session.get('app_id')), numshelf, 'resize')
          full_path_dir = os.path.join(app.root_path, upload_dir)
          #get uploaded image list
          if os.path.isdir(full_path_dir) is False:
            os.makedirs(full_path_dir)
          img_list = os.listdir(full_path_dir)
          img_list = sorted(img_list)
          dir_list = []
          for img in img_list:
            relative_img_path = os.path.join(upload_dir, img)
            dir_list.append({"path":relative_img_path, "filename":img, "modal":img.split('.')[0]})
            #print(dir_list)   
          rendered = render_template('upload_bookshelf_render.html', img_paths = dir_list, numshelf = numshelf, module_name=globalVars['arduino_map']['arduino_name'], user_login=globalVars['user_login'], shelf_infos=globalVars['arduino_map'])
          return rendered
      
        # dislay upload form
        else:
          return render_template('upload_bookshelf.html', nb_lines=globalVars['arduino_map']['nb_lines'], user_login=globalVars['user_login'], shelf_infos=globalVars['arduino_map'])
    
    # manage post pictures + resize
    if request.method == 'POST':

        # delete existing image 
        if 'delete' in  request.form and 'numshelf' in request.form and 'filename' in request.form:
          filename = secure_filename(request.form['filename'])
          numshelf = str(request.form['numshelf'])
          upload_dir = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], 'users', \
            str(globalVars['arduino_map']['user_id']), str(session.get('app_id')), numshelf)
          delete_path = os.path.join(upload_dir, filename)
          delete_path_resize = os.path.join(upload_dir, 'resize', filename)
          if os.path.exists(delete_path) and os.path.exists(delete_path_resize):
            os.remove(delete_path)
            os.remove(delete_path_resize)
            output = {'success': True, 'response':filename+' deleted'}
          else:
            output = {'success': False, 'response':filename+' not exists'}
          app.logger.info('delete: %s', output)
          # display result
          response = app.response_class(
            response=json.dumps(output),
            mimetype='application/json'
          )
          return response
        
        # upload new image for given numshelf
        if 'shelf_img' not in request.files:
            flash('Veuillez sélectionner un dossier')
            return redirect(url_for('bookIndexerAI', _scheme='https', _external=True))
        shelf_img = request.files['shelf_img']
        if shelf_img.filename == '':
            flash('Aucun fichier sélectionné', 'warning')
            return redirect(url_for('bookIndexerAI', _scheme='https', _external=True))
        if tools.allowed_file(shelf_img.filename) is False:
          flash('Format de fichier non autorisé', 'warning')
          return redirect(url_for('bookIndexerAI', _scheme='https', _external=True))
        if shelf_img and 'numshelf' in request.form:
            filename = secure_filename(shelf_img.filename)
            numshelf = str(request.form['numshelf'])
            upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'users', str(globalVars['arduino_map']['user_id']), str(session.get('app_id')), numshelf)
            #create user dir if not exists
            user_dir = os.path.join(app.root_path, upload_dir)
            if not os.path.exists(user_dir):
              os.makedirs(user_dir)
            
            #order file list
            count_img = os.listdir(user_dir)
            nb_img = len(count_img)
            if nb_img == 0:
              nb_img = 1
            filename = str(nb_img) + '_' + filename
            
            #save image 
            full_path_img = os.path.join(user_dir, filename)
            shelf_img.save(full_path_img)
            
            #resize image
            img = Image.open(full_path_img)
            width, height = img.size
            ratio = width/height
            img_resized = img.resize((2000,int(2000/ratio))) if(ratio > 1) else img.resize((1500,int(1500/ratio)))
            resize_dir = os.path.join(user_dir, 'resize')
            if not os.path.exists(resize_dir):
              os.makedirs(resize_dir)
            img_resized_path = os.path.join(resize_dir, filename)
            img_resized.save(img_resized_path)
            
            return redirect(url_for('bookIndexerAI', numshelf=numshelf, _scheme='https', _external=True))

  #used for ocr indexation
  @app.route('/api/ajax_ocr/', methods=['POST'])
  @flask_login.login_required
  async def ajaxOcr():
    globalVars = tools.initApp()
    if request.method == 'POST' and session.get('app_id'):
      img_path = request.form.get('img')
      numshelf = request.form.get('numshelf')
      img_num = request.form.get('img_num')
      # rebuild local path for img
      upload_dir = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], 'users', str(globalVars['arduino_map']['user_id']), str(session.get('app_id')), numshelf)#, 'resize')
      if not os.path.exists(upload_dir):
        abort(404)
      # perform ocr + search
      output = {}
      # execute ocr analyze for image checked
      res = ocrAnalyse(os.path.join(upload_dir, img_path))
      #print(res)
      if 'success' in res:
        # manage exception error in ocr result
        if res['success'] == False:
          output = res
          output.update({'img_num':img_num})
        else:
          # return ocr result
          output = {'success': True, 'response':res['response'], 'ocr_nb_books':len(res['response']), 'img_num':img_num}
      # display result
      response = app.response_class(
        response=json.dumps(output),
        mimetype='application/json'
      )
      return response

  # use api books to retrieve books from ocr result
  @app.route('/api/ajax_bookindexer/', methods=['POST'])
  @flask_login.login_required  
  def searchApiBooksForOcr():
    #print(request.form)
    globalVars = tools.initApp()
    if request.method == 'POST' and session.get('app_id'):# and request.is_json:       
      # book must have title to perform search
      ocrbook = request.form
      app_id = session.get('app_id')
      if 'title' in ocrbook and len(ocrbook['title']) < 2:
        searchedbook = tools.formatBookApi('ocr', ocrbook, None, False)
      else:
        # first, search for book inside shelf index
        if 'id_book' in ocrbook and ocrbook['id_book'].isnumeric():
          searchedbook = db.get_book(ocrbook['id_book'], session.get('app_id'), globalVars['arduino_map']['user_id']) 
        else:
          searchedbook = db.search_book_title(globalVars['arduino_map']['user_id'], ocrbook['title'])
        if searchedbook:
          searchedbook['authors'] = searchedbook['author'].split(',')
          searchedbook['found'] = 'local'
          #app.logger.info('ocr 3 : book found local "%s"', searchedbook['title'])
          # for automatic indexation : set position 
          # if int(ocrbook['autoindex']) == 1:
          #   previousbook = 0
          #   if 'previousbook' in ocrbook:
          #     previousbook = int(ocrbook['previousbook'])
          #   address = db.update_position_before_order(app_id, searchedbook['id'], int(ocrbook['numshelf']), globalVars, 0, previousbook)
          # else:
          address = db.get_position_for_book(app_id, searchedbook['id'], True)
          if address:
            searchedbook['address'] = address
        else:
        #second search with api
          query = ocrbook['title']
          if 'author' in ocrbook and ocrbook['author'] is not None :
            query += " +inauthor:" + ocrbook['author']
          query += "+intitle:"+ocrbook['title']
          #print(query)
          app.logger.info('ocr : search book api with "%s"', query)
          data = tools.searchBookApi(query, 'googleapis')
          #print(data)
          if 'items' in data:
            # first test  : match ocr title into api title 
            test = tools.matchApiSearchResults(ocrbook['title'], data, 'ocr-in-api')
            if test == False:
              # 2nd test  : match api title into ocr title 
              test = tools.matchApiSearchResults(ocrbook['title'], data, 'api-in-ocr')
            if test:
              searchedbook = tools.formatBookApi('googleapis', test, None, True)
              #autmatic save process              
              #app.logger.info('autoindex %s', ocrbook['autoindex'])
              if ocrbook['autoindex'] == 'save_book' or ocrbook['autoindex'] == '1':
                if 'width' not in searchedbook:
                  searchedbook['width'] = round(tools.set_book_width(searchedbook['pages']))                
                bookId = db.bookSave(searchedbook, globalVars['arduino_map']['user_id'], session.get('app_id'), None, ocrbook['title'])
                searchedbook['id'] = bookId['id']
                searchedbook['found'] = 'local'
                app.logger.info('ocr 5 : book saved from api "%s"', searchedbook['title'])
              # if ocrbook['autoindex'] == '1':
              #   previousbook = 0
              #   if 'previousbook' in ocrbook:
              #     previousbook = int(ocrbook['previousbook'])
              #   searchedbook['address'] = db.update_position_before_order(app_id, searchedbook['id'], \
              #     int(ocrbook['numshelf']), globalVars, 0, previousbook)
            # no search result is found
            else:
              searchedbook = tools.formatBookApi('ocr', ocrbook, None, False)
          else:
            searchedbook = tools.formatBookApi('ocr', ocrbook, None, False)

      return render_template('_book_search_result.html', book=searchedbook, numbook=ocrbook['numbook'], numshelf=ocrbook['numshelf'], app_id=session.get('app_id'), img_num=ocrbook['img_num'])
    abort(404)

  # use subprocess to gemeni ocr analyse
  def ocrAnalyse(img_path):
    #return json.loads('{"success": 1, "response": [{"title": "Paris ne finit jamais", "author": "Enrique Vila-Matas", "editor": "José Corti"}, {"title": "Tigre en papier", "author": "Olivier Rolin", "editor": "Hachette"}, {"title": "Le Monde grec antique", "author": "Thomas Piketty", "editor": "Hachette"}, {"title": "Capital et idéologie", "author": "Thomas Piketty", "editor": "Hachette"}, {"title": "Il faut dire que les temps ont changé...", "author": "Daniel Cohen", "editor": "Albin Michel"}, {"title": "La philosophie du catharisme", "author": "René Nelli", "editor": "Seuil"}, {"title": "La vie quotidienne des cathares", "author": "René Nelli", "editor": "Hachette"}, {"title": "Problèmes de linguistique générale", "author": "Benveniste", "editor": "Gallimard"}, {"title": "Histoire du mouvement ouvrier français", "author": "Jacques Girault, Jean-Louis Robert", "editor": "Messioon"}, {"title": "La révolution anarchiste", "author": "Nataf", "editor": "Jurassienne"}, {"title": "Surveiller et punir", "author": "Michel Foucault", "editor": "Gallimard"}, {"title": "Réflexions sur la peine capitale", "author": "Albert Camus", "editor": "Gallimard"}, {"title": "Les esclaves en Grèce ancienne", "author": "Yvon Garlan", "editor": "La Découverte"}, {"title": "Théâtre comique du Moyen Age", "author": "Michel Vovelle", "editor": "Hachette"}, {"title": "Piété baroque et déchristianisation en Provence au XVIIIe siècle", "author": "Michel Vovelle", "editor": "Hachette"}]}')
    
    #return json.loads('{"success": 1, "response": [{"title": "Donne-moi quelque chose qui ne meure pas", "author": "Bobin-Boubat", "editor": "nrf"}, {"title": "Paraboles de Jesus", "author": "Alphonse Maillot", "editor": "None"}, {"title": "La crise de la culture", "author": "Hannah Arendt", "editor": "None"}, {"title": "Thème et variations", "author": "Léo Ferré", "editor": "Le Castor Astral"}, {"title": "Oeuvre romanesques", "author": "Sartre", "editor": ""}, {"title": "Les beaux textes de l\'antiquité", "author": "Emmanuel Levinas", "editor": "GIF"}, {"title": "Nouvelles lectures talmudiques", "author": "", "editor": "NAGEL"}, {"title": "Le banquet", "author": "Platon", "editor": ""}, {"title": "L\'existentialisme", "author": "Sartre", "editor": "lexique des sciences sociales"}, {"title": "Capital et idéologie", "author": "Thomas Piketty", "editor": ""}]}')

    ocr_path = os.path.join(app.root_path, "../../bibliobus-ocr-ia")
    #ocr_output = os.popen("cd " + ocr_path + " && ./ocr_wrapper.sh " + " ".join(img_paths)).read()
    import subprocess
    ocr_output = subprocess.check_output("cd " + ocr_path + " && ./ocr_wrapper.sh " + img_path, shell=True)
    #print(ocr_output)
    try :
      ocr_analyse = json.loads(ocr_output)
      app.logger.info('ocr 1 : ai result: %s', ocr_analyse)
      output = {'success':True, 'response':ocr_analyse}
    except Exception as e:
      print(e)
      output = {'success':False, 'response': 'Error parsing JSON output -- ' + str(e)}
    #print(output)
    return output
