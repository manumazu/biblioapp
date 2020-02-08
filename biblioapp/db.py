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
  mysql['cursor'].execute("SELECT id, arduino_name FROM biblio_app WHERE id_ble=%s",(uuid))
  row = mysql['cursor'].fetchone()
  mysql['cursor'].close()
  mysql['conn'].close()
  if row:
    return row

def get_user_for_uuid(uuid):
  mysql = get_db()
  mysql['cursor'].execute("SELECT bu.id, bu.email, bu.password, bu.name, ba.id as id_app, ba.arduino_name FROM biblio_user bu \
    INNER JOIN biblio_user_app bua ON bu.id = bua.id_user \
    INNER JOIN biblio_app ba ON bua.id_app = ba.id WHERE (ba.id_ble=%s)", (uuid))
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
  mysql['cursor'].execute("SELECT bb.`id`, bb.`title`, bb.`author`, bp.`position`, bp.`row`, bp.`item_type`, bp.`led_column`\
  FROM biblio_book bb inner join biblio_position bp on bp.id_item=bb.id and bp.item_type='book'\
	inner join biblio_app app on bp.id_app=app.id where "+ where +" order by row, led_column",args)
  rows = mysql['cursor'].fetchall()
  mysql['cursor'].close()
  mysql['conn'].close()
  from collections import defaultdict
  books = defaultdict(dict)
  for row in rows:
    books[row['row']][row['led_column']]={'item_type':row['item_type'],'id':row['id'], \
    'title':row['title'], 'author':row['author'], 'position':row['position'], 'url':'/book/'+str(row['id'])}
  #add static elements
  #statics = get_static_elements(app_id)
  #for static in statics:
  #  books[static['row']].append([static['led_column']]={'item_type':static['item_type'],'id':None, 'position':row['position']})
  if rows:
    #sorted_dict = sorted(books, key=lambda x: int(books[x][0]))
    return books

def get_books_for_row(app_id, numrow) :
  mysql = get_db()
  mysql['cursor'].execute("SELECT bb.`id`, bb.`title`, bb.`author`, bp.`position`, bp.`row`, bp.`item_type`, bp.`led_column`\
  FROM biblio_book bb inner join biblio_position bp on bp.id_item=bb.id and bp.item_type='book'\
  inner join biblio_app app on bp.id_app=app.id where app.id=%s and bp.row=%s order by row, led_column",(app_id,numrow))  
  rows = mysql['cursor'].fetchall()
  mysql['cursor'].close()
  mysql['conn'].close()
  if rows:
    return rows

def get_books_to_range(user_id) :
  mysql = get_db()
  mysql['cursor'].execute("SELECT * FROM biblio_book bb \
	left join biblio_position bp on bp.id_item=bb.id and bp.item_type='book' \
	where bp.id_item is null order by bb.author, bb.title and bb.id_user=%s", int(user_id))
  rows = mysql['cursor'].fetchall()
  mysql['cursor'].close()
  mysql['conn'].close()
  if rows:
    return rows

def get_static_elements(app_id, numrow) :
  mysql = get_db()
  mysql['cursor'].execute("SELECT * FROM biblio_position bp WHERE bp.item_type='static' \
  and bp.id_app=%s and bp.row=%s order by bp.led_column", (int(app_id),numrow))
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

def set_request(app_id, row, column, interval, led_column) :
  now = tools.getNow()
  mysql = get_db()
  mysql['cursor'].execute("INSERT INTO biblio_request (`id_app`, `row`, `column`, `range`, `led_column`) \
    VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE `date_add`=%s, `range`=%s, `led_column`=%s",  \
  (app_id, row, column, interval, led_column, now.strftime("%Y-%m-%d %H:%M:%S"), interval, led_column))
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

'''
manage position suppression for one item
- compute sum of intervals for setting physical position
- check current position
- check and delete requested position on arduino
- decrement remaining positions
- delete current position
'''  

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


def sort_items(app_id, user_id, items, row) :
  mysql = get_db()
  i=0
  sortable={}
  for item in items :
    if 'id_item' in item:
      item_id=item['id_item']
    else:
      item_id=item
    position = get_position_for_book(app_id, item_id)
    if position:
      interval = position['range'] 
    else:
      book = get_book(item_id, user_id)
      interval = tools.led_range(book['pages'])
    i+=1
    set_position(app_id, item_id, i, row, interval)
    sortable[i]={'book':item_id,'position':i}
  mysql['cursor'].close()
  mysql['conn'].close()
  return sortable

def set_position(app_id, item_id, position, row, interval) :
  led_column = get_led_column(app_id, item_id, row, position)
  mysql = get_db()
  mysql['cursor'].execute("INSERT INTO biblio_position (`id_app`, `id_item`, `item_type`, \
      `position`, `row`, `range`, `led_column`) VALUES (%s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY \
      UPDATE position=%s, row=%s, `range`=%s, `led_column`=%s", \
      (app_id, item_id, 'book', position, row, interval, led_column, position, row, interval, led_column))
  mysql['conn'].commit()
  mysql['cursor'].close()
  mysql['conn'].close()
  return led_column

'''compute sum of intervals for setting physical position'''
def get_led_column(app_id, item_id, row, column) :
  mysql = get_db()
  mysql['cursor'].execute("SELECT sum(`range`) as `column` FROM `biblio_position` \
    WHERE `position`<%s  and id_app=%s and `row`=%s and id_item <> %s and item_type='book'",(column, app_id, row, item_id))
  res = mysql['cursor'].fetchone()
  mysql['cursor'].close()
  mysql['conn'].close()
  #check for static columns to shift book's real position 
  statics = get_static_positions(app_id, row)
  if res['column'] is not None:
    if statics:
      for static in statics:
        if res['column'] >= static['led_column']:
          res['column'] += static['range']
    return res['column']
  return int(0)

def get_static_positions(app_id, row):
  mysql = get_db()
  mysql['cursor'].execute("SELECT `led_column`, `range` FROM `biblio_position` \
    WHERE item_type='static' AND id_app=%s AND `row`=%s ORDER BY `position`", (app_id, row))
  row = mysql['cursor'].fetchall()
  mysql['cursor'].close()
  mysql['conn'].close()
  if row:
    return row
  return False

def del_item_position(app_id, item, user_id) :
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
    sort_items(app_id, user_id, items, position['row'])
  return True

''' manage taxonomy '''
def get_tag_for_node(id_node, id_taxonomy):
  mysql = get_db()
  mysql['cursor'].execute("SELECT id, tag FROM biblio_tags bt \
    INNER JOIN biblio_tag_node btn ON bt.id = btn.id_tag WHERE btn.id_node=%s and bt.id_taxonomy=%s", (id_node,id_taxonomy))
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

def get_categories_for_user(id_user):
  mysql = get_db()
  mysql['cursor'].execute("SELECT bt.id, bt.tag, count(bb.id) as nbnode FROM `biblio_tags` bt \
    INNER JOIN biblio_tag_node btn ON bt.id = btn.id_tag \
    INNER JOIN biblio_book bb ON btn.id_node = bb.id \
    WHERE bt.id_taxonomy=1 and bb.id_user=%s GROUP BY bt.id ORDER BY bt.tag", id_user)
  row = mysql['cursor'].fetchall()
  mysql['cursor'].close()
  mysql['conn'].close()
  if row:
    return row
  return False

def get_categories_for_term(term):
  mysql = get_db()
  searchTerm = term+"%"
  mysql['cursor'].execute("SELECT bt.tag FROM `biblio_tags` bt \
    WHERE bt.id_taxonomy=1 and bt.tag like %s", searchTerm)
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

def get_authors_for_app(id_app, letter):
  mysql = get_db()
  searchLetter = letter+"%"
  mysql['cursor'].execute("SELECT bt.id, bt.tag, count(bb.id) as nbnode FROM `biblio_tags` bt \
    INNER JOIN biblio_tag_node btn ON bt.id = btn.id_tag \
    INNER JOIN biblio_book bb ON btn.id_node = bb.id \
    INNER JOIN biblio_position bp ON bb.id = bp.id_item and bp.item_type='book' \
    WHERE bt.id_taxonomy=2 and bp.id_app=%s and bt.tag like %s GROUP BY bt.id ORDER BY bt.tag", (id_app, searchLetter))
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

def clean_tag_for_node(id_node, id_taxonomy):
  mysql = get_db()
  mysql['cursor'].execute("DELETE tn.* FROM biblio_tag_node tn LEFT JOIN biblio_tags t ON tn.id_tag = t.id \
      WHERE tn.id_node=%s and t.id_taxonomy=%s and tn.node_type='book'", (id_node, id_taxonomy))
  mysql['conn'].commit()
  mysql['cursor'].close()
  mysql['conn'].close()


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
 
