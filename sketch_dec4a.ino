#include <FastLED.h>
#define NUM_LEDS 85
#define LED_PIN 2

CRGB leds[NUM_LEDS];
int sentimentCount [7] = {0,0,0,0,0,0,0};
int ratioList[NUM_LEDS];
         
void distributeList(int emotion) {
  int index = 0;
  double sum = 0;

  // Update sentiment count with new emotion
  sentimentCount[emotion]++;

  // Print current sentiment count
  for (int i = 0; i < 7; i++) {
      // Serial.print(sentimentCount[i]);
      sum+=sentimentCount[i];
      // Serial.print(" ");  // Print a space between numbers
  }
  // Serial.println();  // Print a newline at the end

  // Calculate frequency (Num of lights correlating to ratio of presence of emotion)
  double freq[7] = {0,0,0,0,0,0,0}; 
  freq[0] = 0;
  for (int i = 0; i < 7; i++) {\
    // Serial.print("sum ");
    // Serial.println(sum);
    // Serial.print("sent count ");
    // Serial.println(sentimentCount[i]);
    // Serial.println(freq[i]);
    //How many LEDS should be lit for this sentiment (Max 85)
    freq[i] = ceil(double(NUM_LEDS) * (double(sentimentCount[i])/double(sum)));
    // Serial.print("freq2 ");
    // Serial.println(freq[i]);
  }

  // // Print frequency
  // for (int i = 0; i < 7; i++) {
  //     Serial.print(freq[i]);
  //     Serial.print(" ");
  // }
  // Serial.println();  // Print a newline at the end

  // Rearrange numbers in the result list
  for (int i = 0; i < NUM_LEDS; i++) {
    ratioList[i] = -1; // Initialize result list with -1
  }
  index = 0;
  for (int i = 0; i < 7; i++) {
    int num = i;
    int count = freq[i];
    for (int j = 0; j < count-1; j++) {
      while (ratioList[index] != -1) {
        index = (index + 1) % NUM_LEDS; // Find the next available position
      }

      ratioList[index] = num;
      index = (index + 8) % NUM_LEDS; // Maximize spacing
    }
  }
  // Randomly assign light ordering (Each same colour should be fairly evenly dispersed)

  //Print ratio list
  // for (int i = 0; i < 85; i++) {
  //     Serial.print(ratioList[i]);
  //     Serial.print(" ");  // Print a space between numbers
  // }
  // Serial.println();  // Print a newline at the end

 }

  

void setup () {

  Serial.begin(9600);

  FastLED.addLeds<WS2812B, LED_PIN, GRB>(leds, NUM_LEDS);
  FastLED.setBrightness(50);
  for (int i=0; i<NUM_LEDS; i++){
    leds[i] = CRGB::Black;
  }
  delay(2000);
}

void loop () {
  // // Wait for a response
  while (Serial.available() == 0) {
    delay(100);
  }

  // // // Read and display the response
  String response = Serial.readStringUntil('\n');
  // // Serial.println("Response from Hugging Face:");
  // Serial.println(response);

  // // // Perform distribution
  // for (int i=0; i<sizeof(fakeloop); i++){
  //   Serial.println(fakeloop[i]);
  distributeList(response.toInt());

    // # 0 = Neutral: Black
    // # 1 = Joy: Golden
    // # 2 = Anger: Red
    // # 3 = Sadness: DeepSkyBlue
    // # 4 = Love: Hot Pink
    // # 5 = Fun: Green
    // # 6 = Unease; DarkOliveGreen
    // # 7 = Reflection: Violet
    FastLED.clear();
    delay(2000);
    // {3,4,2,4,6,1,7,5,2,2,2};
    for (int i=0; i<NUM_LEDS; i++){
      if (ratioList[i]==1){
        leds[i] = CRGB::Gold;
      }
      else if (ratioList[i]==2){
        leds[i] = CRGB::Red;
      }
      else if (ratioList[i]==3){
        leds[i] = CRGB::DeepSkyBlue;
      }
      else if (ratioList[i]==4){
        leds[i] = CRGB::HotPink;
      }
      else if (ratioList[i]==5){
        leds[i] = CRGB::Green;
      }
      else if (ratioList[i]==6){
        leds[i] = CRGB::DarkOliveGreen;
      }
      else if (ratioList[i]==7){
        leds[i] = CRGB::Violet;
      }
    }
    FastLED.show();
    delay(1000);
  }
