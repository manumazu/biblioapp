from flask import Flask, render_template, request, abort, flash, redirect, json, escape
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.secret_key = '2d9-E2.)f&é,A$p@fpa+zSU03êû9_'
Bootstrap(app)

from biblioapp import db, tools

global arduino_id
arduino_map = db.get_arduino_map()
arduino_id = arduino_map['id_arduino']

@app.route("/")
@app.route('/<arduino_id>/')
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
    return render_template('index.html',arduino_id=arduino_id, tidybooks=tidybooks, bookstorange=bookstorange, biblio_nb_rows=arduino_map['nb_lines'])

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
       if db.del_item_position(book):
         ret={'success':True}
       else:
         ret={'success':False}
  response = app.response_class(
        response=json.dumps(ret),
        mimetype='application/json'
  )
  return response

@app.route('/book/<book_id>')
def getBook(book_id):
    book = db.get_book(book_id)
    if book:
        address = db.get_position(book['id'])
        tags = db.get_tag_for_node(book['id'])
        return render_template('book.html', book=book, address=address, tags=tags, arduino_id=arduino_id, biblio_nb_rows=arduino_map['nb_lines'])
    abort(404)

#post request from app
@app.route('/locate/', methods=['GET', 'POST'])
def locateBook():
    if request.method == 'POST':
      test = db.set_request(request)
      flash('Location requested for book {}'.format(request.form['book_id']))
      return redirect('/')

#get request from arduino for current arduino_id
@app.route('/request/')
def getRequest():
  data = db.get_request(arduino_id)
  response = app.response_class(
        response=json.dumps(data),
        mimetype='application/json'
  )
  return response

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
    #print(url)
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
   
if __name__ == "__main__":
    app.run(debug=True)
