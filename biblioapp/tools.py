from datetime import datetime
from biblioapp import app, hashlib, base64

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
    return decode
  except ValueError:
    return False

def set_token(email):
  return hashlib.md5(email.encode('utf-8')).hexdigest()

def set_id_ble(module):
  return "bibus"+"-"+str(module['id']).zfill(4)+"-"+str(module['nb_lines']).zfill(2)+""+str(module['nb_cols']).zfill(3)

def led_range(book, leds_interval):
  #compute interval with led strip spec
  leds_interval = leds_interval / 100 #convert mm to cm
  if book['width']!= None and book['width'] > 0:
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

      firstElem = positions[i-1]

      #store node ids inside 1 block
      if firstElem['id_node'] not in blockelem:
        blockelem.append(firstElem['id_node'])
      if pos['id_node'] not in blockelem:        
        blockelem.append(pos['id_node'])

      #remove block first element from isolated list
      if firstElem['id_node'] in uniqelem:
        uniqelem.remove(firstElem['id_node'])

      #build block element : get first position and agragate intervals
      cpt+=1
      blockend += firstElem['interval']
      if cpt==1:
        block = {'action':action, 'row':pos['row'], 'index':i, 'start':firstElem['led_column'], 'color':pos['color'],}
      block.update({'interval':blockend+pos['interval'], 'nodes':blockelem})

      #populate blocks list
      if block not in blocks:
        blocks.append(block)
        
    #reinit for next block
    else:

      block = {}
      blockelem = []
      blockend = 0
      cpt = 0

      #store isolated elements
      uniqelem.append(pos['id_node'])
  
  #loop 2 : build response for isolated elements
  for i, pos in enumerate(positions): 
    for id_node in uniqelem:
      if id_node == pos['id_node']:
        blocks.append({'action':action, 'row':pos['row'], 'index':i, 'start':pos['led_column'], \
          'color':pos['color'], 'interval':pos['interval'], 'nodes':[id_node]})

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

def formatBookApi(api, data, isbn):
  bookapi = {}

  if api == 'localform':
    authors = data.getlist('authors[]')
    bookapi['authors'] = authors
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
    bookapi['author'] = ', '.join(authors)
    bookapi['title'] = data['volumeInfo']['title']
    if 'subtitle' in data['volumeInfo']:
      bookapi['title'] += ' - '+data['volumeInfo']['subtitle']
    bookapi['reference'] = data['id']
    bookapi['isbn'] = isbn
    bookapi['editor'] = data['volumeInfo']['publisher'] if 'publisher' in data['volumeInfo'] else ""
    bookapi['description'] = data['volumeInfo']['description'] if 'description' in data['volumeInfo'] else ""
    bookapi['pages'] = data['volumeInfo']['pageCount'] if 'pageCount' in data['volumeInfo'] else 0
    bookapi['year'] = getYear(data['volumeInfo']['publishedDate']) if 'publishedDate' in data['volumeInfo'] else "" 

  return bookapi  