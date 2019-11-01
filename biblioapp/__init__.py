from flask import Flask, render_template, request, abort, flash, redirect, json, escape
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.secret_key = '2d9-E2.)f&é,A$p@fpa+zSU03êû9_'
Bootstrap(app)

from biblioapp import db, tools

global arduino_id
arduino_id = db.get_arduino_id()

@app.route("/")
@app.route('/<arduino_id>/')
def home():
    tidybooks = db.get_tidybooks(arduino_id) #books with addresses
    bookstorange = db.get_bookstorange(arduino_id) #books with position
    #print(books)
    return render_template('index.html',arduino_id=arduino_id, tidybooks=tidybooks, bookstorange=bookstorange)

@app.route('/book/<book_id>')
def getBook(book_id):
    book = db.get_book(book_id)
    if book:
        address = db.get_position(book['id'])
        return render_template('book.html',book=book,address=address,arduino_id=arduino_id)
    abort(404)

@app.route('/locate/', methods=['GET', 'POST'])
def locateBook():
    if request.method == 'POST':
      test = db.set_request(request)
      flash('Location requested for book {}'.format(request.form['book_id']))
      return redirect('/')


#Perform request for current arduino_id
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
    if request.form['isbn']:
      query += "ISBN:\""+request.form['isbn']+"\"&"
    if request.form['inauthor']:
      query += "inauthor:"+request.form['inauthor']+"+"
    if request.form['intitle']:
      query += "intitle:"+request.form['intitle']
    url = "https://www.googleapis.com/books/v1/volumes?"+query
    r = requests.get(url)
    data = r.json()
    #print(data['items'])
    return render_template('booksearch.html',data=data, isbn=request.form['isbn'], inauthor=request.form['inauthor'], intitle=request.form['intitle'])
  '''get detail on api'''
  if request.method == 'GET' and request.args.get('ref'):
    ref = request.args.get('ref')
    r = requests.get("https://www.googleapis.com/books/v1/volumes/"+ref)
    data = r.json()
    #print(data['volumeInfo'])
    return render_template('booksearch.html',bookapi=data, ref=ref)
  else:
    return render_template('booksearch.html')

@app.route('/bookreferencer/', methods=['POST'])
def bookReferencer():
  if request.method == 'POST':
    tagIds = db.set_tags(request.form.getlist('tags[]'))
    bookapi={}
    bookapi['author'] = ', '.join(request.form.getlist('authors[]'))
    bookapi['title'] = request.form['title']
    bookapi['reference'] = request.form['reference']
    bookapi['isbn'] = request.form['isbn']
    bookapi['description'] = request.form['description']
    bookapi['editor'] = request.form['editor']
    bookapi['pages'] = request.form['pages']
    bookapi['year'] = request.form['year']
    bookId = db.set_book(bookapi)
    if bookId and tagIds:
      db.set_tag_node(bookId, tagIds)
  return render_template('bookreferencer.html')
   
if __name__ == "__main__":
    app.run(debug=True)
