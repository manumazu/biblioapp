from flask import Flask, render_template, request, abort, flash, redirect, json, escape
from flask_bootstrap import Bootstrap
import flask_login

app = Flask(__name__)
app.config.from_object("config")

login_manager = flask_login.LoginManager()
login_manager.init_app(app)


Bootstrap(app)

from biblioapp import db, tools, models

global arduino_id
arduino_map = db.get_arduino_map()
arduino_id = arduino_map['id_arduino']

@app.route("/")
@app.route("/app/")
@app.route("/ajax_positions_inline/", methods=['GET'])
def home():
  if request.method == 'GET' and request.args.get('row'):
    row = request.args.get('row')
  else:
    row = None
  tidybooks = db.get_tidy_books(arduino_id, row) #books with addresses
  bookstorange = db.get_books_to_range(arduino_id) #books with position
  #search requested books in tidy books 
  requested_books = db.get_request(arduino_id)
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
    user_login = False
    if(flask_login.current_user.is_authenticated):
      user_login = flask_login.current_user.name
    return render_template('index.html',user_login=user_login, tidybooks=tidybooks, bookstorange=bookstorange, biblio_nb_rows=arduino_map['nb_lines'])
  
@app.route('/ajax_sort/', methods=['POST'])
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

@app.route('/authors/')
def listAuthors():
  return render_template('authors.html',db=db)

@app.route('/tag/<tag_id>')
def listNode(tag_id):
  nodes = db.get_node_for_tag(tag_id)
  tag = db.get_tag_by_id(tag_id)
  if nodes:
      books = {}
      for node in nodes:
          book = db.get_book(node['id_node'])
          books[book['id']] = book
          address = db.get_position_for_book(book['id'])
          if address:
            hasRequest = db.get_request_for_position(arduino_id, address['position'], address['row'])
            books[book['id']]['address'] = address
            books[book['id']]['hasRequest'] = hasRequest         
  return render_template('tag.html', books=books, arduino_id=arduino_id, author=tag['tag'])  

@app.route('/book/<book_id>')
def getBook(book_id):
    book = db.get_book(book_id)
    if book:
        address = db.get_position_for_book(book['id'])
        tags = db.get_tag_for_node(book['id'])
        hasRequest = False
        if address:
          hasRequest = db.get_request_for_position(arduino_id, address['position'], address['row'])
        return render_template('book.html', book=book, address=address, tags=tags, arduino_id=arduino_id,  \
          biblio_nb_rows=arduino_map['nb_lines'], hasRequest = hasRequest)
    abort(404)

#post request from app
@app.route('/locate/', methods=['GET', 'POST'])
def locateBook():
    if request.method == 'POST':
      if 'remove_request' in request.form:
        db.del_request(arduino_id,request.form['column'], request.form['row'])
        flash('Location removed for book {}'.format(request.form['book_id']))
      else:
        test = db.set_request(request)
        flash('Location requested for book {}'.format(request.form['book_id']))
      if(request.referrer and 'tag' in request.referrer):
        return redirect('/authors')
      return redirect('/')

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
def searchBookReference():
  import requests
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
    print(url)
    return render_template('booksearch.html',data=data, req=request.form)
  '''get detail on api'''
  if request.method == 'GET' and request.args.get('ref'):
    ref = request.args.get('ref')
    r = requests.get("https://www.googleapis.com/books/v1/volumes/"+ref)
    data = r.json()
    #print(data['volumeInfo'])
    return render_template('booksearch.html',book=data['volumeInfo'], ref=ref)
  else:
    return render_template('booksearch.html')

@app.route('/bookreferencer/', methods=['POST'])
def bookReferencer():
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
    bookId = db.set_book(bookapi)
    '''manage tags + taxonomy'''
    authorTags = tools.getLastnameFirstname(authors)
    authorTagids = db.set_tags(authorTags,'Authors')
    catTagIds = db.set_tags(request.form.getlist('tags[]'),'Categories')
    if len(catTagIds)>0:
      db.set_tag_node(bookId, catTagIds)
    if len(authorTagids)>0:
      db.set_tag_node(bookId, authorTagids)
    return redirect('/')
  return render_template('bookreferencer.html')


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

      if request.form['password'] == exists['password']:

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
