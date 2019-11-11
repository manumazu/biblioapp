from datetime import datetime
from biblioapp import app

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

@app.context_processor
def utility_processor():
    def led_range(nb_pages):
        if nb_pages.strip() == '':
          lrange = 2
        elif int(nb_pages) < 100:
          lrange = 1
        else:
          lrange = round(int(nb_pages)/100)
        return lrange
    return dict(led_range=led_range)