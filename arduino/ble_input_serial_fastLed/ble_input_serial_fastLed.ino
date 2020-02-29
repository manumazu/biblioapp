#include <AltSoftSerial.h>
//#include <SoftwareSerial.h>
#include <FastLED.h>
AltSoftSerial softSerial; // (pin 8 = RX, pin 9 = TX)
//SoftwareSerial softSerial(8, 9); 

// Declare our NeoPixel strip object:
#define DATA_PIN    5
#define NUM_LEDS 62
CRGB leds[NUM_LEDS];

const byte buffSize = 40;
char inputBuffer[buffSize];
const char startMarker = '<';
const char endMarker = '>';
byte bytesRecvd = 0;
boolean readInProgress = false;
boolean newDataFromSerial = false;

byte ledStatus = 1;  // for light or not leds
int buttonState = 0;        // current state of the button
int lastButtonState = 0;    // previous state of the button
int buttonPush = 0;         // counter

int pinReset = 12;
int newLedColumn = 0;
int newLedRow = 0;
int newLedInterval = 0;

int red = -1;
int green = -1;
int blue = -1;

char messageFromSerial[buffSize] = {0};

unsigned long curMillis;

unsigned long prevReplyToPCmillis = 0;
unsigned long replyToPCinterval = 1000;

//=============

void setup() {
  Serial.begin(9600);
  softSerial.begin(9600);

  FastLED.addLeds<NEOPIXEL, DATA_PIN>(leds, NUM_LEDS);
  FastLED.setBrightness(50);
  //FastLED.setMaxPowerInVoltsAndMilliamps(5, 500);
  FastLED.clear(true);

  // declare the reset pin as an input
  pinMode(pinReset, INPUT);
  
  // tell the PC we are ready
  Serial.println("<Arduino is ready>");
}

//=============

void loop() {

  //manage satus for leds :
  //1 = wait for request
  //2 = switch off all leds
  //3 = switch on all leds
  buttonState = digitalRead(pinReset);
  if (buttonState != lastButtonState) {
    if (buttonState == HIGH) {
      buttonPush++;
      
      if(buttonPush>2)
        buttonPush=1;
          
      if (buttonPush == 1) { //force all ledstatus on
        ledStatus = 3;
      }
      if (buttonPush == 2) { //force all ledstatus off
        ledStatus = 2;
      }
      
      //send messages in buffer to serial BLE
      /*for (byte n = 0; n < NUM_LEDS; n++) {
           if(leds[n]) 
           {
              String doc = "{\"row\":"+String(newLedRow)+",\"col\":"+String(n+1)+"}";
              Serial.println(doc);
              softSerial.println(doc);
              delay(10);
           }
      }*/
      
      
    }
    //Serial.println(ledStatus);
  }
  lastButtonState = buttonState;
  
  curMillis = millis();
  getDataFromSerial(); 
  replyToPC();
  lightLEDs();   
}

//============

void lightLEDs() {

  if (ledStatus==1 && readInProgress==false) { 
     if(newLedRow==0) {//for reset action
      ledStatus=false;
     }
     else {
       //@todo : remove test for row=1
       if(newLedRow==1)
       {
          if(newLedInterval <= 0) {//switch off
            for (int i=newLedColumn; i<(newLedColumn-newLedInterval); i++) { //light off given line
              leds[i] = CRGB::Black;
            }
          }
          else {
            FastLED.setBrightness(50);
            for (int i=newLedColumn; i<(newLedColumn+newLedInterval); i++) { //light on given line
              if(red >=0)
                leds[i] = CRGB(red,green,blue);//::Blue;//DarkBlue;
              else
                leds[i] = CRGB::Blue;
            }
          }
          FastLED.show();
          delay(120);
       }
    }
  }
  if (ledStatus==0){
     FastLED.clear(); // soft reset clear OFF all strip
  }
  if (ledStatus == 2) { // hard reset
      FastLED.show();
      ledStatus = 0; 
  }
  if (ledStatus==3){ // display colors for all

      /*for (byte n = 0; n < NUM_LEDS; n++) {
           if(leds[n]) 
           {
              String doc = "{\"row\":"+String(newLedRow)+",\"led\":"+String(-n+1)+"}";//\"action\":"+String(ledStatus)+",
              //Serial.println(doc);
              softSerial.println(doc);
              delay(100);
           }
      }*/
    FastLED.setBrightness(70);      
    fill_solid(leds, NUM_LEDS, CRGB(78,32,9));//::Brown);
    FastLED.show();
    //FastLED.clear();
    ledStatus = 0; 
  }
}

//=============

void getDataFromSerial() {

    // receive data from PC and save it into inputBuffer
    
  if(softSerial.available() > 0) {

    ledStatus = 1; // force led status when request

    char x = softSerial.read();
    //Serial.write(softSerial.read());

    // the order of these IF clauses is significant
      
    if (x == endMarker) {
      readInProgress = false;
      newDataFromSerial = true;
      inputBuffer[bytesRecvd] = 0;
      parseData();
    }
    
    if(readInProgress) {
      inputBuffer[bytesRecvd] = x;
      bytesRecvd ++;
      if (bytesRecvd == buffSize) {
        bytesRecvd = buffSize - 1;
      }
    }

    if (x == startMarker) { 
      bytesRecvd = 0; 
      readInProgress = true;
    }
  }
}

//=============
 
void parseData() {

    // split the data into its parts
    
  char * strtokIndx; // this is used by strtok() as an index
  
  strtokIndx = strtok(inputBuffer,",");      // get the first part - the string  
  newLedRow = atoi(strtokIndx);

  strtokIndx = strtok(NULL, ","); // this continues where the previous call left off 
  strcpy(messageFromSerial, strtokIndx); // copy it to messageFromSerial    
  newLedColumn = atoi(strtokIndx);     // convert this part to an integer
  
  strtokIndx = strtok(NULL, ","); // this continues where the previous call left off
  newLedInterval = atoi(strtokIndx);     // convert this part to an integer

  strtokIndx = strtok(NULL, ","); // set red value
  red = atoi(strtokIndx);
  strtokIndx = strtok(NULL, ","); // set green value
  green = atoi(strtokIndx);   
  strtokIndx = strtok(NULL, ","); // set blue value
  blue = atoi(strtokIndx);   

}

//=============

void replyToPC() {

  if (newDataFromSerial) {    
    newDataFromSerial = false;
    Serial.print("<Position ");
    Serial.print(newLedColumn);
    Serial.print(" ledInterval ");
    Serial.print(newLedInterval);
    Serial.print(" bytesRecvd ");
    Serial.print(bytesRecvd);
    Serial.print(" Time ");
    Serial.print(curMillis >> 9); // divide by 512 is approx = half-seconds
    Serial.println(">");
  }
}
