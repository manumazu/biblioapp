from pyduino import *
import time, requests

def getRequest():
    url='http://127.0.0.1:5000/request/'
    r = requests.get(url)
    data = r.json()
    return data

if __name__ == '__main__':

    json = getRequest()
    
    a = Arduino()
    # if your arduino was running on a serial port other than '/dev/ttyACM0/'
    # declare: a = Arduino(serial_port='/dev/ttyXXXX')

    time.sleep(3)
    # sleep to ensure ample time for computer to make serial connection 

    a.serial_write('putain de merde')
    a.serial_read()

    '''PIN = 3
    a.set_pin_mode(PIN,'O')
    # initialize the digital pin as output

    time.sleep(1)
    # allow time to make connection

    for i in range(0,1000):
        if i%2 == 0:    
            a.digital_write(PIN,1) # turn LED on 
        else:
            a.digital_write(PIN,0) # turn LED off
        time.sleep(1)'''