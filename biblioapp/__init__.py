from flask import Flask, render_template, request, abort
from flaskext.mysql import MySQL

app = Flask(__name__)

from biblioapp import db

cursor = db.get_db()

@app.route("/")
def home():
    return "Hello, World!"

@app.route('/book/<book_id>')
def getBook(book_id):
    cursor.execute("SELECT * FROM biblio_book where id=%s",book_id)
    row = cursor.fetchone()
    if row:
        return render_template('book.html',book=row)
    #while row is not None:
    #    return row[2]
    abort(404)
    
if __name__ == "__main__":
    app.run(debug=True)