from flask import Flask, render_template, request, abort, flash, redirect, json, escape, session, url_for, jsonify, \
Response, send_from_directory
import flask_login, hashlib, math

'''
Customization functionalities
'''
def set_routes_for_customization(app):

  from biblioapp import db, models, tools

  @app.route('/customcodes', methods=['GET', 'POST'])
  @app.route('/api/customcodes', methods=['GET', 'POST'])
  @flask_login.login_required
  def customCodes():
    globalVars = tools.initApp()
    if globalVars['arduino_map'] != None:
      #print(codes)
      #send json when token mode
      if('api' in request.path and 'token' in request.args and request.method == 'GET'):
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
        flash('Your code is saved', 'success')  
      #manage post data from json request
      if request.method == 'POST':
        if request.is_json:
            jsonr = request.get_json()
            #print(jsonr[0]['customvars'])
            db.set_customcode(globalVars['arduino_map']['user_id'], session['app_id'], None, jsonr['title'], jsonr['description'], \
              jsonr['published'], json.dumps(jsonr['customvars']), jsonr['customcode'])
            #print(request.data.decode())
            if('api' in request.path):
              response = app.response_class(
                response=json.dumps([True]),
                mimetype='application/json'
              )
              return response
      codes = db.get_customcodes(globalVars['arduino_map']['user_id'], session['app_id'])
      maxLeds = globalVars['arduino_map']['nb_cols']*globalVars['arduino_map']['nb_lines']      
      return render_template('customcodes.html', user_login=globalVars['user_login'], customcodes=codes, \
        json=json, max_leds=maxLeds, shelf_infos=globalVars['arduino_map'])
    abort(404)

  @app.route('/customcode/<code_id>', methods=['GET', 'POST'])
  @app.route('/api/customcode/<code_id>', methods=['GET', 'POST'])
  @flask_login.login_required
  def customCode(code_id):
    globalVars = tools.initApp()
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
        if('api' in request.path and 'token' in request.args):
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
    globalVars = tools.initApp()
    code_id = request.form['id']
    customcode = db.get_customcode(globalVars['arduino_map']['user_id'], session['app_id'], code_id)
    if customcode: 
      db.del_customcode(code_id, globalVars['arduino_map']['user_id'])
      flash('Code "{}" is deleted'.format(customcode['title']), 'warning')
      return redirect(url_for('customCodes', _scheme='https', _external=True))  

  @app.route('/ajax_customcodetemplate/<template>')
  @flask_login.login_required
  def customCodeTemplate(template):
    globalVars = tools.initApp()
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


  @app.route("/customcolors/<app_id>", methods=['GET', 'POST'])
  @flask_login.login_required
  def customColors(app_id):
    globalVars = tools.initApp()
    user_id = globalVars['arduino_map']['user_id']
    module = db.get_arduino_map(flask_login.current_user.id, app_id)
    #print(module)
    if module:
      #session['app_id'] = module['id']
      #session['app_name'] = module['arduino_name']
      
      #parse coordinates from db
      customcoords = ''
      dbcoords = db.get_customcolors(user_id, app_id)
      if(dbcoords and dbcoords['coordinates']!=''):
        customcoords = json.loads(dbcoords['coordinates'])
      #print(customcoords)

      if request.method == 'POST':
        if request.is_json:
          mode = request.args.get('mode')
          data = request.get_json()
          #print(data)

          #group data by colors and positions
          colorpos = {}
          for numrow, positions in data.items():
            for i, position in enumerate(positions):
              start = 0
              if(i>0):
                start = int(positions[i-1]['handle'])+1
              tmp = [[start,int(position['handle'])],int(numrow)+1]
              if position['color'] not in colorpos:
                colorpos.update({position['color']: [tmp]})
              else:
                colorpos[position['color']].append(tmp)

          #set coordinates : group by colors and "x" positions for computing "y" coords 
          coords = {}
          for color, positions in colorpos.items():
            #sort list by x position
            positions.sort(key=tools.sortCoords)
            #compute y coords size
            for i, position in enumerate(positions):
              #set variables
              row = int(position[1])
              x_start = int(position[0][0])
              x_end = int(position[0][1])
              x_offset = int(x_end-x_start)
              #set key for grouping dict : color, x pos, x end, first row
              group_key = str(x_start)+'-'+str(x_end)
              
              #check for grouping colors wich have the same position on different rows
              if(i>0):
                if (position[0]==last_pos and row==int(last_row+1)): #matching with previous color position
                  y_start = (row-y_offset)-1
                  y_offset += 1         
                  #print('match', position[1], row, last_row)
                else: #not matching
                  y_start = row-1
                  y_offset = 1
                  #print('nomatch', position[1], row, last_row)
              else: #not matching
                y_start = row-1
                y_offset = 1
                #print('nomatch', position[1], row)              

              #store value for next iteration
              last_pos = position[0] 
              last_row = position[1]

              group_key += '_'+str(y_start)+'_'+color #update key

              #coord = color+'_'+str(x_start)+'-'+str(x_end)+'_'+str(y_start)+'-'+str(y_offset)
              rgb = color.split('(')[1].split(')') #extract rgb
              coord = {'color':rgb[0], 'x_start':x_start, 'x_offset':x_offset, 'y_start':y_start, 'y_offset':y_offset}
              coords[group_key] = coord

          #save datas
          coordinates = json.dumps(coords)
          print(coordinates)        
          db.set_customcolors(user_id, app_id, "test", coordinates)

      return render_template('customcolors.html', user_login=flask_login.current_user.name, customcoords=customcoords, \
       module=module, shelf_infos=globalVars['arduino_map'])
    abort(404) 

  @app.route('/api/customcolors')
  @flask_login.login_required 
  def getCustomColors():
    globalVars = tools.initApp()
    user_id = globalVars['arduino_map']['user_id']
    dbcoords = db.get_customcolors(user_id, session['app_id'])
    if(dbcoords and dbcoords['coordinates']!='' and dbcoords['coordinates']!='{}'):
      response = app.response_class(
        response=dbcoords['coordinates'],
        mimetype='application/json'
      )
      return response
    abort(404) 

  @app.route('/customeffects')
  @app.route('/api/customeffects')
  @flask_login.login_required
  def customEffects():
    globalVars = tools.initApp()
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