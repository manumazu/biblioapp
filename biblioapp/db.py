from flaskext.mysql import MySQL
import pymysql
from biblioapp import app
from biblioapp import tools

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

def get_arduino_map() :
    cursor = get_db()
    cursor.execute("SELECT * FROM biblio_app WHERE id=1")
    row = cursor.fetchone()
    cursor.close()
    if row:
      return row

def get_tidy_books(arduino_id) :
  cursor = get_db()
  cursor.execute("SELECT bb.id, bb.title, bb.author, bp.position, bp.row FROM biblio_book bb \
	inner join biblio_position bp on bp.id_item=bb.id and bp.item_type='book'\
	inner join biblio_app app on bp.id_app=app.id\
	where app.id_arduino=%s order by row, position",arduino_id)
  rows = cursor.fetchall()
  cursor.close()
  from collections import defaultdict
  books = defaultdict(dict)
  for row in rows:
    books[row['row']][row['position']]={'id':row['id'], 'title':row['title'], 'author':row['author']}
  #print(books)
  if rows:
    return books

def get_books_to_range(arduino_id) :
  #@todo : books without address are not linked with arduino id ! 
  cursor = get_db()
  cursor.execute("SELECT * FROM biblio_book bb \
	left join biblio_position bp on bp.id_item=bb.id and bp.item_type='book' \
	where bp.id_item is null order by bb.author, bb.title")
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

def get_position(book_id) :
  cursor = get_db()
  cursor.execute("SELECT * FROM biblio_position where id_item=%s and item_type='book'",book_id)
  row = cursor.fetchone()
  cursor.close()
  if row:
    return row
  return False

def get_request(arduino_id) :
  cursor = get_db()
  cursor.execute("SELECT * FROM biblio_request where id_arduino=%s",arduino_id)
  row = cursor.fetchall()
  cursor.close()
  if row:
    return row
  return False

def set_request(request) :
  now = tools.getNow()
  cursor = get_db()
  cursor.execute("INSERT INTO biblio_request (`id_arduino`, `row`, `column`, `range`) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE date_add=%s", \
  (request.form.get('arduino_id'), request.form.get('row'), request.form.get('column'), request.form.get('range'), \
  now.strftime("%Y-%m-%d %H:%M:%S")))
  conn.commit()
  cursor.close()
  return True

''' manage book '''
def get_bookapi(bookapi):
  cursor = get_db()
  cursor.execute("SELECT id FROM biblio_book WHERE `reference`=%s", bookapi['reference'])
  row = cursor.fetchone()
  cursor.close()
  if row:
    return row
  return False

def set_book(bookapi) :
  hasBook = get_bookapi(bookapi)
  datepub = tools.getYear(bookapi['year'])
  if hasBook is False:
    cursor = get_db()
    cursor.execute("INSERT INTO biblio_book (`isbn`, `title`, `author`, `editor`, `year`, `pages`, `reference`, `description`) \
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s )", (bookapi['isbn'], bookapi['title'].strip(), bookapi['author'], bookapi['editor'], datepub, \
    bookapi['pages'], bookapi['reference'], bookapi['description']))
    conn.commit()
    cursor.execute("SELECT LAST_INSERT_ID() as id")
    hasBook = cursor.fetchone()
    cursor.close()
  else:
    cursor = get_db()
    cursor.execute("UPDATE biblio_book SET `isbn`=%s, `title`=%s, `author`=%s, `editor`=%s, `year`=%s, `pages`=%s, `reference`=%s, \
    `description`=%s WHERE id=%s", (bookapi['isbn'], bookapi['title'].strip(), bookapi['author'], bookapi['editor'], datepub, \
    bookapi['pages'], bookapi['reference'], bookapi['description'], hasBook['id']))
    conn.commit()
    cursor.close()
  return hasBook

''' manage position '''
def sort_items(items, row) :
  cursor = get_db()
  i=0
  sortable={}
  for item_id in items :
    i+=1
    cursor.execute("INSERT INTO biblio_position (`id_app`, `id_item`, `item_type`, `position`, `row`) VALUES (%s, %s, %s, %s, %s) \
    ON DUPLICATE KEY UPDATE position=%s, row=%s", (1, item_id, 'book', i, row , i, row))
    conn.commit()
    sortable[i]={'book':item_id,'position':i}
  cursor.close()
  return sortable

def del_item_position(item) :
  cursor = get_db()
  cursor.execute("DELETE FROM biblio_position WHERE `id_item`=%s and `item_type`=%s and `id_app`=1", (item[1], item[0]))
  conn.commit()
  cursor.close()
  return True

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
    if hasTag is False:
      cursor = get_db()
      cursor.execute("INSERT INTO biblio_tags (`tag`) VALUES (%s)", tag)
      conn.commit()
      cursor.execute("SELECT LAST_INSERT_ID() as id")
      row = cursor.fetchone()
      tag_ids.append(row)
      cursor.close()
    else:
      tag_ids.append(hasTag)
  return tag_ids

def set_tag_node(node, tagIds):
  cursor = get_db()
  #print(node, tagIds)
  for tag in tagIds:
    cursor.execute("INSERT INTO biblio_tag_node (`node_type`, `id_node`, `id_tag`) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE id_tag=%s", \
    ('book', node['id'], tag['id'], tag['id']))
    conn.commit()
  cursor.close()

def close_conn() :
    conn.close()
