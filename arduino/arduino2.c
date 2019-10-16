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
int outputCol = 0;
int currentCol = 0;
//for lines
int outputRow = 0;
int currentRow = 0;
//for range
int outputRange = 1;
int currentRange = 0;

int num = 1;
String action;

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
  outputCol = map(analogRead(A0), 0, 1024, 0, NUMPIXELS1);
  // map it to the range lines of the analog out:
  outputRow = map(analogRead(A1), 0, 1024, 1, 3);

  /*StaticJsonBuffer<200> jsonBuffer;
  char json[] = "{\"column\": 10, \"date_add\": \"Wed, 16 Oct 2019 22:11:54 GMT\", \"id_arduino\": 123, \"range\": 2, \"row\": 1}";
  JsonObject& address = jsonBuffer.parseObject(json);
  outputCol = address["column"];
  outputRow = address["row"];
  outputRange = address["range"];*/
  
  Serial.println(outputCol+(String)'-'+outputRow);
}

void ledsManager(String action, int pos = 0, int line = 0, int range = 0) {
   
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
         if(line==j && i>=pos && i<=(pos+range-1)) //light on given line
        	currentPix.setPixelColor(i, currentPix.Color(redColor, greenColor, blueColor));
            currentCol = pos;
            currentRow = line;
       }
       currentPix.show();
     }
   } 
}


void loop() {

  delay(delayval);
  getLedAddress();
  
  if(outputCol!=currentCol || outputRow!=currentRow) {// new request
    stateReset=1;
    setColor();
    ledsManager(String("off"));//switch off all
    
  }
  
  //light asked led  
  if(stateReset==1) { 
    ledsManager(String("on"),outputCol, outputRow, outputRange);
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
