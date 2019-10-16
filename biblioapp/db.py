from flaskext.mysql import MySQL
import pymysql
from biblioapp import app
from datetime import datetime

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

def get_request(arduino_id) :
  cursor = get_db()
  cursor.execute("SELECT * FROM biblio_request where id_arduino=%s",arduino_id)
  row = cursor.fetchone()
  cursor.close()
  if row:
    return row
  return False

def set_request(request) :
  now = datetime.now()
  cursor = get_db()
  cursor.execute("INSERT INTO biblio_request (`id_arduino`, `row`, `column`, `range`) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE date_add=%s", \
  (request.form.get('arduino_id'), request.form.get('row'), request.form.get('column'), request.form.get('range'), \
  now.strftime("%Y-%m-%d %H:%M:%S")))
  conn.commit()
  cursor.close()
  return True

def close_conn() :
    conn.close()
