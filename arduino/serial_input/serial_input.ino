/*#include <Servo.h>
Servo myServo;
byte servoPin = 8;
byte servoMin = 10;
byte servoMax = 170;
byte servoPos = 0;
byte newServoPos = servoMin;*/

const byte numLEDs = 3;
byte ledPin[numLEDs] = {3, 4, 5};
unsigned long LEDinterval[numLEDs] = {400, 400, 400};
unsigned long prevLEDmillis[numLEDs] = {0, 0, 0};

const byte buffSize = 40;
char inputBuffer[buffSize];
const char startMarker = '<';
const char endMarker = '>';
byte bytesRecvd = 0;
boolean readInProgress = false;
boolean newDataFromPC = false;

boolean ledStatus = false;
int switchstate = 0;
int newLedColumn = 0;

char messageFromPC[buffSize] = {0};
int newFlashInterval = 0;
float servoFraction = 0.0; // fraction of servo range to move


unsigned long curMillis;

unsigned long prevReplyToPCmillis = 0;
unsigned long replyToPCinterval = 1000;

//=============

void setup() {
  Serial.begin(9600);

  // declare LEDs as output
  for (byte n = 0; n < numLEDs; n++) {
     pinMode(ledPin[n], OUTPUT);
    // digitalWrite(ledPin[n], HIGH);
  }

  // declare the switch pin as an input
  pinMode(7, INPUT);
  
  /*delay(500); // delay() is OK in setup as it only happens once
  
  for (byte n = 0; n < numLEDs; n++) {
     digitalWrite(ledPin[n], LOW);
  }*/
  
    // tell the PC we are ready
  Serial.println("<Arduino is ready>");
}

//=============

void loop() {
  //set stop button
  switchstate = digitalRead(7);
  if (switchstate == HIGH) {
    //force ledstatus off
    ledStatus = false;
  }
  curMillis = millis();
  getDataFromPC();
  replyToPC();
  lightLEDs();  
  //flashLEDs();
}

//============

void lightLEDs() {

  if (ledStatus==true) { 
     if(newLedColumn==0) //when nothing is requested
      ledStatus=false;
     else 
      digitalWrite(ledPin[newLedColumn-1], HIGH ); 
  }
  else {
    for (byte n = 0; n < numLEDs; n++) {
       digitalWrite( ledPin[n], LOW );
    }  
  }
}

//=============

void getDataFromPC() {

    // receive data from PC and save it into inputBuffer
    
  if(Serial.available() > 0) {

    char x = Serial.read();

      // the order of these IF clauses is significant
      
    if (x == endMarker) {
      readInProgress = false;
      newDataFromPC = true;
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
  strcpy(messageFromPC, strtokIndx); // copy it to messageFromPC
  newLedColumn = atoi(strtokIndx);
  
  strtokIndx = strtok(NULL, ","); // this continues where the previous call left off
  newFlashInterval = atoi(strtokIndx);     // convert this part to an integer
  
  strtokIndx = strtok(NULL, ","); 
  servoFraction = atof(strtokIndx);     // convert this part to a float

}

//=============

void replyToPC() {

  if (newDataFromPC) {
    ledStatus = true;
    newDataFromPC = false;
    Serial.print("<Msg ");
    Serial.print(messageFromPC);
    Serial.print(" NewFlash ");
    Serial.print(newFlashInterval);
    Serial.print(" SrvFrac ");
    Serial.print(servoFraction);
    Serial.print(" Time ");
    Serial.print(curMillis >> 9); // divide by 512 is approx = half-seconds
    Serial.println(">");
  }
}


/*
//=============

void updateLED1() {

  if (newFlashInterval > 100) {
    LEDinterval[0] = newFlashInterval;
  }
}

//=============

void flashLEDs() {
  if (ledStatus==true) {
    for (byte n = 0; n < numLEDs; n++) {
      if (curMillis - prevLEDmillis[n] >= LEDinterval[n]) {
         prevLEDmillis[n] += LEDinterval[n];
         digitalWrite( ledPin[n], !digitalRead( ledPin[n]) );
      }
    }
  }
  else {
    for (byte n = 0; n < numLEDs; n++) {
       digitalWrite( ledPin[n], LOW );
    }
  }
}
*/
