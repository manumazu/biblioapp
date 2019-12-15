from flaskext.mysql import MySQL
import pymysql
from biblioapp import app
from biblioapp import tools

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

def get_app_for_uuid(uuid) :
  cursor = get_db()
  cursor.execute("SELECT id_arduino FROM biblio_app WHERE uuid=%s",uuid)
  row = cursor.fetchone()
  cursor.close()
  if row:
    return row

def get_tidy_books(arduino_id, line = None) :
  cursor = get_db()
  if line == None:
    where = "app.id_arduino=%s"
    args = arduino_id
  else:
    where = "app.id_arduino=%s and bp.row=%s"
    args = (arduino_id,line)
  cursor.execute("SELECT bb.id, bb.title, bb.author, bp.position, bp.row FROM biblio_book bb \
	inner join biblio_position bp on bp.id_item=bb.id and bp.item_type='book'\
	inner join biblio_app app on bp.id_app=app.id\
	where "+ where +" order by row, position",args)
  rows = cursor.fetchall()
  cursor.close()
  from collections import defaultdict
  books = defaultdict(dict)
  for row in rows:
    books[row['row']][row['position']]={'id':row['id'], 'title':row['title'], 'author':row['author'], 'url':'/book/'+str(row['id'])}
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

def get_request(arduino_id) :
  cursor = get_db()
  cursor.execute("SELECT * FROM biblio_request where id_arduino=%s",arduino_id)
  row = cursor.fetchall()
  cursor.close()
  if row:
    return row
  return False

def get_request_for_position(arduino_id, position, row) :
  cursor = get_db()
  cursor.execute("SELECT * FROM biblio_request where id_arduino=%s and `column`=%s and `row`=%s",(arduino_id, position, row))
  row = cursor.fetchone()
  cursor.close()
  if row:
    return row
  return False  

def set_request(request) :
  now = tools.getNow()
  cursor = get_db()
  cursor.execute("INSERT INTO biblio_request (`id_arduino`, `row`, `column`, `range`) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE `date_add`=%s, `range`=%s", \
  (request.form.get('arduino_id'), request.form.get('row'), request.form.get('column'), request.form.get('range'), \
  now.strftime("%Y-%m-%d %H:%M:%S"), request.form.get('range')))
  conn.commit()
  cursor.close()
  return True

def del_request(arduino_id, column, row) :
  cursor = get_db()
  cursor.execute("DELETE FROM biblio_request where id_arduino=%s and `column`=%s and `row`=%s",(arduino_id, column,row))
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

''' manage items position '''
def get_position_for_book(book_id) :
  cursor = get_db()
  cursor.execute("SELECT * FROM biblio_position where id_app=1 and id_item=%s and item_type='book'",book_id)
  row = cursor.fetchone()
  cursor.close()
  if row:
    return row
  return False

def get_positions_for_row(row) :
  cursor = get_db()
  cursor.execute("SELECT id_item FROM biblio_position where id_app=%s and `row`=%s order by `position`",(1, row))
  row = cursor.fetchall()
  cursor.close()
  if row:
    return row
  return False


def sort_items(items, row) :
  cursor = get_db()
  i=0
  sortable={}
  for item in items :
    if 'id_item' in item:
      item_id=item['id_item']
    else:
      item_id=item
    i+=1
    cursor.execute("INSERT INTO biblio_position (`id_app`, `id_item`, `item_type`, `position`, `row`) VALUES (%s, %s, %s, %s, %s) \
    ON DUPLICATE KEY UPDATE position=%s, row=%s", (1, item_id, 'book', i, row , i, row))
    conn.commit()
    sortable[i]={'book':item_id,'position':i}
  cursor.close()
  return sortable

'''
manage position suppression for one item
- check current postion
- check and delete requested postion on arduino
- decrement remaining positions
- delete current position
'''
def del_item_position(item, arduino_id) :
  position = get_position_for_book(item[1])
  if position:
    cursor = get_db()
    cursor.execute("DELETE FROM biblio_position WHERE `id_item`=%s and `item_type`=%s and `id_app`=1", (item[1], item[0]))
    conn.commit()
    cursor.close()
  has_request = get_request_for_position(arduino_id, position['position'], position['row'])
  #remove request
  if has_request:
    del_request(arduino_id, position['position'], position['row'])
  #get list for remaining items and sort them again
  items = get_positions_for_row(position['row'])
  sort_items(items, position['row'])
  return True

''' manage taxonomy '''
def get_tag_for_node(id_node):
  cursor = get_db()
  cursor.execute("SELECT id, tag FROM biblio_tags bt INNER JOIN biblio_tag_node btn ON bt.id = btn.id_tag WHERE btn.id_node=%s", id_node)
  row = cursor.fetchall()
  cursor.close()
  if row:
    return row
  return False

def get_node_for_tag(id_tag):
  cursor = get_db()
  cursor.execute("SELECT id_node FROM biblio_tag_node btn INNER JOIN biblio_tags bt ON bt.id = btn.id_tag WHERE btn.id_tag=%s and btn.node_type='book'", id_tag)
  row = cursor.fetchall()
  cursor.close()
  if row:
    return row
  return False

def get_author(letter):
  cursor = get_db()
  searchLetter = letter+"%"
  cursor.execute("SELECT id, tag FROM `biblio_tags` WHERE id_taxonomy=2 and tag like %s", searchLetter)
  row = cursor.fetchall()
  cursor.close()
  if row:
    return row
  return False

def get_tag(tag):
  cursor = get_db()
  cursor.execute("SELECT id, tag FROM biblio_tags WHERE tag=%s", tag)
  row = cursor.fetchone()
  cursor.close()
  if row:
    return row
  return False

def get_tag_by_id(tag_id):
  cursor = get_db()
  cursor.execute("SELECT id, tag FROM biblio_tags WHERE id=%s", tag_id)
  row = cursor.fetchone()
  cursor.close()
  if row:
    return row
  return False  

def get_id_taxonomy(label):
  cursor = get_db()
  cursor.execute("SELECT id, label FROM biblio_taxonomy WHERE label=%s", label)
  row = cursor.fetchone()
  cursor.close()
  if row:
    return row
  return False

def set_tags(tags, taxonomy_label):
  tag_ids = []
  taxonomy = get_id_taxonomy(taxonomy_label)
  for tag in tags:
    hasTag = get_tag(tag)
    if hasTag is False:
      cursor = get_db()
      cursor.execute("INSERT INTO biblio_tags (`tag`, `id_taxonomy`) VALUES (%s, %s)", (tag, taxonomy['id']))
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
