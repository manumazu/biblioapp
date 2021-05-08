import pytest, json, jwt
from werkzeug.security import generate_password_hash, check_password_hash
from biblioapp import models, tools, create_app

def test_new_user():
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the email, hashed_password
    """
    user = models.User()
    user.email = 'emmanuel.mazurier@gmail.com'
    user.password = 'b1bl104pp$'
    user.hashed_password = generate_password_hash(user.password)
    assert user.email == 'emmanuel.mazurier@gmail.com'
    assert check_password_hash(user.hashed_password,user.password)


def test_new_token():
    """
    GIVEN a jwt token
    WHEN an email is requested
    THEN check if email belongs to the given token
    """
    flask_app = create_app()
    email = 'emmanuel.mazurier@gmail.com'
    new_token = models.get_token('test',email)
    verif_token = jwt.decode(new_token, flask_app.config['SECRET_KEY'], algorithms=['HS256'])['test']
    assert verif_token == email
    

def test_bibus_encode():
    data = {'id':1, 'arduino_name':'test module', 'id_ble':'bibus0001', 'nb_lines':3, 'nb_cols':62, 'strip_length':102.5, 'leds_interval':1.66, 'mood_color':'118,43,21'}
    """
    GIVEN a user_app structure
    WHEN an id_ble is base64 encoded
    THEN check id_ble string assertion with decoded data
    """
    uuid = tools.uuid_encode(data['id_ble'])
    id_ble =  tools.uuid_decode(uuid)
    assert id_ble.decode('utf-8') == data['id_ble']