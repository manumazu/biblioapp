from datetime import datetime
from biblioapp import app, hashlib

def getYear(datestr):
  if len(datestr)>10:
    datepub = datetime.strptime(datestr,'%Y-%m-%dT%H:%M:%S%z')
    datepub = datepub.year
  elif len(datestr)==10:
    datepub = datetime.strptime(datestr,'%Y-%m-%d')
    datepub = datepub.year
  else:
    datepub = datestr
  return datepub

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

def set_token(email):
  return hashlib.md5(email.encode('utf-8')).hexdigest()

def led_range(nb_pages):
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
def build_block_position(positions):

  cpt = 0
  blockend = 0  
  block = {}
  blocks = []
  blockelem = []
  uniqelem = []

  for i, pos in enumerate(positions): 
    
    #check if current pos is following the previous pos
    if int(pos['led_column']) == int(positions[i-1]['led_column'] + positions[i-1]['interval']): 

      firstElem = positions[i-1]

      #store node ids inside 1 block
      if firstElem['id_node'] not in blockelem:
        blockelem.append(firstElem['id_node'])
      if pos['id_node'] not in blockelem:        
        blockelem.append(pos['id_node'])

      #remove block first element from isolated elements
      if firstElem['id_node'] in uniqelem:
        uniqelem.remove(firstElem['id_node'])

      #build block element : get first position and agragate intervals
      cpt+=1
      blockend += firstElem['interval']
      if cpt==1:
        block = {'row':pos['row'], 'start':firstElem['led_column']}
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
  
  print(uniqelem)   
  return blocks