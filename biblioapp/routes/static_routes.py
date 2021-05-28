from flask import Flask, render_template, request, abort, flash, redirect, json, escape, session, url_for, jsonify, \
Response, send_from_directory
import flask_login

'''
Static pages
'''
def set_routes_for_static_pages(app):

  @app.route("/")
  def root():
    #detect language in header request
    browserLang = request.accept_languages.best_match(app.available_locales)
    return redirect(url_for('presentation', language=browserLang.split('_')[0], _scheme='https', _external=True))

  @app.route("/<language>")
  def presentation(language = 'fr'):
    userName = ""
    if flask_login.current_user.is_authenticated:
      userName=flask_login.current_user.name
    if language not in app.languages:
      language = 'fr'
    #print(app.languages[language])      
    return render_template('index.html', **app.languages[language], current_language=language, available_languages=app.available_languages, user_login=userName)

  @app.route('/privacy')
  def privacy():
	  return render_template('privacy.html') 

  @app.route('/offline')
  def offline():
	  return render_template('offline.html')       

  @app.route('/apple-app-site-association')
  @app.route('/manifest.json')
  @app.route('/favicon.ico')
  @app.route('/sw.js')
  def static_from_root():
	  return send_from_directory(app.static_folder, request.path[1:])

  @app.route('/.well-known/assetlinks.json')
  def assetlinks():
    return send_from_directory(app.static_folder, 'assetlinks.json') 
