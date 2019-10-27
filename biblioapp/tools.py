from datetime import datetime

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