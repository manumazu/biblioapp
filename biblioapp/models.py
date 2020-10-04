from biblioapp import app, db, tools, flask_login, login_manager, session, hashlib, redirect, url_for, request, jsonify, Response
from time import time
import jwt


#users = {'foo@bar.tld': {'password': 'secret'}}
#mandatory for flask_login 
class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    exist = db.get_user(email)
    if exist is None:
        return

    user = User()
    user.id = exist['email']
    user.name = exist['firstname']
    return user


@login_manager.request_loader
def request_loader(request):
    '''login via token for uuid'''
    exist = None
    token = None
    if 'token' in request.args:
        token = request.args.get('token')
    if 'token' in request.form:
        token = request.form.get('token')
    if token:     
        #verify token for reset password
        if 'reset_password' in request.path:
            exist = verify_token('auth',token)
        #verify token for guest requests            
        elif 'uuid' in request.view_args or 'uuid' in request.args or 'uuid' in request.form :
            exist = verify_token('guest',token)
        if exist is None:
            return 
        #open session for mobile app request
        if 'uuid' in request.view_args or 'uuid' in request.args or 'uuid' in request.form :
            if 'uuid' in request.view_args:
                uuid = request.view_args.get('uuid')
            if 'uuid' in request.args:
                uuid = request.args.get('uuid')
            if 'uuid' in request.form:
                uuid = request.form.get('uuid')                
            uuid = tools.uuid_decode(uuid)
            #check arduino module for given user
            module = db.get_user_for_uuid(uuid)
            if module is None:
                return 
            session['app_id'] = module['id_app']
            session['app_name'] = module['arduino_name']   
            session['email'] = exist['email']
            session['firstname'] = exist['firstname']
        #send user
        user = User()
        user.id = exist['email']
        user.name = exist['firstname']     
        return user
    '''login via form wwith session'''
    if 'email' in request.form: 
        email = request.form.get('email')
        exist = db.get_user(email)  
        if exist is None:
            return 

        user = User()
        user.id = email

        # DO NOT ever store passwords in plaintext and always compare password
        # hashes using constant-time comparison!
        user.is_authenticated = request.form['password'] == exist['password']
        return user
    return 

@login_manager.unauthorized_handler
def unauthorized_handler():
    #return 'Unauthorized'
    if 'token' in request.args:
        #manage error response for request with SSE
        if 'uuid' in request.args and 'request' in request.path:
            resp = "event: error\n"
            resp += "data:Unauthorized"
            resp += "\nretry: 5000"
            resp += "\n\n"
            return Response(resp, status=200, mimetype='text/event-stream')    
        else:
            return jsonify(success=False,
                       data={'token_required': True},
                       message='Authorize please to access this page.'), 401
    else:
        return redirect(url_for('login', _scheme='https', _external=True))

#generate generic token 
def get_token(role,email, expires_in=600):
    return jwt.encode({role: email, 'exp': time() + expires_in}, \
        app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

#verify token
def verify_token(role,token):
    try:
        id = jwt.decode(token, app.config['SECRET_KEY'],algorithms=['HS256'])[role]
    except:
        return
    #when a session is open return it
    if 'email' in session and id == session['email']:
        #print(id)
        return session
    return db.get_user(id)

