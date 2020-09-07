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
  mysql['cursor'].execute("SELECT * FROM biblio_app WHERE id_ble=%s",(uuid))
  row = mysql['cursor'].fetchone()
  mysql['cursor'].close()
  mysql['conn'].close()
  if row:
    return row

def get_user_for_uuid(uuid):
  mysql = get_db()
  mysql['cursor'].execute("SELECT bu.id, bu.email, bu.password, bu.firstname, ba.id as id_app, ba.arduino_name FROM biblio_user bu \
    INNER JOIN biblio_user_app bua ON bu.id = bua.id_user \
    INNER JOIN biblio_app ba ON bua.id_app = ba.id WHERE (ba.id_ble=%s)", (uuid))
  row = mysql['cursor'].fetchone()
  mysql['cursor'].close()
  mysql['conn'].close()
  if row:
    return row
  return None

def get_module(id) :
  mysql = get_db()
  mysql['cursor'].execute("SELECT ba.*, bua.id_user FROM biblio_app ba \
    INNER JOIN biblio_user_app bua ON bua.id_app = ba.id WHERE ba.id=%s",(id))
  row = mysql['cursor'].fetchone()
  mysql['cursor'].close()
  mysql['conn'].close()
  if row:
    return row   

def set_module(data) :
  module={}
  if 'module_id' in data:
    mysql = get_db()
    #user mode
    if 'action' in data and data['action']=='user_edit':
      mysql['cursor'].execute("UPDATE biblio_app SET arduino_name=%s, mood_color=%s WHERE id=%s", \
        (data['module_name'], data['mood_color'], data['module_id']))
    #admin mode
    if 'action' in data and data['action']=='admin':
      mysql['cursor'].execute("UPDATE biblio_app SET arduino_name=%s, `id_ble`=%s, `nb_lines`=%s, `nb_cols`=%s, \
        `leds_interval`=%s, `strip_length`=%s WHERE id=%s", (data['module_name'], data['id_ble'], data['nb_lines'], data['nb_cols'], \
          data['leds_interval'], data['strip_length'], data['module_id']))
    mysql['conn'].commit()
    mysql['cursor'].close()
    mysql['conn'].close()
    module['id'] = data['module_id']
  else:
    mysql = get_db()
    mysql['cursor'].execute("INSERT INTO biblio_app (`arduino_name`, `id_ble`, `nb_lines`, `nb_cols`, `leds_interval`, \
      `strip_length`) VALUES (%s, %s, %s, %s, %s, %s)", (data['module_name'], data['id_ble'], data['nb_lines'], \
      data['nb_cols'], data['leds_interval'], data['strip_length']))
    mysql['conn'].commit()
    mysql['cursor'].execute("SELECT LAST_INSERT_ID() as id")
    module = mysql['cursor'].fetchone()
    mysql['cursor'].close()
    mysql['conn'].close()
  return module 

def update_id_ble(module_id, id_ble) : 
  mysql = get_db()
  mysql['cursor'].execute("UPDATE biblio_app SET id_ble=%s WHERE id=%s", (id_ble, module_id))
  mysql['conn'].commit()
  mysql['cursor'].close()
  mysql['conn'].close() 

def set_user_app(id_user, id_app) :
  mysql = get_db()
  mysql['cursor'].execute("INSERT INTO biblio_user_app (`id_user`, `id_app`) VALUES (%s, %s) \
    ON DUPLICATE KEY UPDATE `id_user`=%s", (id_user, id_app, id_user))
  mysql['conn'].commit()
  mysql['cursor'].close()
  #print(mysql['cursor']._last_executed)
  mysql['conn'].close() 

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
  mysql['cursor'].execute("SELECT bb.`id`, bb.`title`, bb.`author`, bp.`position`, bp.`range`, bp.`row`, bp.`item_type`, bp.`led_column`,\
  bp.`borrowed` FROM biblio_book bb inner join biblio_position bp on bp.id_item=bb.id and bp.item_type='book'\
  inner join biblio_app app on bp.id_app=app.id where app.id=%s and bp.row=%s order by row, led_column",(app_id,numrow))  
  rows = mysql['cursor'].fetchall()
  mysql['cursor'].close()
  mysql['conn'].close()
  if rows:
    return rows

def get_books_to_range(user_id) :
  mysql = get_db()
  mysql['cursor'].execute("SELECT bb.* FROM biblio_book bb \
  left join `biblio_tag_node` btn on bb.id =  btn.id_node and btn.node_type='book' \
  left join `biblio_tags` bt on btn.id_tag =  bt.id and bt.id_taxonomy=2 \
	left join biblio_position bp on bp.id_item=bb.id and bp.item_type='book' \
	where bp.id_item is null and bb.id_user=%s group by bb.id order by bt.tag", int(user_id))
  rows = mysql['cursor'].fetchall()
  mysql['cursor'].close()
  mysql['conn'].close()
  if rows:
    return rows

#qty books by row for module
def stats_books(app_id, rownum):
  mysql = get_db()
  mysql['cursor'].execute("SELECT bp.`row`, count(bb.`id`) as nbbooks FROM biblio_book bb \
  inner join biblio_position bp on bp.id_item=bb.id and bp.item_type='book' \
  inner join biblio_app app on bp.id_app=app.id where app.id=%s and bp.`row`=%s", (app_id, rownum))
  row = mysql['cursor'].fetchone()
  mysql['cursor'].close()
  mysql['conn'].close()
  if row:
    return row  

def get_book(book_id, user_id) :
  mysql = get_db()
  mysql['cursor'].execute("SELECT * FROM biblio_book where id=%s and id_user=%s",(book_id, user_id))
  row = mysql['cursor'].fetchone()
  mysql['cursor'].close()
  mysql['conn'].close()
  if row:
    return row

def del_book(book_id, user_id) :
  mysql = get_db()
  mysql['cursor'].execute("DELETE FROM biblio_book where id=%s and id_user=%s",(book_id, user_id))
  mysql['conn'].commit()
  mysql['cursor'].close()
  mysql['conn'].close()

def get_request(app_id, action) :
  mysql = get_db()
  mysql['cursor'].execute("SELECT * FROM biblio_request where id_app=%s and `action`=%s",(app_id, action))
  row = mysql['cursor'].fetchall()
  mysql['cursor'].close()
  mysql['conn'].close()
  if row:
    return row
  return False

def get_request_for_mobile(app_id, action, sent) :
  mysql = get_db()
  mysql['cursor'].execute("SELECT * FROM biblio_request where id_app=%s and `action`=%s and `sent`=%s and `client`='server'",\
    (app_id, action, sent))
  row = mysql['cursor'].fetchall()
  mysql['cursor'].close()
  mysql['conn'].close()
  if row:
    return row
  return False  

def get_request_for_position(app_id, position, row) :
  mysql = get_db()
  mysql['cursor'].execute("SELECT * FROM biblio_request where id_app=%s and `column`=%s and `row`=%s \
    and `action`='add'", (app_id, position, row))
  row = mysql['cursor'].fetchone()
  mysql['cursor'].close()
  mysql['conn'].close()
  if row:
    return row
  return False 

def get_request_for_tag(app_id, tag_id) :
  mysql = get_db()
  mysql['cursor'].execute("SELECT * FROM biblio_request where id_app=%s and `id_tag`=%s \
    and `action`='add'", (app_id, tag_id))
  row = mysql['cursor'].fetchone()
  mysql['cursor'].close()
  mysql['conn'].close()
  if row:
    return row
  return False   

def set_request(app_id, node_id, row, column, interval, led_column, node_type, client, action, tag_id = None, color = None) :
  now = tools.getNow()
  mysql = get_db()
  mysql['cursor'].execute("INSERT INTO biblio_request (`id_app`, `id_node`, `node_type`, `row`, `column`, `range`, \
    `led_column`, `client`, `action`, `id_tag`, `color`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
    ON DUPLICATE KEY UPDATE `date_add`=%s, `range`=%s, `led_column`=%s, `client`=%s, `action`=%s", (app_id, node_id, node_type,\
     row, column, interval, led_column, client, action, tag_id, color, now.strftime("%Y-%m-%d %H:%M:%S"), interval, led_column, \
     client, action))
  mysql['conn'].commit()
  mysql['cursor'].close()
  mysql['conn'].close()
  return True

def set_request_sent(app_id, node_id, sent) :
  mysql = get_db()
  mysql['cursor'].execute("UPDATE biblio_request SET `sent`=%s WHERE `id_app`=%s and `id_node`=%s \
    and `node_type` in ('book', 'static')", (sent, app_id, node_id))
  mysql['conn'].commit()
  mysql['cursor'].close()
  mysql['conn'].close()
  return True

def del_request(app_id, led_column, row) :
  mysql = get_db()
  mysql['cursor'].execute("DELETE FROM biblio_request where id_app=%s and `led_column`=%s and `row`=%s",(app_id, led_column,row)) 
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

def set_request_remove(app_id) :
  now = tools.getNow()
  mysql = get_db()
  mysql['cursor'].execute("UPDATE biblio_request SET `action`='remove', `client`='mobile', `date_add`=%s WHERE `id_app`=%s \
    and action='add'", (now.strftime("%Y-%m-%d %H:%M:%S"), app_id))
  mysql['conn'].commit()
  mysql['cursor'].close()
  mysql['conn'].close()
  return True  


''' manage book '''
def get_bookapi(isbn, user_id):
  mysql = get_db()
  mysql['cursor'].execute("SELECT id FROM biblio_book WHERE `isbn`=%s and `id_user`=%s", (isbn, user_id))
  row = mysql['cursor'].fetchone()
  mysql['cursor'].close()
  mysql['conn'].close()
  if row:
    return row
  return False

def set_book(bookapi, user_id) :
  hasBook = {}
  if 'id' in bookapi:
    mysql = get_db()
    mysql['cursor'].execute("UPDATE biblio_book SET `isbn`=%s, `title`=%s, `author`=%s, `editor`=%s, `year`=%s, `pages`=%s, `reference`=%s, \
    `description`=%s, `width`=%s  WHERE id=%s", (bookapi['isbn'], bookapi['title'].strip(), bookapi['author'], bookapi['editor'], bookapi['year'], \
    bookapi['pages'], bookapi['reference'], bookapi['description'], bookapi['width'], bookapi['id']))
    mysql['conn'].commit()
    mysql['cursor'].close()
    mysql['conn'].close()
    hasBook['id'] = bookapi['id']    
  else:
    mysql = get_db()
    mysql['cursor'].execute("INSERT INTO biblio_book (`id_user`, `isbn`, `title`, `author`, `editor`, `year`, `pages`, \
      `reference`, `description`, `width`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (user_id, bookapi['isbn'], \
        bookapi['title'].strip(), bookapi['author'], bookapi['editor'], bookapi['year'], bookapi['pages'], bookapi['reference'], \
        bookapi['description'], bookapi['width']))
    mysql['conn'].commit()
    mysql['cursor'].execute("SELECT LAST_INSERT_ID() as id")
    hasBook = mysql['cursor'].fetchone()
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
  mysql['cursor'].execute("SELECT id_item FROM biblio_position where id_app=%s and `row`=%s \
    and `item_type`<>'static' order by `position`",(app_id, row))
  row = mysql['cursor'].fetchall()
  mysql['cursor'].close()
  mysql['conn'].close()
  if row:
    return row
  return False

#positions taken by row for module
def stats_positions(app_id, rownum):
  mysql = get_db()
  mysql['cursor'].execute("SELECT bp.`row`, sum(bp.range) as totpos FROM biblio_position bp \
  inner join biblio_app app on bp.id_app=app.id \
  where app.id=%s and bp.`row`=%s", (app_id, rownum))#item_type='book' and inner join biblio_book bb on bb.id=bp.id_item \ 
  #print(mysql['cursor']._last_executed)
  row = mysql['cursor'].fetchone()
  mysql['cursor'].close()
  mysql['conn'].close()
  if row:
    return row 

def get_borrowed_books(app_id):
  mysql = get_db()
  mysql['cursor'].execute("SELECT * FROM biblio_position bp WHERE bp.id_app=%s and bp.item_type='book' and bp.borrowed = 1", \
    (app_id))
  row = mysql['cursor'].fetchall()
  mysql['cursor'].close()
  mysql['conn'].close()
  if row:
    return row
  return False

def set_borrow_book(app_id, item_id, mode) :
  if mode == 'add':
    borrowed = 1
  if mode == 'remove':
    borrowed = 0
  mysql = get_db()
  mysql['cursor'].execute("UPDATE biblio_position SET borrowed=%s WHERE id_item=%s and id_app=%s", (borrowed, item_id, app_id))
  mysql['conn'].commit()
  mysql['cursor'].close()
  mysql['conn'].close()
  return True

def sort_items(app_id, user_id, items, row, leds_interval) :
  i=0
  sortable=[] 
  for item in items :
    if 'id_item' in item:
      item_id=item['id_item']
    else:
      item_id=item     
    if item_id is not None:
      position = get_position_for_book(app_id, item_id)
      if position:
        interval = position['range'] 
      else:
        book = get_book(item_id, user_id)
        interval = tools.led_range(book, leds_interval)
    i+=1
    led_column = set_position(app_id, item_id, i, row, interval, 'book')
    sortable.append({'book':item_id, 'position':i, 'fulfillment':int(led_column+interval), 'shelf':row})
  return sortable

def set_position(app_id, item_id, position, row, interval, item_type, led_column = None) :
  if(led_column is None):
    led_column = get_led_column(app_id, item_id, row, position)
  mysql = get_db()
  mysql['cursor'].execute("INSERT INTO biblio_position (`id_app`, `id_item`, `item_type`, \
      `position`, `row`, `range`, `led_column`) VALUES (%s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY \
      UPDATE position=%s, row=%s, `range`=%s, `led_column`=%s", \
      (app_id, item_id, item_type, position, row, interval, led_column, position, row, interval, led_column))
  mysql['conn'].commit()
  mysql['cursor'].close()
  mysql['conn'].close()
  #print(mysql['cursor']._last_executed)
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
  mysql['cursor'].execute("SELECT `led_column`, `range`, position, item_type FROM `biblio_position` \
    WHERE item_type='static' AND id_app=%s AND `row`=%s ORDER BY `position`", (app_id, row))
  row = mysql['cursor'].fetchall()
  mysql['cursor'].close()
  mysql['conn'].close()
  if row:
    return row
  return False

def del_item_position(app_id, item_id, item_type, numrow) :
  mysql = get_db()
  mysql['cursor'].execute("DELETE FROM biblio_position WHERE `id_item`=%s and `item_type`=%s and `id_app`=%s and `row`=%s", \
    (item_id, item_type, app_id, numrow))
  mysql['conn'].commit()
  mysql['cursor'].close()
  mysql['conn'].close()
  #print(mysql['cursor']._last_executed)    
  return True

#get address for max position in all rows
def get_last_saved_position(id_app):
  mysql = get_db()
  mysql['cursor'].execute("SELECT * FROM `biblio_position` WHERE id_app = %s and item_type='book' and \
    position in (SELECT max(position) FROM `biblio_position` WHERE id_app = %s and item_type='book' GROUP by row) \
    ORDER BY row DESC LIMIT 1", (id_app, id_app));
  row = mysql['cursor'].fetchone()
  mysql['cursor'].close()
  mysql['conn'].close()
  if row:
    return row
  return False

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

def get_categories_for_app(id_user, id_app):
  mysql = get_db()
  mysql['cursor'].execute("SELECT bt.id, bt.tag, btu.color, count(bb.id) as nbnode FROM `biblio_tags` bt \
    INNER JOIN biblio_tag_node btn ON bt.id = btn.id_tag \
    INNER JOIN biblio_tag_user btu ON btn.id_tag = btu.id_tag \
    INNER JOIN biblio_book bb ON btn.id_node = bb.id \
    INNER JOIN biblio_position bp ON bb.id = bp.id_item and bp.item_type='book'\
    WHERE bt.id_taxonomy=1 and bp.id_app=%s and btu.id_user=%s GROUP BY bt.id ORDER BY bt.tag", (id_user, id_app))
  #print(mysql['cursor']._last_executed)
  row = mysql['cursor'].fetchall()
  mysql['cursor'].close()
  mysql['conn'].close()
  if row:
    return row
  return False  

def get_categories_for_user(id_user):
  mysql = get_db()
  mysql['cursor'].execute("SELECT bt.id, bt.tag, btu.color, count(bb.id) as nbnode FROM `biblio_tags` bt \
    INNER JOIN biblio_tag_node btn ON bt.id = btn.id_tag \
    INNER JOIN biblio_tag_user btu ON btn.id_tag = btu.id_tag \
    INNER JOIN biblio_book bb ON btn.id_node = bb.id \
    WHERE bt.id_taxonomy=1 and bb.id_user=%s and btu.id_user=%s GROUP BY bt.id ORDER BY bt.tag", (id_user, id_user))
  #print(mysql['cursor']._last_executed)
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
  mysql['cursor'].execute("SELECT id, tag, color FROM biblio_tags WHERE tag=%s", tag)
  row = mysql['cursor'].fetchone()
  mysql['cursor'].close()
  mysql['conn'].close()
  if row:
    return row
  return False

def set_color_for_tag(id_user, id_tag, color):
  mysql = get_db()
  mysql['cursor'].execute("UPDATE biblio_tag_user SET color=%s WHERE id_tag=%s and id_user=%s", (color, id_tag, id_user))
  mysql['conn'].commit()
  mysql['cursor'].close()
  mysql['conn'].close()
  return True

def get_tag_by_id(tag_id, user_id):
  mysql = get_db()
  mysql['cursor'].execute("SELECT bt.id, bt.tag, btu.color, bt.id_taxonomy FROM biblio_tags bt \
    LEFT JOIN biblio_tag_user btu ON bt.id = btu.id_tag and btu.id_user=%s \
    WHERE id=%s", (user_id, tag_id))
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

def set_tag_user(user_id, tagIds):
  mysql = get_db()
  #print(tagIds)
  for tag in tagIds:
    mysql['cursor'].execute("INSERT INTO biblio_tag_user (`id_user`, `id_tag`) VALUES (%s, %s) ON DUPLICATE KEY UPDATE id_tag=%s", \
    (user_id, tag['id'], tag['id']))
    mysql['conn'].commit()
  mysql['cursor'].close()
  mysql['conn'].close()  

def get_user(email):
  mysql = get_db()
  mysql['cursor'].execute("SELECT id, email, password, firstname FROM biblio_user WHERE email=%s", email)
  row = mysql['cursor'].fetchone()
  mysql['cursor'].close()
  mysql['conn'].close()
  if row:
    return row
  return None

def set_user(email, firstname, lastname, password):
  mysql = get_db()
  mysql['cursor'].execute("INSERT INTO biblio_user (email, firstname, lastname, password) VALUES (%s, %s, %s, %s)", \
    (email, firstname, lastname, password))
  mysql['conn'].commit()
  mysql['cursor'].execute("SELECT LAST_INSERT_ID() as id")
  user = mysql['cursor'].fetchone()   
  mysql['cursor'].close()
  mysql['conn'].close()
  if user:
    return user
  return None  

def set_user_pwd(email, password):
  mysql = get_db()
  mysql['cursor'].execute("UPDATE biblio_user SET password = %s WHERE email = %s", (password, email))
  mysql['conn'].commit()
  mysql['cursor'].close()
  mysql['conn'].close()

def set_customcode(user_id, app_id, code_id, title, description, published, customvars, customcode) :
  now = tools.getNow()
  mysql = get_db()
  if code_id is None :
    #get last position
    position = get_max_code_position(user_id, app_id)
    if position['maxpos'] is not None and position['maxpos']>0:
      position = position['maxpos']+1
    else:
      position = 0
    mysql['cursor'].execute("INSERT INTO biblio_customcode (`id_app`, `id_user`, `title`, `description`, `published`, \
      `customvars`, `customcode`, `position`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (app_id, user_id, title, description, \
        published, customvars, customcode, position))
  else :
    mysql['cursor'].execute("UPDATE biblio_customcode SET `id_app`=%s, `title`=%s, `description`=%s, `published`=%s, \
      `customvars`=%s, `customcode`=%s, `date_upd`=%s WHERE id=%s", (app_id, title, description, published, customvars, customcode, \
        now.strftime("%Y-%m-%d %H:%M:%S"), code_id))
  mysql['conn'].commit()
  mysql['cursor'].close()
  mysql['conn'].close()
  return True

def get_customcode(user_id, app_id, code_id) :
  mysql = get_db()
  mysql['cursor'].execute("SELECT * FROM biblio_customcode where id_user=%s and id_app=%s and id=%s", \
    (user_id, app_id, code_id))
  row = mysql['cursor'].fetchone()
  mysql['cursor'].close()
  mysql['conn'].close()
  if row:
    return row
  return False

def del_customcode(code_id, user_id):
  mysql = get_db()
  mysql['cursor'].execute("DELETE FROM biblio_customcode where id=%s and id_user=%s",(code_id, user_id))
  mysql['conn'].commit()
  mysql['cursor'].close()
  mysql['conn'].close()

def get_customcodes(user_id, app_id, published_only = False) :
  mysql = get_db()
  if published_only == True :
    mysql['cursor'].execute("SELECT id, title, description, customvars, date_add, date_upd, published FROM biblio_customcode \
    where id_user=%s and id_app=%s and published=1 order by `position`", (user_id, app_id))    
  else :
    mysql['cursor'].execute("SELECT id, title, description, customvars, date_add, date_upd, published FROM biblio_customcode \
    where id_user=%s and id_app=%s order by `position`", (user_id, app_id))
  row = mysql['cursor'].fetchall()
  mysql['cursor'].close()
  mysql['conn'].close()
  if row:
    return row
  return False

def get_max_code_position(user_id, app_id):
  mysql = get_db()
  mysql['cursor'].execute("SELECT max(position) as maxpos FROM `biblio_customcode` WHERE id_app=%s and published=1", (app_id))
  res = mysql['cursor'].fetchone()
  mysql['cursor'].close()
  mysql['conn'].close()
  if res:
    return res
  return False

def set_code_position(app_id, code_id, position):
  mysql = get_db()
  mysql['cursor'].execute("UPDATE biblio_customcode SET `position`=%s WHERE `id`=%s and `id_app`=%s", \
    (position, code_id, app_id))
  mysql['conn'].commit()
  mysql['cursor'].close()
  mysql['conn'].close()
  return True  

def sort_customcodes(user_id, app_id, codes) :
  i=0
  sortable={} 
  for code in codes :
    i+=1
    set_code_position(app_id, code, i)
    sortable[i]={'code':code,'position':i}
  return sortable

def search_book(app_id, keyword) :
  searchTerm = "%"+keyword+"%"
  mysql = get_db()
  mysql['cursor'].execute("SELECT id, title, author FROM biblio_search where id_app=%s and \
    (author like %s or title like %s or tags like %s)", (app_id, searchTerm, searchTerm, searchTerm))
  row = mysql['cursor'].fetchall()
  mysql['cursor'].close()
  mysql['conn'].close()
  if row:
    return row
  return False