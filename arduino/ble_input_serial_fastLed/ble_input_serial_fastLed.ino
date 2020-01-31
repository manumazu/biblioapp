#include <AltSoftSerial.h>
//#include <SoftwareSerial.h>
#include <FastLED.h>
AltSoftSerial softSerial; // (pin 8 = RX, pin 9 = TX)
//SoftwareSerial softSerial(8, 9); 

// Declare our NeoPixel strip object:
#define DATA_PIN    5
#define NUM_LEDS 30
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

char messageFromSerial[buffSize] = {0};
int newLedInterval = 0;
//float servoFraction = 0.0; // fraction of servo range to move


unsigned long curMillis;

unsigned long prevReplyToPCmillis = 0;
unsigned long replyToPCinterval = 1000;

//=============

void setup() {
  Serial.begin(9600);
  softSerial.begin(9600);

  FastLED.addLeds<NEOPIXEL, DATA_PIN>(leds, NUM_LEDS);

  // declare the reset pin as an input
  pinMode(pinReset, INPUT);
  
  // tell the PC we are ready
  Serial.println("<Arduino is ready>");
}

//=============

void loop() {

  //manage satus for leds :
  //1 = wait for request
  //0 = switch off all leds
  //3 = switch on all leds
  buttonState = digitalRead(pinReset);
  if (buttonState != lastButtonState) {
    if (buttonState == HIGH) {
      buttonPush++;
      if(buttonPush>2)
        buttonPush=1;

      //send messages in buffer to serial BLE
      /*for (byte n = 0; n < numLEDs; n++) {
           if(digitalRead(ledPin[n])) 
           {
              String doc = "{\"row\":"+String(newLedRow)+",\"col\":"+String(n+1)+"}";
              Serial.println(doc);
              softSerial.println(doc);
              delay(10);
           }
      }*/
        
      newLedColumn = 0;//reset current led  
      if (buttonPush == 1) { //force ledstatus off
        ledStatus = 0;
      }
      if (buttonPush == 2) { //force all ledstatus on
        ledStatus = 3;
      }
      
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

  if (ledStatus==1) { 
     if(newLedColumn==0) {//when nothing is requested
      ledStatus=false;
     }
     else {
       if(newLedRow==1){//light only for row=1
        leds[newLedColumn-1] = CRGB::Blue; 
        FastLED.show(); 
        delay(90);
       }
    }
  }
  if (ledStatus==0){
      FastLED.clear(); // clear OFF all strip
  }
  if (ledStatus==3){
    /*for(int i=0; i<strip.numPixels(); i++) { // For each pixel in strip...
      strip.setPixelColor(i, strip.Color(255, 69, 0));//  Set pixel's color (in RAM) to BROWN
      strip.show();                          //  Update strip to match
      //delay(wait);                           //  Pause for a moment
    }*/
  }
}

//=============

void getDataFromSerial() {

    // receive data from PC and save it into inputBuffer
    
  if(softSerial.available() > 0) {//softSerial.available()

    ledStatus = 1; // force led status when request

    char x = softSerial.read();//softSerial.read()
    //Serial.write(softSerial.read());
    //softSerial.write(softSerial.read());

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
    
  //strtokIndx = strtok(NULL, ","); 
  //servoFraction = atof(strtokIndx);     // convert this part to a float

}

//=============

void replyToPC() {

  if (newDataFromSerial) {    
    ledStatus = true;
    newDataFromSerial = false;
    Serial.print("<Msg ");
    Serial.print(messageFromSerial);
    //Serial.print(" ledInterval ");
    //Serial.print(newLedInterval);
    Serial.print(" Time ");
    Serial.print(curMillis >> 9); // divide by 512 is approx = half-seconds
    Serial.println(">");
  }
}
