#include <ArduinoJson.h>
//#include <Arduino_JSON.h>

const byte numChars = 200;
char receivedChars[numChars];

boolean newData = false;

void setup() {
    Serial.begin(9600);
    //while (!Serial) continue;
}

void loop() {
    recvWithStartEndMarkers();
    showNewData();
    //Serial.println(receivedChars);

    /*StaticJsonDocument<numChars> jsonArr;

    DeserializationError error = deserializeJson(jsonArr, receivedChars);

    // Test if parsing succeeds.
    if (error) {
      Serial.print(F("deserializeJson() failed: "));
      Serial.println(error.c_str());
      return;
    }*/
    
    
    /*size_t node_length = measureJson(jsonArr);
    
    Serial.println(node_length);
    int row = 0;
    int col = 0;
    for (int i = 0; i < node_length; i++) {
      col = jsonArr[i]["column"];
      Serial.println(col);
    }*/
    
    /*JSONVar jsonArr = JSON.parse(receivedChars);
    Serial.println(JSON.typeof(jsonArr));*/

    
    
}

void showNewData() {
    if (newData == true) {
        //Serial.print("This just in ... ");
        //Serial.println(receivedChars);
        StaticJsonDocument<numChars> jsonArr;

        DeserializationError error = deserializeJson(jsonArr, receivedChars);
    
        // Test if parsing succeeds.
        if (error) {
          Serial.print(F("deserializeJson() failed: "));
          Serial.println(error.c_str());
          return;
        }

        size_t node_length = measureJson(jsonArr);
        //Serial.println(node_length);
        int row = 0;
        int col = 0;
        for (int i = 0; i < node_length; i++) {
          col = jsonArr[i];
          Serial.println(col);
        }
        
        newData = false;
    }
}

void recvWithStartEndMarkers() {
    static boolean recvInProgress = false;
    static byte ndx = 0;
    char startMarker = '<';
    char endMarker = '>';
    char rc;
 
 // if (Serial.available() > 0) {
    while (Serial.available() > 0 && newData == false) {
        rc = Serial.read();

        if (recvInProgress == true) {
            if (rc != endMarker) {
                receivedChars[ndx] = rc;
                ndx++;
                if (ndx >= numChars) {
                    ndx = numChars - 1;
                }
            }
            else {
                receivedChars[ndx] = '\0'; // terminate the string
                recvInProgress = false;
                ndx = 0;
                newData = true;
            }
        }

        else if (rc == startMarker) {
            recvInProgress = true;
        }
    }
}
