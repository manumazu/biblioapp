#include <Adafruit_NeoPixel.h>
#include <ArduinoJson.h>

#define PIN 2	 // input pin Neopixel is attached to
#define PIN2 3	 // input pin Neopixel2 is attached to

#define NUMPIXELS1      12 // number of neopixels in strip
#define NUMPIXELS2      12 // number of neopixel2 in strip

Adafruit_NeoPixel pixels1 = Adafruit_NeoPixel(NUMPIXELS1, PIN, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel pixels2 = Adafruit_NeoPixel(NUMPIXELS2, PIN2, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel currentPix;

int delayval = 500; // timing delay in milliseconds

int redColor = 0;
int greenColor = 0;
int blueColor = 0;

const int buttonPin = 4;
int buttonState = 1;
int stateReset = 1;

//for columns
int outputCols = 0;
int currentCol = 0;
//for lines
int outputRow = 0;
int currentRow = 0;

int num = 1;
String action;

int address[3];
int currentadd[3];

void setup() {
  // Initialize the NeoPixel library.
  pixels1.begin();
  pinMode(buttonPin, INPUT_PULLUP); //reset/start
  pinMode(A0, INPUT);//col
  pinMode(A1, INPUT);//row  
  Serial.begin(9600);
}

void getLedAddress() {
  // map it to the range pix of the analog out:
  outputCols = map(analogRead(A0), 0, 1024, 0, NUMPIXELS1);
  
  // map it to the range lines of the analog out:
  outputRow = map(analogRead(A1), 0, 1024, 1, 3);  
 
  address[0]=outputCols;//pos
  address[1]=outputRow;//line
  address[2]=1;//space
  
  Serial.println(address[0]+(String)'-'+address[1]);
}

void ledsManager(String action, int pos = 0, int line = 0, int space = 0) {
   
   for (int j=1; j <= 2; j++) 
   {
      if (j==1) {
          num = NUMPIXELS1;
          currentPix = pixels1;
      }
      if (j==2) {
          num = NUMPIXELS2;
          currentPix = pixels2;
      }

     for (int i=0; i < num; i++) 
     {
       if(action.equals("off")) {
         currentPix.setPixelColor(i, currentPix.Color(0, 0, 0));
       }
       if(action.equals("all")) {
         currentPix.setPixelColor(i, currentPix.Color(255, 69, 0));
       }   
       if(action.equals("on")){
         if(line==j && i>=pos && i<=(pos+space-1)) //light on given line
        	currentPix.setPixelColor(i, currentPix.Color(redColor, greenColor, blueColor));
            currentCol = pos;
            currentRow = line;
            currentadd[0]=pos;
            currentadd[1]=line;
            currentadd[2]=space;
       }
       currentPix.show();
     }
   } 
}


void loop() {

  delay(delayval);
  getLedAddress();
  
  if(outputCols!=currentCol || outputRow!=currentRow) {// new request
    stateReset=1;
    setColor();
    ledsManager(String("off"));//switch off all
    
  }
  
  //light asked led  
  if(stateReset==1) { 
    ledsManager(String("on"),address[0], address[1], address[2]);
  }
  
  //reset mode
  buttonState = digitalRead(buttonPin);
  if (stateReset==1 && buttonState == LOW) {
    Serial.println("PUSH");
    stateReset = 2;
    ledsManager(String("all"));
  }
  
  /*buttonState = digitalRead(buttonPin);
  if (stateReset==2 && buttonState == LOW) {
    Serial.println("PUSH2");
    delay(delayval);
  	stateReset = 1; 
  }*/

}

// setColor()
// picks random values to set for RGB
void setColor(){
  redColor = random(0, 255);
  greenColor = random(0,255);
  blueColor = random(0, 255);
}
