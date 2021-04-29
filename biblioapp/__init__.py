from flask import Flask, render_template, request, abort, redirect, json, escape, session, url_for, jsonify, \
Response, send_from_directory
from flask_bootstrap import Bootstrap
import flask_login, hashlib, base64, os
from flask_session import Session
from flask_cors import CORS

login_manager = flask_login.LoginManager()

#entry point for entire application, used in unit tests
def create_app():
  app = Flask(__name__)
  CORS(app, resources={r"/api/*": {"origins": "*"}})
  app.config.from_pyfile("../config.py")
  #override elements from environment settings
  for variable, value in os.environ.items():
    #if variable.startswith("MYSQL_"):
    app.config[variable] = value

  #Session(app)
  sess = Session()
  sess.init_app(app)
  bootstrap = Bootstrap(app)
  login_manager.init_app(app)

  from biblioapp.routes.user_routes import set_routes_for_user
  from biblioapp.routes.static_routes import set_routes_for_static_pages
  from biblioapp.routes.module_routes import set_routes_for_module
  from biblioapp.routes.positions_routes import set_routes_for_positions
  from biblioapp.routes.books_routes import set_routes_for_books
  from biblioapp.routes.customize_routes import set_routes_for_customization
  set_routes_for_user(app)
  set_routes_for_static_pages(app)
  set_routes_for_module(app)
  set_routes_for_positions(app)
  set_routes_for_books(app)
  set_routes_for_customization(app)

  return app

app = create_app()

if __name__ == "__main__":
  app.run(debug=True)
