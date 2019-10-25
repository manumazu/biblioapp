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

int node_length = 3;
//for columns
int outputCol[NUMPIXELS1];//biggest band;
int currentCol[NUMPIXELS1];
//for lines
int outputRow[NUMPIXELS1];
int currentRow[NUMPIXELS1];
//for range
int outputRange[NUMPIXELS1];

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

int getLedAddress() {
  // map it to the range pix of the analog out:
  /*outputCol[0] = map(analogRead(A0), 0, 1024, 0, NUMPIXELS1);
  outputCol[1] = 5;
  outputCol[2] = 8;
  
  // map it to the range lines of the analog out:
  outputRow[0] = map(analogRead(A1), 0, 1024, 1, 3);
  outputRow[1] = 2;
  outputRow[2] = 2;
  
  // ranges
  outputRange[0] = 2;
  outputRange[1] = 1;
  outputRange[2] = 2;*/
  
  StaticJsonBuffer<200> jsonBuffer;
  char json[] = "[{\"column\": 8, \"range\": 3, \"row\": 2, \"date_add\": \"Fri, 25 Oct 2019 11:12:05 GMT\", \"id_arduino\": 123} \
    , {\"column\": 5, \"range\": 2, \"row\": 1, \"date_add\": \"Wed, 23 Oct 2019 18:54:22 GMT\", \"id_arduino\": 123} \
    , {\"column\": 1, \"range\": 2, \"row\": 2}]";
  JsonArray& nodes = jsonBuffer.parseArray(json);
  node_length = nodes.size(); 
  for(int i=0; i<node_length;i++){
    outputCol[i] = nodes[i]["column"];
	outputRow[i] = nodes[i]["row"];
    outputRange[i] = nodes[i]["range"];
  }
}

void ledsManager(String action) {
   
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
       if(action.equals("on"))
       {
         //loop on asked position array
         for (int x=0; x < node_length; x++) {
           int pos = outputCol[x];
           int line = outputRow[x];
           int range = outputRange[x];
           setColor(x*10);
           if(line==j && i>=pos && i<=(pos+range-1)){ //light on given line
              currentPix.setPixelColor(i, currentPix.Color(redColor, greenColor, blueColor));
              currentCol[x] = pos;
              currentRow[x] = line;
           }
           Serial.println(pos+(String)'-'+line+(String)'-'+range);
         }
       }
       currentPix.show();
     }
   } 
}


void loop() {

  delay(delayval);
  getLedAddress();
  
  if(outputCol[0]!=currentCol[0] || outputRow[0]!=currentRow[0]) {// new request
    stateReset=1;
    ledsManager(String("off"));//switch off all
  }
  
  //light asked led  
  if(stateReset==1) {
    ledsManager(String("on"));
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
void setColor(int x){
  redColor = random(x, 255);
  greenColor = random(x,255);
  blueColor = random(x, 255);
}
