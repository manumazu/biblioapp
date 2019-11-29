#======================================

# THE DEMO PROGRAM STARTS HERE

#======================================

import serial, requests

from ComArduino2 import *

url='https://bibliobus.bearstech.com/request/'
r = requests.get(url)
datas = r.json()

testData = []
for data in datas:
  msg = "<LED%d,%d000,0.2>" % (data['column'],data['column'])
  testData.append(msg)

# NOTE the user must ensure that the serial port and baudrate are correct
# serPort = "/dev/ttyS80"
serPort = "/dev/ttyACM0"
baudRate = 9600

conn = serial.Serial(serPort, baudRate)
print ("Serial port " + serPort + " opened  Baudrate " + str(baudRate))

waitForArduino(conn)

runTest(conn, testData)

conn.close



'''testData = []
testData.append("<LED1,100,0.2>")
testData.append("<LED2,200,0.7>")
testData.append("<LED3,300,0.5>")
testData.append("<LED1,1000,0.2>")
testData.append("<LED2,1500,0.7>")
testData.append("<LED3,3000,0.7>")'''
