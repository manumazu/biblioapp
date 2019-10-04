from flask import Flask, render_template, request, abort, flash, redirect

app = Flask(__name__)
app.secret_key = '2d9-E2.)f&é,A$p@fpa+zSU03êû9_'

from biblioapp import db

cursor = db.get_db()

@app.route("/")
def home():
    return render_template('layout.html')

@app.route('/book/<book_id>')
def getBook(book_id):
    cursor.execute("SELECT * FROM biblio_book where id=%s",book_id)
    row = cursor.fetchone()
    if row:
        return render_template('book.html',book=row)
    abort(404)

@app.route('/locate/', methods=['GET', 'POST'])
def locateBook():
    if request.method == 'POST':
      flash('Location requested for book {}'.format(request.form['book_id']))
      return redirect('/')
    
    
if __name__ == "__main__":
    app.run(debug=True)