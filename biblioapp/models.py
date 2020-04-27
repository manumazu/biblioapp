from biblioapp import app, db, tools, flask_login, login_manager, session, hashlib, redirect, url_for


users = {'foo@bar.tld': {'password': 'secret'}}

class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    exist = db.get_user(email)
    if exist is None:
        return

    user = User()
    user.id = exist['email']
    user.name = exist['name']
    return user


@login_manager.request_loader
def request_loader(request):
    '''login via token for uuid'''
    if 'token' in request.args:
        if 'uuid' in request.view_args or 'uuid' in request.args :
            if 'uuid' in request.view_args:
                uuid = request.view_args.get('uuid')
            if 'uuid' in request.args:
                uuid = request.args.get('uuid')
            uuid = tools.uuid_decode(uuid)
            exist = db.get_user_for_uuid(uuid)
            if exist is None:
                return
            hashmail = hashlib.md5(exist['email'].encode('utf-8')).hexdigest()
            if request.args.get('token')==hashmail:
                session['app_id'] = exist['id_app']
                session['app_name'] = exist['arduino_name']
                user = User()
                user.id = exist['email']
                user.name = exist['name']
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
    return redirect(url_for('login', _scheme='https', _external=True))  
