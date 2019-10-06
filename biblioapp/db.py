from flaskext.mysql import MySQL
import pymysql
from biblioapp import app

db = MySQL()

def get_db() :
	# MySQL configurations
	app.config['MYSQL_DATABASE_USER'] = 'manu'
	app.config['MYSQL_DATABASE_PASSWORD'] = 'mdp'
	app.config['MYSQL_DATABASE_DB'] = 'bibliobus'
	app.config['MYSQL_DATABASE_HOST'] = 'localhost'
	db.init_app(app)
	conn = db.connect()
	cursor = conn.cursor(pymysql.cursors.DictCursor)	
	return cursor

def get_arduino_id() :
    cursor = get_db()
    cursor.execute("SELECT id_arduino FROM biblio_app WHERE id=1")
    row = cursor.fetchone()
    if row:
      return row['id_arduino']
    return false

def get_book_address(arduino_id,id_address) :
  cursor = get_db()
  cursor.execute("SELECT * FROM biblio_address where id=%s",id_address)
  row = cursor.fetchone()
  if row:
    return row
  return false