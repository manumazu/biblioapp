from flask import Flask, render_template, request, abort, flash, redirect, json, escape, session, url_for, jsonify, \
Response, send_from_directory
import flask_login, hashlib

'''
Manage positions for elements in shelves
'''
def set_routes_for_positions(app):

  from biblioapp import db, models, tools

  #used when no color is customized : blue
  color_default = '51, 102, 255'

  '''
  manage location requests
  '''

  #post request from app
  @app.route('/locate/', methods=['GET', 'POST'])
  @app.route('/api/locate/', methods=['GET', 'POST'])
  @flask_login.login_required
  def locateBook():
    globalVars = tools.initApp()
    action = 'add'
    positions = []
    color = color_default #default blue color
    app_id = session['app_id']
    book_id = None
    address = None
    client = 'server'
    if ('api' in request.path and 'token' in request.args):
      client = 'mobile'

    '''get form request params'''
    if (request.method == 'POST'):
      app_id = request.form.get('app_id')
      column = request.form.get('column')
      row = request.form.get('row')
      book_id = request.form.get('book_id')
      leds_range = request.form.get('range')
      address = db.get_position_for_book(app_id, book_id)
      if address['borrowed'] == 1:
        color = '255,0,0'
      if 'remove_request' in request.form:
        action = 'remove'

    '''get params for location'''      
    if (request.method == 'GET'):
      app_id = session['app_id']
      book_id = request.args.get('book_id')
      color = request.args.get('color')
      address = db.get_position_for_book(app_id, book_id)    
      if 'remove_request' in request.args:
        action = 'remove'

    #manage request
    if address != None and book_id != None :
      db.set_request(app_id, book_id, address['row'], address['position'], address['range'], address['led_column'], \
      'book', client, action, None, color)
      if action == 'remove':
        retMsg = 'Location removed for book {}'.format(book_id)
      else: 
        retMsg = 'Location requested for book {}'.format(book_id)
      flash(retMsg, 'info')
    else :
      retMsg = 'Unable to find book'
      flash(retMsg, 'danger')

    #send data for mobile
    if('api' in request.path and 'token' in request.args):
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
    
    if(request.referrer and 'tag' in request.referrer):
      return redirect(url_for('listAuthors', _scheme='https', _external=True))
    return redirect(url_for('myBookShelf', _scheme='https', _external=True))

  @app.route('/locate_for_tag/<tag_id>') 
  @app.route('/api/locate_for_tag/<tag_id>')  
  @flask_login.login_required
  def locateBooksForTag(tag_id, methods=['GET', 'POST']):
    globalVars = tools.initApp()
    nodes = db.get_node_for_tag(tag_id, session.get('app_id'))
    tag = db.get_tag_by_id(tag_id, globalVars['arduino_map']['user_id'])

    if tag['color'] is not None:
      colors = tag['color'].split(",")
      tag['red'] = colors[0]
      tag['green'] = colors[1]
      tag['blue'] = colors[2]
    else:
      tag['color'] = color_default

    action = 'add'
    if('action' in request.args):#for add or remove
      action = request.args.get('action')

    client = 'server'
    if('token' in request.args):
      client = 'mobile'

    positions = []
    if nodes:
      for node in nodes:
        address = db.get_position_for_book(session['app_id'], node['id_node'])
        if address:
          book = db.get_book(node['id_node'], session.get('app_id'), globalVars['arduino_map']['user_id'])
      
          #manage request
          db.set_request(session['app_id'], node['id_node'], address['row'], address['position'], address['range'], \
            address['led_column'], 'book', client, action, tag_id, tag['color'])

          #if tag['color'] is None:
          #  tag['color'] = color_default

          positions.append({'item':book['title'], 'action':action, 'row':address['row'], 'led_column':address['led_column'], \
          'interval':address['range'], 'id_tag':tag_id, 'color':tag['color'], 'id_node':node['id_node'], 'client':client})

    '''get elements for block build'''
    positions.sort(key=tools.sortPositions)
    blocks = tools.build_block_position(positions, action)
    #print(blocks)

    #send json when token mode
    if('api' in request.path and 'token' in request.args):
      response = app.response_class(
        response=json.dumps(blocks),
        mimetype='application/json'
      )
      return response
    for i, book in enumerate(positions):
      flash('Location requested for book {}'.format(book['item']), 'info')
    return redirect(url_for('listAuthors', _scheme='https', _external=True))

  #get request from arduino for current arduino_name
  @app.route('/request', methods=['GET'])
  @app.route('/api/request', methods=['GET'])
  @flask_login.login_required
  def getRequestForModule():
    globalVars = tools.initApp()
    if globalVars['arduino_map'] != None:  

      #get request for distant mobile app
      #if('uuid' in request.args):
      source = 'server'
      if 'api' in request.path and 'token' in request.args:
        source = 'mobile'
        
      positions_add = []
      blocks = []
      has_nodes = 0 # used for gaming
      if source == 'mobile':
        datas_add = db.get_request_for_mobile(session['app_id'], 'add', 0)
      else:
        datas_add = db.get_request(session['app_id'], 'add')
      
      if datas_add:   
        for i, data in enumerate(datas_add):

          has_nodes += data['id_node']

          if data['color'] is None:
            data['color'] = color_default

          #build simple requests blocks for gaming
          if data['id_node'] == 0: 
            blocks.append({'action':data['action'], 'row':data['row'], 'index':i, 'start':data['led_column'], 'color':data['color'], 'id_tag':data['id_tag'],'interval':data['range'], 'nodes':[0], 'client':data['client']})
          #build position array for books requests
          else:
            positions_add.append({'action':data['action'], 'row':data['row'], \
              'led_column':data['led_column'], 'interval':data['range'], 'id_tag':data['id_tag'], \
              'color':data['color'], 'id_node':data['id_node'], 'client':data['client']})
            
          #flag sent nodes for SSE requests in mobile App
          if source == 'mobile':
            db.set_request_sent(session['app_id'], data['id_node'], 1)
              
        #arrange positions inside blocks for books request + manage remove
        if has_nodes:
          positions_add.sort(key=tools.sortPositions)          
          blocks += tools.build_block_position(positions_add, 'add')

      #removing requests for nodes
      positions_remove = []  
      datas_remove = db.get_request(session['app_id'], 'remove')
      #resp = "event: ping\n"
      if datas_remove:
        #soft remove   
        for data in datas_remove:
          #send remove for mobile only when request come from server 
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

      #reset requests 
      reset_requests = []  
      reset = db.get_request_for_mobile(session['app_id'], 'reset', 0)
      #resp = "event: ping\n"
      if reset:
        #soft remove   
        for data in reset:
          #send remove for mobile only when request come from server 
          if (source == 'mobile' and data['client']=='server') or (source == 'server'):
            blocks.append({'action':data['action'], 'client':data['client']})
        # clean reset request sent            
        if source == 'mobile':
          db.del_reset_request(session['app_id']) 
          
      #print(blocks)
      
      # decrease delay for gaming
      delay = "500" if has_nodes == 0 and reset == None else "2000"

      #print(delay)
      
      #set message for SSE
      resp = "event: ping\n"
      if len(blocks) > 0:        
        json_dump = json.dumps(blocks)
        resp += "data: "+json_dump
        resp += "\nid: "+hashlib.md5(json_dump.encode("utf-8")).hexdigest()
        resp += "\nretry: "+delay
      else:
        resp += "\ndata: {}"
        resp +="\nid: 0"
        resp += "\nretry: 5000"
      resp += "\n\n"
      return Response(resp, mimetype='text/event-stream') 

      #response = app.response_class(response=json.dumps(blocks),mimetype='application/json')
      #return response   
    #abort(404)

  #record requests sent from bibliogame application
  @app.route('/request', methods=['POST'])
  @app.route('/api/request', methods=['POST'])
  @flask_login.login_required
  def setRequestForModule():
    globalVars = tools.initApp()
    if request.is_json:
      jsonr = request.get_json()
      blocks = tools.build_block_position(jsonr, 'add')
      #print(blocks)
      for block in blocks:
        if type(block['nodes']) is list:
          for node in block['nodes']:
            #app_id, node_id, row, column, interval, led_column, node_type, client, action, tag_id = None, color = None
            db.set_request(session['app_id'], node, block['row'], block['start'], \
              block['interval'], block['start'], 'book', block['client'], block['action'], \
              block['id_tag'], block['color']);
      response = app.response_class(
        response=json.dumps(blocks),
        mimetype='application/json'
      )
      return response
    abort(404)       

  #remove all request from arduino for current module
  @app.route('/api/reset', methods=['GET'])
  @flask_login.login_required
  def setResetForModule():
    globalVars = tools.initApp()
    if globalVars['arduino_map'] != None:
      data = db.set_request_remove(session['app_id'])
      response = app.response_class(
            response=json.dumps(data),
            mimetype='application/json'
      )
      return response
    abort(404)

  #add reset request for server demand and remove all gaming requests
  @app.route('/api/reset-game', methods=['POST'])
  @flask_login.login_required
  def askResetForModule():
    globalVars = tools.initApp()
    if globalVars['arduino_map'] != None:
      if request.is_json:
        jsonr = request.get_json()
        #print(jsonr)
        if jsonr[0] and jsonr[0]['action']=='reset':
          db.set_reset_request(session['app_id'])
          db.clean_request_game(session['app_id'])
      response = app.response_class(
            response=json.dumps(True),
            mimetype='application/json'
      )
      return response
    abort(404)


  #get position for book isbn - third party application
  @app.route("/api/get-position-for-modules/<hash_email>")
  def listModules(hash_email):
    modules = db.get_arduino_for_api(hash_email)
    data = {}
    if modules:
        data['token'] = models.get_token('guest',modules[0]['email'])
        data['bibus'] = []
        for module in modules:
          data['bibus'].append({'uuid': tools.uuid_encode(module['id_ble']), 'name': module['arduino_name']})
        response = app.response_class(
              response=json.dumps(data),
              mimetype='application/json'
        )
        return response
    abort(401)   


  '''
  Manage positions
  '''
  @app.route("/ajax_positions_inline/", methods=['GET'])
  @flask_login.login_required
  def jsonBookshelf(): 
    globalVars = tools.initApp()
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


  @app.route('/api/sort', methods=['POST'])
  @app.route('/ajax_sort/', methods=['POST'])
  @flask_login.login_required
  def ajaxSort():
    globalVars = tools.initApp()
    book_ids = []

    if request.method == 'POST' and session.get('app_id'):
  
      reset_positions = False
      if request.is_json and 'book_ids' in request.json:
        book_ids = request.json['book_ids']
        current_row = request.json['row']
        #lastPos = request.json['last_position'] 
      elif 'row' in request.form:
        current_row = request.form['row'] 
        book_ids = request.form.getlist('book[]')
        source_img_num = 0
        if 'source_img_num' in request.form:
          source_img_num = request.form['source_img_num'] 
        if 'reset_positions' in request.form:
          reset_positions = True        

      if len(book_ids) > 0:
        app_id = session.get('app_id')
        sortable = []
        postedPos = {}
        shift_position = 0   
        previousbook = 0
        decrease = 0

        #clean positions for current shelf
        if reset_positions:
          db.del_positions_for_shelf(app_id, current_row)

        # merge positions already in shelf with new positions
        new_positions = []
        bdd_positions = []
        current_positions = db.get_positions_for_row(app_id, current_row)
        if current_positions:
          for pos in current_positions:
            bdd_positions.append(str(pos['id_item']))
        
        # prevent not changing order for ocr position 
        for bid in bdd_positions:
          if bid not in new_positions and bid not in book_ids:
            new_positions.append(bid)
             
        for bid in book_ids:
          if bid not in new_positions:
            new_positions.append(bid)

        # update all positions for current shelf
        pos = 0
        for i, book_id in enumerate(new_positions):
          
          # shift book position for books not found in ocr result
          if book_id.startswith('empty'):
            shift_position = int(book_id.split('_')[1])

          # save position
          if book_id.isnumeric():
            pos += 1
            db.update_position_before_order(app_id, book_id, current_row, globalVars, pos, shift_position)
            #app.logger.info('id %s, pos %s shift_position %s', book_id, pos, shift_position)
            shift_position = 0
                
        #app.logger.info('new positions %s', new_positions)

        #update new leds number
        positions = db.get_positions_for_row(app_id, current_row)
        for pos in positions:
          led_columns_sum = db.get_led_column(app_id, pos['id_item'], current_row, pos['position'])
          db.set_led_column(app_id, pos['id_item'], current_row, led_columns_sum)
          sortable.append({'book':pos['id_item'], 'position':pos['position'], 'fulfillment':int(led_columns_sum+pos['range']), 'led_column':led_columns_sum, \
           'shelf':current_row})

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
    globalVars = tools.initApp()
    if request.method == 'POST' and session.get('app_id'):
      book_id = request.form.get('book_id')
      #leds_range = request.form.get('range')
      #update book width
      book = db.get_book(book_id, session.get('app_id'), globalVars['arduino_map']['user_id'])
      book_width = request.form.get('new_book_width')
      book['width'] = round(float(book_width))
      db.set_book(book, globalVars['arduino_map']['user_id'], session.get('app_id'))
      leds_range = tools.led_range(book, globalVars['arduino_map']['leds_interval'])
      #update position
      column = request.form.get('column');
      row = request.form.get('row')
      app_id = session.get('app_id')
      db.set_position(app_id, book_id, column, row, leds_range, 'book', 0) #reinit led column
      led_column = db.get_led_column(app_id, book_id, row, column)
      db.set_led_column(app_id, book_id, row, led_column)
      ret={'led_column':int(led_column)}
      response = app.response_class(
            response=json.dumps(ret),
            mimetype='application/json'
      )
      return response

  @app.route('/ajax_del_position/', methods=['POST'])
  @flask_login.login_required
  def ajaxDelPosition():
    globalVars = tools.initApp()
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
            app_id = session.get('app_id')
            i=0
            sortable = []
            for item in items:
              position = db.get_position_for_book(app_id, item['id_item'])
              if position:
                interval = position['range'] 
              else:
                book = db.get_book(item['id_item'], app_id, globalVars['arduino_map']['user_id'])
                interval = tools.led_range(book, globalVars['arduino_map']['leds_interval'])
              i+=1   
              db.set_position(app_id, item['id_item'], i, position['row'], interval, 'book', 0) #reinit led column
            
            #update new leds number
            positions = db.get_positions_for_row(app_id, position['row'])
            for pos in positions:
              led_column = db.get_led_column(app_id, pos['id_item'], pos['row'], pos['position'])
              db.set_led_column(app_id, pos['id_item'], pos['row'], led_column)
              sortable.append({'book':pos['id_item'], 'position':pos['position'], 'fulfillment':int(led_column+pos['range']), 'shelf':pos['row']})

    response = app.response_class(
          response=json.dumps(sortable),
          mimetype='application/json'
    )
    return response


  @app.route('/ajax_permute_position/')
  @flask_login.login_required
  def ajaxPermutePosition():
    globalVars = tools.initApp()
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
