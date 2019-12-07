#======================================

# THE DEMO PROGRAM STARTS HERE

#======================================

import pexpect, time, requests

url='https://bibliobus.bearstech.com/request/'
r = requests.get(url)
datas = r.json()

testData = []
initStr = teststr = ' '.join(hex(ord(x)) for x in '<0>')
testData.append(initStr)
if datas:
  for data in datas:
    msg = "<%d,%d000,0.2>" % (data['column'],data['column'])
    teststr = ' '.join(hex(ord(x)) for x in msg)
    testData.append(teststr)

serverMACAddress = '4C:24:98:E6:99:DB' #HC08

child = pexpect.spawn('bluetoothctl')
child.sendline('connect '+serverMACAddress)
time.sleep(.5)
child.sendline('menu gatt')
time.sleep(.5)
child.sendline('select-attribute 0000ffe1-0000-1000-8000-00805f9b34fb')
time.sleep(1)
for data in testData:
   child.sendline('write "'+data+'"')
time.sleep(.5)
child.sendline('back')
child.sendline('disconnect '+serverMACAddress)
time.sleep(.5)
child.sendline('exit')




'''testData = []
testData.append("<LED1,100,0.2>")
testData.append("<LED2,200,0.7>")
testData.append("<LED3,300,0.5>")
testData.append("<LED1,1000,0.2>")
testData.append("<LED2,1500,0.7>")
testData.append("<LED3,3000,0.7>")'''
