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
  row = cursor.fetchall()
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

''' manage book '''
def get_book(bookapi):
  cursor = get_db()
  cursor.execute("SELECT id FROM biblio_book WHERE `reference`=%s", bookapi['reference'])
  row = cursor.fetchone()
  cursor.close()
  if row:
    return row
  return False

def set_book(bookapi) :
  hasBook = get_book(bookapi)
  if hasBook is False:
    datepub = datetime.strptime(bookapi['year'],'%Y-%m-%dT%H:%M:%S+02:00')
    cursor = get_db()
    cursor.execute("INSERT INTO biblio_book (`isbn`, `title`, `author`, `editor`, `year`, `pages`, `reference`, `description`) \
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s )", (bookapi['isbn'], bookapi['title'], bookapi['author'], bookapi['editor'], datepub.year, \
    bookapi['pages'], bookapi['reference'], bookapi['description']))
    conn.commit()
    cursor.execute("SELECT LAST_INSERT_ID() as id")
    hasBook = cursor.fetchone()
    cursor.close()
  return hasBook

''' manage taxonomy '''
def get_tag(tag):
  cursor = get_db()
  cursor.execute("SELECT id, tag FROM biblio_tags WHERE tag=%s", tag)
  row = cursor.fetchone()
  cursor.close()
  if row:
    return row
  return False

def set_tags(tags):
  tag_ids = []
  for tag in tags:
    hasTag = get_tag(tag)
    tag_ids.append(hasTag)
    if hasTag is False:
      cursor = get_db()
      cursor.execute("INSERT INTO biblio_tags (`tag`) VALUES (%s)", tag)
      conn.commit()
      cursor.execute("SELECT LAST_INSERT_ID() as id")
      row = cursor.fetchone()
      tag_ids.append(row)
      cursor.close()
  return tag_ids

def close_conn() :
    conn.close()
