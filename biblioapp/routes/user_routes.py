from flask import Flask, render_template, request, abort, flash, redirect, json, escape, session, url_for, jsonify, \
Response, send_from_directory
import flask_login, hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message

'''
User infos
'''
def set_routes_for_user(app):

  from biblioapp import db, models, tools

  @app.route("/api/user", methods=['GET', 'POST'])
  @app.route("/user", methods=['GET', 'POST'])
  @flask_login.login_required
  def userInfos():
    user = db.get_user(flask_login.current_user.id)
    #user['api_key'] = secrets.token_urlsafe(29)
    if request.method == 'POST':
        firstname=request.form.get('firstname')
        lastname=request.form.get('lastname')
        email=request.form.get('email')
        hash_email = hashlib.md5(email.encode("utf-8")).hexdigest()
        test = db.set_user(email, hash_email, firstname, lastname, None, user['id'])
        if test is not None:
          if user['email'] != email:
            return redirect(url_for('logout', _scheme='https', _external=True))
          else:
            flash('User infos updated', 'success')
            return redirect(url_for('userInfos', _scheme='https', _external=True))
    if request.method == 'GET' and 'api' in request.path:
      response = app.response_class(
        response=json.dumps(user),
        mimetype='application/json'
      )
      return response

    return render_template('user.html', user=user, user_login=flask_login.current_user.name) 

  '''
  Reset Password
  '''
  @app.route("/forgot_password", methods=['GET', 'POST'])
  def forgotPassword():
    mail = Mail(app)
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
    token = ''
    errors = []
    if 'token' in request.args:
      token = request.args.get('token')
      #token was verified by request_loader or user is logged
      if flask_login.current_user.is_authenticated:
        email = flask_login.current_user.id
      else:
        abort(403)    

    #check for changing password
    if request.method == 'POST':
      if flask_login.current_user.is_authenticated:
        email = flask_login.current_user.id    
      else:
        abort(403)         
      user = db.get_user(email)

      #check if current password is correct 
      if 'password' in request.form:
        if check_password_hash(user['password'], request.form['password']) == False:
          errors.append('Your current password is not the same than the one you give.')  

      #check new password
      npassword = request.form.get('upassword')
      cpassword = request.form.get('cpassword')

      if npassword != '' and npassword == cpassword and email != None:
        hashed = generate_password_hash(npassword)
        db.set_user_pwd(email, hashed)
        flash('Your password has been reset', 'success')
      else:
        errors.append('New password is empty or different than password confirm')

      #manage errors
      if 'token' in request.args:
        errorRedirect = 'resetPassword'
        successRedirect = 'login'
        paramsRedirect = {'token':token, '_scheme':'https', '_external':True}
      else:
        errorRedirect = 'userInfos'
        successRedirect = 'userInfos' 
        paramsRedirect = {'_scheme':'https', '_external':True}
      if len(errors) > 0:
        for error in errors:
          flash(error, 'danger')
        return redirect(url_for(errorRedirect, **paramsRedirect))
      else:
        return redirect(url_for(successRedirect, _scheme='https', _external=True))

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
        hash_email = hashlib.md5(email.encode("utf-8")).hexdigest()
        test = db.set_user(email, hash_email, firstname, lastname, hashed, None)
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
    secretKey = app.config['RECAPTCHA_SECRET']
    r = requests.post("https://www.google.com/recaptcha/api/siteverify?secret="+secretKey+"&response="+recaptcha_response)
    data = r.json()
    if 'success' in data:
      if data['score'] >= 0.5: 
        return "ok"
    return "ko"

  @app.route('/api/login', methods=['GET', 'POST'])
  @app.route('/login', methods=['GET', 'POST'])
  def login():
      if request.method == 'GET':
        if request.args.get('saved'):
          flash('Congratulation, your account is saved! You can login now', 'success')  
        return render_template('login.html')

      if request.is_json:
        email = request.json['email']
        pwd = request.json['password']
      else:
        email = request.form['email']
        pwd = request.form['password']
      
      exists = db.get_user(email)
      if exists is not None:
        #hash = generate_password_hash(exists['password'])
        if check_password_hash(exists['password'],pwd):

          user = models.User()
          user.id = email
          user.name = exists['firstname'] 
          flask_login.login_user(user)
          #return token and user infos when api exists in requested url
          if 'api' in request.url:
            token = models.get_token('guest',exists['email'])
            modules = db.get_arduino_for_user(exists['email'])
            user = {'email': exists['email'], 'firstname': exists['firstname'], \
            'lastname': exists['lastname'], 'modules': modules}
            data = [{'user': user, 'token': token}]
            return app.response_class(
                response=json.dumps(data),
                mimetype='application/json'
            )
          return redirect(url_for('selectArduino', _scheme='https', _external=True))

      return 'Bad login'

  @app.route('/logout')
  def logout():
      session.clear()
      flask_login.logout_user()
      flash('Logged out', 'info')
      return redirect(url_for('login', _scheme='https', _external=True))
