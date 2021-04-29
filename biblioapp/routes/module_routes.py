from flask import Flask, render_template, request, abort, flash, redirect, json, escape, session, url_for, jsonify, \
Response, send_from_directory
import flask_login, hashlib, math

'''
Module functionalities
'''
def set_routes_for_module(app):

  from biblioapp import db, models, tools

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
        flash('Bookshelf "{}"selected'.format(request.form.get('module_name')), 'info')
        return redirect(url_for('myBookShelf', _scheme='https', _external=True))
    if request.method == 'GET':
      if request.args.get('app_id'):
        session['app_id'] = request.args.get('app_id')
        return redirect(url_for('editArduino', app_id=session['app_id'], _scheme='https', _external=True))
    return render_template('modules.html', user_login=flask_login.current_user.name, modules=modules)

  @app.route("/module/<app_id>", methods=['GET', 'POST'])
  @flask_login.login_required
  def editArduino(app_id):
    globalVars = tools.initApp()
    module = db.get_arduino_map(flask_login.current_user.id, app_id) #globalVars['arduino_map']
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
            #print(positions)
            for i in range(len(positions)):
              pos = i+1        
              if mode == 'save': 
                db.set_position(app_id, pos, pos, numrow, 1, 'static', positions[i])            
              if mode == 'preview': #set distant request for preview
                db.set_request(app_id, pos, numrow, pos, 1, positions[i], 'static', 'server', 'add')
              if mode == 'remove': #remove all static 
                db.del_item_position(int(app_id), pos, 'static', numrow)        
      return render_template('module.html', user_login=flask_login.current_user.name, module=module, db=db, shelf_infos=globalVars['arduino_map'])
    abort(404) 

  #get module infos from arduino for current arduino_name
  @app.route('/api/module/<uuid>/')
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

  #create new module or edit characteristic of an arduino existing module
  @app.route("/adminmodule/", defaults={'app_id': None}, methods=['GET', 'POST'])
  @app.route("/adminmodule/<app_id>/", methods=['GET', 'POST'])
  @flask_login.login_required
  def newArduino(app_id = None):
    globalVars = tools.initApp()
    if flask_login.current_user.id == app.config['SHELF_ADMIN_EMAIL']:
      if app_id is not None:
        module = db.get_module(app_id)
      else:
        module = {}
      #user_id = globalVars['arduino_map']['user_id']
      users = db.get_users()
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
        data['id_user'] = request.form.get('user')
        #don't erease current BLE gatt 
        if request.form.get('module_id'):
          data['module_id'] = request.form.get('module_id')
          data['id_ble'] = module['id_ble']
        else:
          data['id_ble'] = "xxxx" #set empty id_ble
        #save module, set user_app, and set id_ble
        new_module = db.set_module(data)
        if 'id' in new_module:
            db.set_user_app(data['id_user'], new_module['id'])
            module = db.get_module(new_module['id'])
            if module['id_ble']=='xxxx':
              id_ble = tools.set_id_ble(module)
              db.update_id_ble(module['id'], id_ble)
            return redirect(url_for('newArduino', _scheme='https', _external=True, app_id=new_module['id']))
      if request.args.get('module_id'):
        module = db.get_module(request.args.get('module_id'))
      return render_template('module_admin.html', user_login=flask_login.current_user.name, module=module, users=users, \
        shelf_infos=globalVars['arduino_map'])
    abort(404)