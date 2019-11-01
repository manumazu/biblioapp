#include <Adafruit_NeoPixel.h>
#include <ArduinoJson.h>

#define PIN 2	 // input pin Neopixel is attached to

#define NUMPIXELS      24 // number of neopixels in strip

Adafruit_NeoPixel pixels = Adafruit_NeoPixel(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);
//Adafruit_NeoPixel currentPix;

int delayval = 250; // timing delay in milliseconds

int redColor = 0;
int greenColor = 0;
int blueColor = 0;

const int buttonPin = 4;
int buttonState = 1;
int stateReset = 1;

int node_length = 3;
//for columns
int outputCol[NUMPIXELS];
int currentCol[NUMPIXELS];
//for range
int outputRange[NUMPIXELS];


void setup() {
  // Initialize the NeoPixel library.
  pixels.begin();
  pinMode(buttonPin, INPUT_PULLUP); //reset/start
  pinMode(A0, INPUT);//col 
  Serial.begin(9600);
}

int getLedAddress() {
  // map it to the range pix of the analog out:
  outputCol[0] = map(analogRead(A0), 0, 1024, 0, NUMPIXELS);
  outputCol[1] = 5;
  outputCol[2] = 8;
  
  // ranges
  outputRange[0] = 2;
  outputRange[1] = 1;
  outputRange[2] = 3;
  
  /*StaticJsonBuffer<200> jsonBuffer;
  char json[] = "[{\"column\": 14, \"range\": 3, \"row\": 2, \"date_add\": \"Fri, 25 Oct 2019 11:12:05 GMT\", \"id_arduino\": 123} \
      , {\"column\": 5, \"range\": 2, \"row\": 1, \"date_add\": \"Wed, 23 Oct 2019 18:54:22 GMT\", \"id_arduino\": 123} \
    , {\"column\": 1, \"range\": 2, \"row\": 2} \
  ]";
  JsonArray& nodes = jsonBuffer.parseArray(json);
  node_length = nodes.size(); 
  for(int i=0; i<node_length;i++){
    outputCol[i] = nodes[i]["column"];
	//outputRow[i] = nodes[i]["row"];
    outputRange[i] = nodes[i]["range"];
  }*/
}

void ledsAll() {
  for (int i=0; i < NUMPIXELS; i++) 
  {
      pixels.setPixelColor(i, pixels.Color(255, 69, 0));
  }
  pixels.show();
}

void ledsOn() {
  //loop on asked position array
  for (int x=0; x < node_length; x++) {
    int pos = outputCol[x];
    int range = outputRange[x];
    for (int i=pos; i<=(pos+range-1); i++) { //light on given line
      pixels.setPixelColor(i, pixels.Color(redColor, greenColor, blueColor));
    }
    currentCol[x] = pos;
  }
  pixels.show();
}


void loop() {

  //delay(delayval);
  getLedAddress();
  
  if(outputCol[0]!=currentCol[0]) {// new request
    stateReset=1;
    pixels.clear();
    setColor(random(NUMPIXELS));
    Serial.println(outputCol[0]+(String)'-'+outputRange[0]);
  }
  
  //light asked led  
  if(stateReset==1) {
    ledsOn();
  }
  
  //reset mode
  buttonState = digitalRead(buttonPin);
  if (stateReset==1 && buttonState == LOW) {
    Serial.println("PUSH");
    stateReset = 2;
    ledsAll();
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
