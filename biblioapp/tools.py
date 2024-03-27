from flask import session, flash
from datetime import datetime
from biblioapp import create_app, db, hashlib, base64
from unidecode import unidecode
import flask_login
import re

app = create_app()

def initApp():
  user_login = False
  arduino_map = None
  arduino_name = None  
  if(flask_login.current_user.is_authenticated):
    user_login = flask_login.current_user.name  
    #prevent empty session for module : select first one
    if 'app_id' not in session:
      modules = db.get_arduino_for_user(flask_login.current_user.id) 
      if modules:   
        for module in modules:
          session['app_id'] = module['id']
          session['app_name'] = module['arduino_name']
          flash('Bookshelf "{}"selected'.format(module['arduino_name']), 'info')
          break
    if 'app_id' in session and session['app_id'] != None:
      arduino_map = db.get_arduino_map(flask_login.current_user.id, session['app_id'])
      if arduino_map != None:
        arduino_name = arduino_map['arduino_name']            
  return {'user_login':user_login,'arduino_map':arduino_map,'arduino_name':arduino_name}

def getYear(datestr):
  try:
    datepub = datetime.strptime(datestr,'%b %d, %Y')
    return datepub.year
  except ValueError:
    try:
      datepub = datetime.strptime(datestr,'%B %d, %Y')
      return datepub.year
    except ValueError:
      try:
        datepub = datetime.strptime(datestr,'%Y-%m-%dT%H:%M:%S%z')
        return datepub.year
      except ValueError: 
        try:
          datepub = datetime.strptime(datestr,'%Y-%m-%d')
          return datepub.year
        except ValueError:
          return datestr

def getNow():
  return datetime.now()

def getLastnameFirstname(names):
  lnfn=[]
  for name in names:
    namearr = name.split(' ')
    if len(namearr)>1:
      lnfn.append(' '.join(namearr[::-1])) #reverse names array
    else:
      lnfn.append(namearr[0])
  return lnfn

def uuid_decode(encode):
  try:
    decode = base64.b64decode(encode)
    return decode.decode('utf-8')
  except ValueError:
    return False

def uuid_encode(string):
  try:
    encode = base64.b64encode(string.encode('utf-8'))
    return encode.decode('utf-8')
  except ValueError:
    return False    

#def set_token(email):
#  return hashlib.md5(email.encode('utf-8')).hexdigest()

def set_id_ble(module):
  return "bibus"+"-"+str(module['id']).zfill(4)+"-"+str(module['nb_lines']).zfill(2)+""+str(module['nb_cols']).zfill(3)

def led_range(book, leds_interval):
  #compute interval with led strip spec
  if book['width'] and book['width'] > 0:
    book_width = book['width'] / 10 #convert mm to cm
    lrange = round(book_width/leds_interval)
  #compute range with book nb of pages
  else:
    nb_pages =str(book['pages'])
    if nb_pages.strip() == '':
      lrange = 1
    elif int(nb_pages) < 200:
      lrange = 1
    elif int(nb_pages) > 1000:
      lrange = round(int(nb_pages)/400)
    else:
      lrange = round(int(nb_pages)/200)
  return lrange

@app.context_processor
def utility_processor():
    return dict(led_range=led_range)

'''build blocks of nearby positions :
agregate intervals and reduce messages to Arduino
'''
def build_block_position(positions, action):

  cpt = 0
  blockend = 0  
  block = {}
  blocks = []
  blockelem = []
  uniqelem = []

  #loop 1 : group nearby positions, and separate isolated postions 
  for i, pos in enumerate(positions): 

    #check if current pos is following the previous pos
    if int(pos['led_column']) == int(positions[i-1]['led_column'] + positions[i-1]['interval']) \
    and pos['color'] == positions[i-1]['color'] and pos['row'] == positions[i-1]['row'] : 

      prevItem = positions[i-1]

      #store node ids inside list
      if pos['id_node'] not in blockelem:        
        blockelem.append(pos['id_node'])

      #remove block first element from isolated list
      idx = prevItem['id_node'] if prevItem['id_node'] > 0 else (prevItem['row']+prevItem['led_column']+prevItem['interval'])
      if idx in uniqelem:
        uniqelem.remove(idx)

      #build block element : get first position and agragate intervals
      cpt+=1
      blockend += prevItem['interval']
      if cpt==1:
        block = {'action':action, 'row':pos['row'], 'index':i, 'start':prevItem['led_column'], \
        'color':pos['color'], 'id_tag':pos['id_tag'],}
      block.update({'interval':blockend+pos['interval'], 'nodes':blockelem, 'client':pos['client']})

      #populate blocks list
      if block not in blocks:
        blocks.append(block)
        
    #reinit for next block
    else:

      block = {}
      blockelem = []
      blockend = 0
      cpt = 0

      #store isolated elements: node_id for books, position for gaming
      idx = pos['id_node'] if pos['id_node'] > 0 else (pos['row']+pos['led_column']+pos['interval'])
      uniqelem.append(idx)
  
  #loop 2 : build response for isolated elements
  for i, pos in enumerate(positions):
    idx = pos['id_node'] if pos['id_node'] > 0 else (pos['row']+pos['led_column']+pos['interval'])
    for j in uniqelem:
      if j == idx:
        blocks.append({'action':action, 'row':pos['row'], 'index':i, 'start':pos['led_column'], \
          'id_tag':pos['id_tag'], 'color':pos['color'], 'interval':pos['interval'], \
          'nodes':[pos['id_node']], 'client':pos['client']})
  
  #print(blocks)

  #reset order for blocks:
  if(action=='remove'):
    blocks.sort(key=sortIndexBlocks, reverse=True)
  else:
    blocks.sort(key=sortIndexBlocks)

  return blocks

def sortIndexBlocks(elem):
  return elem['index'] 

def sortPositions(address):
  return address['row']*100+address['led_column']

def sortCoords(coords):
  return coords[0]

def match_words(words, string):
  w = unidecode(words).lower()
  s = unidecode(string).lower()
  # search words inside string
  compare = re.search("^"+re.escape(w), s, re.IGNORECASE)
  #print(compare)
  if compare and compare.start() == 0:
    return True
  return False

# search ocr book title and api search result title
def matchApiSearchResults(title, data, way):
  cpt = 0
  for item in data['items']:
    # test match on 2 sides
    #print(item['volumeInfo']['title'])
    if way == 'ocr-in-api':
      test = match_words(title, item['volumeInfo']['title'])
    if way == 'api-in-ocr':
      test = match_words(item['volumeInfo']['title'], title)
    # take the first matchting result only
    if test:
      cpt += 1
      if cpt == 1:
        searchedbook = formatBookApi('googleapis', item, None)
        return searchedbook
  return False

# Search books with open api
async def searchBookApi(query, api, ref = None):
  import requests
  if api == 'googleapis':
    url = "https://www.googleapis.com/books/v1/volumes?key="+app.config['GOOGLE_BOOK_API_KEY']+"&q="
  if api == 'openlibrary':
    url = "https://openlibrary.org/api/books?format=json&jscmd=data&bibkeys="
  if ref is not None:
    url = "https://www.googleapis.com/books/v1/volumes/"
    query = ref

  data = {}
  r = requests.get(url + query)
  data = r.json()
  #print(query)
  return data

def formatBookApi(api, data, isbn):
  bookapi = {}

  if api == 'localform':
    authors = data.getlist('authors[]')
    bookapi['authors'] = authors
    authors = authors[:3]
    bookapi['author'] = ', '.join(authors)
    bookapi['title'] = data['title']
    bookapi['reference'] = data['reference']
    bookapi['isbn'] = isbn
    bookapi['description'] = data['description']
    bookapi['editor'] = data['editor']
    bookapi['pages'] = data['pages']
    bookapi['year'] = data['year']
    if 'book_width' in data:
      bookapi['width'] = data['book_width']#round(float(data['book_width'])*10)
    else :
      bookapi['width'] = None

  if api == 'openlibrary':
    authors = []
    if 'authors' in data:
      for author in data['authors']:
        authors.append(author['name'])
    bookapi['authors'] = authors
    authors = authors[:3]
    bookapi['author'] = ', '.join(authors)
    bookapi['title'] = data['title']
    if 'subtitle' in data:
      bookapi['title'] += ' - '+data['subtitle']
    bookapi['reference'] = data['key']
    bookapi['isbn'] = isbn
    bookapi['editor'] = data['publishers'][0]['name'] if 'publishers' in data else ""
    bookapi['description'] = data['note'] if 'note' in data else ""
    bookapi['pages'] = data['number_of_pages'] if 'number_of_pages' in data else 0
    bookapi['year'] = getYear(data['publish_date']) if 'publish_date' in data else ""
    
  elif api == 'googleapis':
    authors = []
    if 'authors' in data['volumeInfo']:
      authors = data['volumeInfo']['authors']
    bookapi['authors'] = authors
    authors = authors[:3]
    bookapi['author'] = ', '.join(authors)
    bookapi['title'] = data['volumeInfo']['title']
    if 'subtitle' in data['volumeInfo']:
      bookapi['title'] += ' - '+data['volumeInfo']['subtitle']
    bookapi['reference'] = data['id']
    if isbn is not None:
      bookapi['isbn'] = isbn
    else:
      if 'industryIdentifiers' in data['volumeInfo']:
        for Ids in data['volumeInfo']['industryIdentifiers']:
          if Ids['type'] == "ISBN_13":
            bookapi['isbn'] = Ids['identifier']
    bookapi['editor'] = data['volumeInfo']['publisher'] if 'publisher' in data['volumeInfo'] else ""
    bookapi['description'] = data['volumeInfo']['description'] if 'description' in data['volumeInfo'] else ""
    bookapi['pages'] = data['volumeInfo']['pageCount'] if 'pageCount' in data['volumeInfo'] else 0
    bookapi['year'] = getYear(data['volumeInfo']['publishedDate']) if 'publishedDate' in data['volumeInfo'] else ""
    if 'dimensions' in data['volumeInfo'] and 'thickness' in data['volumeInfo']['dimensions']:
      width = data['volumeInfo']['dimensions']['thickness']
      converter = 10 if width.find('cm') else 1 # convert dimension from cm to mm
      bookapi['width'] = str2int(width)*converter

  return bookapi

def str2int(str):
  import re
  res = re.findall(r'\b\d+\b', str)
  if len(res):
    return float(".".join(res))
  return False

def get_leds_effects():
  return [ 'rainbow', 'rainbowWithGlitter', 'confetti', 'sinelon' , 'juggle', 'bpm', 'snowSparkle', 'fadeOut' ]


def seconds_between_now(d1):
    #d1 = datetime.strptime(str(d1), "%Y-%m-%d %H:%M:%S")
    d2 = getNow()
    return abs((d2 - d1).seconds)

def drawline(line, x, y, xoffset, nb_leds, color):
  leds = {}
  dy = int(y+line)-1; #y must be > 0
  maxled = (dy * nb_leds) + (x + xoffset) #XY(x+xoffset, dy);
  for j in range(maxled-xoffset):
    leds[j] = color;
  return leds

def allowed_file(filename):
  return '.' in filename and \
    filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

