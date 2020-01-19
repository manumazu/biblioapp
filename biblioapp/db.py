from flaskext.mysql import MySQL
import pymysql
from biblioapp import app
from biblioapp import tools

db = MySQL()
db.init_app(app)

def get_db() :
  conn = db.connect()
  cursor = conn.cursor(pymysql.cursors.DictCursor)	
  return {'conn':conn,'cursor':cursor}

def get_arduino_map(user_email, app_id):
  mysql = get_db()
  mysql['cursor'].execute("SELECT ba.*, bu.id as user_id FROM biblio_app ba \
    INNER JOIN biblio_user_app bua ON bua.id_app = ba.id \
    INNER JOIN biblio_user bu ON bu.id=bua.id_user \
    WHERE bu.email=%s and ba.id=%s", (user_email, app_id))
  row = mysql['cursor'].fetchone()
  mysql['cursor'].close()
  mysql['conn'].close()
  if row:
    return row

def get_arduino_for_user(user_email):
  mysql = get_db()
  mysql['cursor'].execute("SELECT ba.*, bu.id as user_id FROM biblio_app ba \
    INNER JOIN biblio_user_app bua ON bua.id_app = ba.id \
    INNER JOIN biblio_user bu ON bu.id=bua.id_user \
    WHERE bu.email=%s", user_email)
  row = mysql['cursor'].fetchall()
  mysql['cursor'].close()
  mysql['conn'].close()
  if row:
    return row    

def get_app_for_uuid(uuid) :
  mysql = get_db()
  mysql['cursor'].execute("SELECT id, arduino_name FROM biblio_app WHERE id_ble=%s or mac=%s",(uuid,uuid))
  row = mysql['cursor'].fetchone()
  mysql['cursor'].close()
  mysql['conn'].close()
  if row:
    return row

def get_user_for_uuid(uuid):
  mysql = get_db()
  mysql['cursor'].execute("SELECT bu.id, bu.email, bu.password, bu.name, ba.id as id_app, ba.arduino_name FROM biblio_user bu \
    INNER JOIN biblio_user_app bua ON bu.id = bua.id_user \
    INNER JOIN biblio_app ba ON bua.id_app = ba.id WHERE (ba.id_ble=%s OR ba.mac=%s)", (uuid,uuid))
  row = mysql['cursor'].fetchone()
  mysql['cursor'].close()
  mysql['conn'].close()
  if row:
    return row
  return None    

def get_tidy_books(app_id, line = None) :
  mysql = get_db()
  if line == None:
    where = "app.id=%s"
    args = app_id
  else:
    where = "app.id=%s and bp.row=%s"
    args = (app_id,line)
  mysql['cursor'].execute("SELECT bb.`id`, bb.`title`, bb.`author`, bp.`position`, bp.`row` FROM biblio_book bb \
	inner join biblio_position bp on bp.id_item=bb.id and bp.item_type='book'\
	inner join biblio_app app on bp.id_app=app.id\
	where "+ where +" order by row, position",args)
  rows = mysql['cursor'].fetchall()
  mysql['cursor'].close()
  mysql['conn'].close()
  from collections import defaultdict
  books = defaultdict(dict)
  for row in rows:
    books[row['row']][row['position']]={'id':row['id'], 'title':row['title'], 'author':row['author'], 'url':'/book/'+str(row['id'])}
  #print(books)
  if rows:
    return books

def get_books_to_range(user_id) :
  mysql = get_db()
  mysql['cursor'].execute("SELECT * FROM biblio_book bb \
	left join biblio_position bp on bp.id_item=bb.id and bp.item_type='book' \
	where bp.id_item is null order by bb.author, bb.title and bb.id_user=%s", user_id)
  rows = mysql['cursor'].fetchall()
  mysql['cursor'].close()
  mysql['conn'].close()
  if rows:
    return rows

def get_book(book_id, user_id) :
  mysql = get_db()
  mysql['cursor'].execute("SELECT * FROM biblio_book where id=%s and id_user=%s",(book_id, user_id))
  row = mysql['cursor'].fetchone()
  mysql['cursor'].close()
  mysql['conn'].close()
  if row:
    return row

def get_request(app_id) :
  mysql = get_db()
  mysql['cursor'].execute("SELECT * FROM biblio_request where id_app=%s",app_id)
  row = mysql['cursor'].fetchall()
  mysql['cursor'].close()
  mysql['conn'].close()
  if row:
    return row
  return False

def get_request_for_position(app_id, position, row) :
  mysql = get_db()
  mysql['cursor'].execute("SELECT * FROM biblio_request where id_app=%s and `column`=%s and `row`=%s",(app_id, position, row))
  row = mysql['cursor'].fetchone()
  mysql['cursor'].close()
  mysql['conn'].close()
  if row:
    return row
  return False  

def set_request(app_id, row, column, range) :
  now = tools.getNow()
  mysql = get_db()
  mysql['cursor'].execute("INSERT INTO biblio_request (`id_app`, `row`, `column`, `range`) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE `date_add`=%s, `range`=%s", \
  (app_id, row, column, range, now.strftime("%Y-%m-%d %H:%M:%S"), range))
  mysql['conn'].commit()
  mysql['cursor'].close()
  mysql['conn'].close()
  return True

def del_request(app_id, column, row) :
  mysql = get_db()
  mysql['cursor'].execute("DELETE FROM biblio_request where id_app=%s and `column`=%s and `row`=%s",(app_id, column,row))
  mysql['conn'].commit()
  mysql['cursor'].close()
  mysql['conn'].close()
  return True

def clean_request(app_id) :
  mysql = get_db()
  mysql['cursor'].execute("DELETE FROM biblio_request where id_app=%s",(app_id))
  mysql['conn'].commit()
  mysql['cursor'].close()
  mysql['conn'].close()
  return True


''' manage book '''
def get_bookapi(bookapi, user_id):
  mysql = get_db()
  mysql['cursor'].execute("SELECT id FROM biblio_book WHERE `reference`=%s and `id_user`=%s", (bookapi['reference'], user_id))
  row = mysql['cursor'].fetchone()
  mysql['cursor'].close()
  mysql['conn'].close()
  if row:
    return row
  return False

def set_book(bookapi, user_id) :
  hasBook = get_bookapi(bookapi, user_id)
  datepub = tools.getYear(bookapi['year'])
  if hasBook is False:
    mysql = get_db()
    mysql['cursor'].execute("INSERT INTO biblio_book (`id_user`, `isbn`, `title`, `author`, `editor`, `year`, `pages`, `reference`, `description`) \
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s )", (user_id, bookapi['isbn'], bookapi['title'].strip(), bookapi['author'], bookapi['editor'], datepub, \
    bookapi['pages'], bookapi['reference'], bookapi['description']))
    mysql['conn'].commit()
    mysql['cursor'].execute("SELECT LAST_INSERT_ID() as id")
    hasBook = mysql['cursor'].fetchone()
    mysql['cursor'].close()
    mysql['conn'].close()
  else:
    mysql = get_db()
    mysql['cursor'].execute("UPDATE biblio_book SET `isbn`=%s, `title`=%s, `author`=%s, `editor`=%s, `year`=%s, `pages`=%s, `reference`=%s, \
    `description`=%s WHERE id=%s", (bookapi['isbn'], bookapi['title'].strip(), bookapi['author'], bookapi['editor'], datepub, \
    bookapi['pages'], bookapi['reference'], bookapi['description'], hasBook['id']))
    mysql['conn'].commit()
    mysql['cursor'].close()
    mysql['conn'].close()
  return hasBook

''' manage items position '''
def get_position_for_book(app_id, book_id) :
  mysql = get_db()
  mysql['cursor'].execute("SELECT * FROM biblio_position where id_app=%s and id_item=%s and item_type='book'",(app_id, book_id))
  row = mysql['cursor'].fetchone()
  mysql['cursor'].close()
  mysql['conn'].close()
  if row:
    return row
  return False

def get_positions_for_row(app_id, row) :
  mysql = get_db()
  mysql['cursor'].execute("SELECT id_item FROM biblio_position where id_app=%s and `row`=%s order by `position`",(app_id, row))
  row = mysql['cursor'].fetchall()
  mysql['cursor'].close()
  mysql['conn'].close()
  if row:
    return row
  return False


def sort_items(app_id, items, row) :
  mysql = get_db()
  i=0
  sortable={}
  for item in items :
    if 'id_item' in item:
      item_id=item['id_item']
    else:
      item_id=item
    i+=1
    mysql['cursor'].execute("INSERT INTO biblio_position (`id_app`, `id_item`, `item_type`, `position`, `row`) VALUES (%s, %s, %s, %s, %s) \
    ON DUPLICATE KEY UPDATE position=%s, row=%s", (app_id, item_id, 'book', i, row , i, row))
    mysql['conn'].commit()
    sortable[i]={'book':item_id,'position':i}
  mysql['cursor'].close()
  mysql['conn'].close()
  return sortable

'''
manage position suppression for one item
- check current position
- check and delete requested postion on arduino
- decrement remaining positions
- delete current position
'''
def del_item_position(app_id, item) :
  position = get_position_for_book(app_id, item[1])
  if position:
    mysql = get_db()
    mysql['cursor'].execute("DELETE FROM biblio_position WHERE `id_item`=%s and `item_type`=%s and `id_app`=%s", (item[1], item[0], position['id_app']))
    mysql['conn'].commit()
    mysql['cursor'].close()
    mysql['conn'].close()
  has_request = get_request_for_position(app_id, position['position'], position['row'])
  #remove request
  if has_request:
    del_request(app_id, position['position'], position['row'])
  #get list for remaining items and sort them again
  items = get_positions_for_row(position['id_app'], position['row'])
  if items:
    sort_items(app_id, items, position['row'])
  return True

''' manage taxonomy '''
def get_tag_for_node(id_node):
  mysql = get_db()
  mysql['cursor'].execute("SELECT id, tag FROM biblio_tags bt \
    INNER JOIN biblio_tag_node btn ON bt.id = btn.id_tag WHERE btn.id_node=%s", id_node)
  row = mysql['cursor'].fetchall()
  mysql['cursor'].close()
  mysql['conn'].close()
  if row:
    return row
  return False

def get_node_for_tag(id_tag, id_user):
  mysql = get_db()
  mysql['cursor'].execute("SELECT id_node FROM biblio_tag_node btn \
    INNER JOIN biblio_tags bt ON bt.id = btn.id_tag \
    INNER JOIN biblio_book bb ON btn.id_node = bb.id \
    WHERE btn.id_tag=%s and btn.node_type='book' and bb.id_user=%s", (id_tag, id_user))
  row = mysql['cursor'].fetchall()
  mysql['cursor'].close()
  mysql['conn'].close()
  if row:
    return row
  return False

def get_categories(id_user):
  mysql = get_db()
  mysql['cursor'].execute("SELECT bt.id, bt.tag, count(bb.id) as nbnode FROM `biblio_tags` bt \
    INNER JOIN biblio_tag_node btn ON bt.id = btn.id_tag \
    INNER JOIN biblio_book bb ON btn.id_node = bb.id \
    WHERE bt.id_taxonomy=1 and bb.id_user=%s GROUP BY bt.id", id_user)
  row = mysql['cursor'].fetchall()
  mysql['cursor'].close()
  mysql['conn'].close()
  if row:
    return row
  return False

def get_authors_alphabetic(letter, id_user):
  mysql = get_db()
  searchLetter = letter+"%"
  mysql['cursor'].execute("SELECT bt.id, bt.tag, count(bb.id) as nbnode FROM `biblio_tags` bt \
    INNER JOIN biblio_tag_node btn ON bt.id = btn.id_tag \
    INNER JOIN biblio_book bb ON btn.id_node = bb.id \
    WHERE bt.id_taxonomy=2 and tag like %s and bb.id_user=%s GROUP BY bt.id", (searchLetter, id_user))
  row = mysql['cursor'].fetchall()
  mysql['cursor'].close()
  mysql['conn'].close()
  if row:
    return row
  return False

def get_authors_for_app(id_app):
  mysql = get_db()
  mysql['cursor'].execute("SELECT bt.id, bt.tag, count(bb.id) as nbnode FROM `biblio_tags` bt \
    INNER JOIN biblio_tag_node btn ON bt.id = btn.id_tag \
    INNER JOIN biblio_book bb ON btn.id_node = bb.id \
    INNER JOIN biblio_position bp ON bb.id = bp.id_item and bp.item_type='book' \
    WHERE bt.id_taxonomy=2 and bp.id_app=%s GROUP BY bt.id ORDER BY bt.tag", id_app)
  row = mysql['cursor'].fetchall()
  mysql['cursor'].close()
  mysql['conn'].close()
  if row:
    return row
  return False

def get_tag(tag):
  mysql = get_db()
  mysql['cursor'].execute("SELECT id, tag FROM biblio_tags WHERE tag=%s", tag)
  row = mysql['cursor'].fetchone()
  mysql['cursor'].close()
  mysql['conn'].close()
  if row:
    return row
  return False

def get_tag_by_id(tag_id):
  mysql = get_db()
  mysql['cursor'].execute("SELECT id, tag FROM biblio_tags WHERE id=%s", tag_id)
  row = mysql['cursor'].fetchone()
  mysql['cursor'].close()
  mysql['conn'].close()
  if row:
    return row
  return False  

def get_id_taxonomy(label):
  mysql = get_db()
  mysql['cursor'].execute("SELECT id, label FROM biblio_taxonomy WHERE label=%s", label)
  row = mysql['cursor'].fetchone()
  mysql['cursor'].close()
  mysql['conn'].close()
  if row:
    return row
  return False

def set_tags(tags, taxonomy_label):
  tag_ids = []
  taxonomy = get_id_taxonomy(taxonomy_label)
  for tag in tags:
    hasTag = get_tag(tag)
    if hasTag is False:
      mysql = get_db()
      mysql['cursor'].execute("INSERT INTO biblio_tags (`tag`, `id_taxonomy`) VALUES (%s, %s)", (tag, taxonomy['id']))
      mysql['conn'].commit()
      mysql['cursor'].execute("SELECT LAST_INSERT_ID() as id")
      row = mysql['cursor'].fetchone()
      tag_ids.append(row)
      mysql['cursor'].close()
      mysql['conn'].close()
    else:
      tag_ids.append(hasTag)
  return tag_ids

def set_tag_node(node, tagIds):
  mysql = get_db()
  #print(node, tagIds)
  for tag in tagIds:
    mysql['cursor'].execute("INSERT INTO biblio_tag_node (`node_type`, `id_node`, `id_tag`) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE id_tag=%s", \
    ('book', node['id'], tag['id'], tag['id']))
    mysql['conn'].commit()
  mysql['cursor'].close()
  mysql['conn'].close()

def get_user(email):
  mysql = get_db()
  mysql['cursor'].execute("SELECT id, email, password, name FROM biblio_user WHERE email=%s", email)
  row = mysql['cursor'].fetchone()
  mysql['cursor'].close()
  mysql['conn'].close()
  if row:
    return row
  return None
 
