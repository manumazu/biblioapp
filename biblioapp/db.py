from flaskext.mysql import MySQL
import pymysql
from biblioapp import app

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'manu'
app.config['MYSQL_DATABASE_PASSWORD'] = 'mdp'
app.config['MYSQL_DATABASE_DB'] = 'bibliobus'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

db = MySQL()
db.init_app(app)
conn = db.connect()

def get_db() :
  cursor = conn.cursor(pymysql.cursors.DictCursor)	
  return cursor

def get_arduino_id() :
    cursor = get_db()
    cursor.execute("SELECT id_arduino FROM biblio_app WHERE id=1")
    row = cursor.fetchone()
    cursor.close()
    if row:
      return row['id_arduino']

def get_books(arduino_id) :
  cursor = get_db()
  cursor.execute("SELECT * FROM biblio_book bb \
	left join biblio_address ba on bb.id_address=ba.id \
	inner join biblio_app app on ba.id_app=app.id \
	where app.id_arduino=%s",arduino_id)
  rows = cursor.fetchall()
  cursor.close()
  if rows:
    return rows

def get_book(book_id) :
  cursor = get_db()
  cursor.execute("SELECT * FROM biblio_book where id=%s",book_id)
  row = cursor.fetchone()
  cursor.close()
  if row:
    return row

def get_address(address_id) :
  cursor = get_db()
  cursor.execute("SELECT * FROM biblio_address where id=%s",address_id)
  row = cursor.fetchone()
  cursor.close()
  if row:
    return row

def close_conn() :
    conn.close()
