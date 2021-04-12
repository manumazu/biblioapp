import pytest, json, jwt
from werkzeug.security import generate_password_hash, check_password_hash
from biblioapp import models, create_app

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
    verif_token = jwt.decode(new_token, flask_app.config['SECRET_KEY'],algorithms=['HS256'])['test']
    assert verif_token == email