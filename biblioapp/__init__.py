from flask import Flask, render_template, request, abort, flash, redirect

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
    
if __name__ == "__main__":
    app.run(debug=True)
