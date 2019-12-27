from flask import Flask, render_template, request, abort, flash, redirect, json, escape
from flask_bootstrap import Bootstrap
import flask_login
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_object("config")

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

Bootstrap(app)

from biblioapp import db, tools, models

global arduino_id, user_login

def initApp():
  user_login = False
  if(flask_login.current_user.is_authenticated):
    user_login = flask_login.current_user.name  
    arduino_map = db.get_arduino_map(flask_login.current_user.id)
    arduino_id = arduino_map['id_arduino']
  else:
    user_login = False
    arduino_map = None
    arduino_id = None
  return {'user_login':user_login,'arduino_map':arduino_map,'arduino_id':arduino_id}

@app.route("/")
@app.route('/authors/')
def listAuthors():
  globalVars = initApp()
  if(globalVars['user_login']==False):
    return redirect('/login')
  return render_template('authors.html', user_login=globalVars['user_login'], db=db, user_id=globalVars['arduino_map']['user_id'])

@app.route('/categories/')
def listCategories():
  globalVars = initApp()
  if(globalVars['user_login']==False):
    return redirect('/login')
  categories = db.get_categories(globalVars['arduino_map']['user_id'])
  return render_template('categories.html', user_login=globalVars['user_login'], categories=categories)  

@app.route("/ajax_positions_inline/", methods=['GET'])
@app.route("/app/")
def myBookShelf():
  globalVars = initApp()
  if(globalVars['user_login']==False):
    return redirect('/login')
    
  if request.method == 'GET' and request.args.get('row'):
    row = request.args.get('row')
  else:
    row = None
  tidybooks = db.get_tidy_books(globalVars['arduino_id'], row) #books with addresses
  bookstorange = db.get_books_to_range(globalVars['arduino_id']) #books with position
  #search requested books in tidy books 
  requested_books = db.get_request(globalVars['arduino_id'])
  if requested_books:
   for requested in requested_books:
     if requested['row'] in tidybooks:
       if requested['column'] in tidybooks[requested['row']]:
         tidybooks[requested['row']][requested['column']]['requested']=True
  if request.method == 'GET' and request.args.get('row'):
    response = app.response_class(
      response=json.dumps(tidybooks[int(row)]),
      mimetype='application/json'
    )
    return response
  else:
    return render_template('index.html',user_login=globalVars['user_login'], tidybooks=tidybooks, \
      bookstorange=bookstorange, biblio_nb_rows=globalVars['arduino_map']['nb_lines'])

@app.route('/ajax_sort/', methods=['POST'])
@flask_login.login_required
def ajaxSort():
  if request.method == 'POST':
    current_row = request.form['row'] 
    book_ids = request.form.getlist('book[]')
    sortable = db.sort_items(book_ids, current_row)
    response = app.response_class(
        response=json.dumps(sortable),
        mimetype='application/json'
    )
  return response

@app.route('/ajax_del_position/', methods=['POST'])
@flask_login.login_required
def ajaxDelPosition():
  if request.method == 'POST':
    for elem in request.form:
       book = elem.split('_')
       if db.del_item_position(book, arduino_id):
         ret={'success':True}
       else:
         ret={'success':False}
  response = app.response_class(
        response=json.dumps(ret),
        mimetype='application/json'
  )
  return response

@app.route('/tag/<tag_id>')
@flask_login.login_required
def listNode(tag_id):
  globalVars = initApp()
  nodes = db.get_node_for_tag(tag_id, globalVars['arduino_map']['user_id'])
  tag = db.get_tag_by_id(tag_id)
  if nodes:
      books = {}
      for node in nodes:
          book = db.get_book(node['id_node'], globalVars['arduino_map']['user_id'])
          books[book['id']] = book
          address = db.get_position_for_book(globalVars['arduino_map']['id'], book['id'])
          if address:
            hasRequest = db.get_request_for_position(globalVars['arduino_id'], address['position'], address['row'])
            books[book['id']]['address'] = address
            books[book['id']]['hasRequest'] = hasRequest         
  return render_template('tag.html', books=books, user_login=globalVars['user_login'], \
    arduino_id=globalVars['arduino_id'], author=tag['tag'])  

@app.route('/book/<book_id>')
@flask_login.login_required
def getBook(book_id):
  globalVars = initApp()
  book = db.get_book(book_id, globalVars['arduino_map']['user_id'])
  if book:
      address = db.get_position_for_book(globalVars['arduino_map']['id'], book['id'])
      tags = db.get_tag_for_node(book['id'])
      hasRequest = False
      if address:
        hasRequest = db.get_request_for_position(globalVars['arduino_id'], address['position'], address['row'])
      return render_template('book.html', user_login=globalVars['user_login'], book=book, address=address, tags=tags, \
        arduino_id=globalVars['arduino_id'], biblio_nb_rows=globalVars['arduino_map']['nb_lines'], hasRequest = hasRequest)
  abort(404)

#post request from app
@app.route('/locate/', methods=['GET', 'POST'])
@flask_login.login_required
def locateBook():
  globalVars = initApp()
  if request.method == 'POST':

    if 'remove_request' in request.form:
      db.del_request(globalVars['arduino_id'],request.form['column'], request.form['row'])
      flash('Location removed for book {}'.format(request.form['book_id']))
    else:
      test = db.set_request(globalVars['arduino_id'], request.form.get('row'), request.form.get('column'), request.form.get('range'))
      flash('Location requested for book {}'.format(request.form['book_id']))
    
    if(request.referrer and 'tag' in request.referrer):
      return redirect('/authors')
    return redirect('/')

@app.route('/locate_for_tag/<tag_id>')  
@flask_login.login_required
def locateBooksForTag(tag_id):
  globalVars = initApp()
  nodes = db.get_node_for_tag(tag_id, globalVars['arduino_map']['user_id'])
  db.clean_request(globalVars['arduino_id'])
  for node in nodes:
    address = db.get_position_for_book(globalVars['arduino_map']['id'], node['id_node'])
    if address:
      book = db.get_book(node['id_node'], globalVars['arduino_map']['user_id'])
      db.set_request(globalVars['arduino_id'], address['row'], address['position'], tools.led_range(book['pages']))
      flash('Location requested for book {}'.format(book['title']))
  return redirect('/authors')


#get request from arduino for current arduino_id
@app.route('/request/<uuid>/')
def getRequest(uuid):
  user_app = db.get_app_for_uuid(uuid)
  if(user_app):
    data = db.get_request(user_app['id_arduino'])
    response = app.response_class(
          response=json.dumps(data),
          mimetype='application/json'
    )
    return response
  abort(404)

@app.route('/booksearch/', methods=['GET', 'POST'])
@flask_login.login_required
def searchBookReference():
  import requests
  globalVars = initApp()
  '''search on api'''
  if request.method == 'POST':
    query = "key=AIzaSyBVwKgWVqNaLwgceI_b3lSJJAGLw_uCDos&q="
    if 'isbn' in request.form and request.form['isbn']:
      query += "ISBN:\""+request.form['isbn']+"\"&"
    if 'inauthor' in request.form and request.form['inauthor']:
      query += "inauthor:"+request.form['inauthor']+"+"
    if 'intitle' in request.form and request.form['intitle']:
      query += "intitle:"+request.form['intitle']
    if 'query' in request.form:
      query += request.form['query']
    url = "https://www.googleapis.com/books/v1/volumes?"+query
    r = requests.get(url)
    data = r.json()
    #print(url)
    return render_template('booksearch.html', user_login=globalVars['user_login'], data=data, req=request.form)

  '''get detail on api'''
  if request.method == 'GET' and request.args.get('ref'):
    ref = request.args.get('ref')
    r = requests.get("https://www.googleapis.com/books/v1/volumes/"+ref)
    data = r.json()
    #print(data['volumeInfo'])
    return render_template('booksearch.html', user_login=globalVars['user_login'], book=data['volumeInfo'], ref=ref)
  else:
    return render_template('booksearch.html', user_login=globalVars['user_login'])

@app.route('/bookreferencer/', methods=['POST'])
@flask_login.login_required
def bookReferencer():
  globalVars = initApp()
  if request.method == 'POST':
    authors = request.form.getlist('authors[]')
    bookapi={}
    bookapi['author'] = ', '.join(authors)
    bookapi['title'] = request.form['title']
    bookapi['reference'] = request.form['reference']
    bookapi['isbn'] = request.form['isbn']
    bookapi['description'] = request.form['description']
    bookapi['editor'] = request.form['editor']
    bookapi['pages'] = request.form['pages']
    bookapi['year'] = request.form['year']
    bookId = db.set_book(bookapi, globalVars['arduino_map']['user_id'])
    '''manage tags + taxonomy'''
    authorTags = tools.getLastnameFirstname(authors)
    authorTagids = db.set_tags(authorTags,'Authors')
    catTagIds = db.set_tags(request.form.getlist('tags[]'),'Categories')
    if len(catTagIds)>0:
      db.set_tag_node(bookId, catTagIds)
    if len(authorTagids)>0:
      db.set_tag_node(bookId, authorTagids)
    return redirect('/')
  return render_template('bookreferencer.html', user_login=globalVars['user_login'])


'''
Authentication
'''
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    email = request.form['email']
    exists = db.get_user(email)
    if exists is not None:
      #hash = generate_password_hash(exists['password'])
      if check_password_hash(exists['password'],request.form['password']):

        user = models.User()
        user.id = email
        user.name = exists['name'] 
        flask_login.login_user(user)
        return redirect('/protected')

      return 'Bad login'

@app.route('/protected')
@flask_login.login_required
def protected():
  flash('Logged in as: ' + flask_login.current_user.name)
  return redirect('/')

@app.route('/logout')
def logout():
    flask_login.logout_user()
    flash('Logged out')
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
