from flask import Flask, render_template, request, abort, flash, redirect, json

app = Flask(__name__)
app.secret_key = '2d9-E2.)f&é,A$p@fpa+zSU03êû9_'

from biblioapp import db

global arduino_id
arduino_id = db.get_arduino_id()

@app.route("/")
@app.route('/<arduino_id>/')
def home():
    books = db.get_books(arduino_id)
    return render_template('index.html',arduino_id=arduino_id, books=books)

@app.route('/book/<book_id>')
def getBook(book_id):
    book = db.get_book(book_id)
    if book:
        if book['id_address']:
          address = db.get_address(book['id_address'])
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

@app.route('/bookreferencer/', methods=['GET', 'POST'])
def searchBookReference():
  if request.method == 'POST' and request.form['isbn']:
    import requests
    #url = "https://openlibrary.org/api/books?bibkeys=ISBN:"+request.form['isbn'] 
    url = "https://www.googleapis.com/books/v1/volumes?q=ISBN:"+request.form['isbn']
    r = requests.get(url)
    data = json.loads(r.content)
    return render_template('bookreferencer.html',data=data, isbn=request.form['isbn'])
  else:
    return render_template('bookreferencer.html')
    
if __name__ == "__main__":
    app.run(debug=True)
