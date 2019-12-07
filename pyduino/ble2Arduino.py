#======================================

# THE DEMO PROGRAM STARTS HERE

#======================================

import pexpect, time, requests

#get requested position of items int app
url='https://bibliobus.bearstech.com/request/'
r = requests.get(url)
datas = r.json()

#manage hexadecimal conversion for position to send
testData = []
initStr = teststr = ' '.join(hex(ord(x)) for x in '<0>') #init <0> = "0x3c 0x30 0x3e"
testData.append(initStr)
if datas:
  for data in datas:
    msg = "<%d,%d000,0.2>" % (data['column'],data['column'])
    teststr = ' '.join(hex(ord(x)) for x in msg)
    testData.append(teststr)

#manage bluetoothctl wrapper
serverMACAddress = '4C:24:98:E6:99:DB' #HC08

child = pexpect.spawn('bluetoothctl')
child.sendline('connect '+serverMACAddress)
time.sleep(.5)
child.sendline('menu gatt') #search for UUID 0xFFE1
child.sendline('select-attribute 0000ffe1-0000-1000-8000-00805f9b34fb')
#time.sleep(0.5)
for data in testData:
   child.sendline('write "'+data+'"')
#time.sleep(.5)
child.sendline('back')
child.sendline('disconnect '+serverMACAddress)
child.sendline('exit')
