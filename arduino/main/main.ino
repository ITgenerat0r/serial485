
#include <String.h>

#define key_pin 6



int key_value = 0;
float v = 0;

String tp = "";

void setup() {
  // put your setup code here, to run once:

  Serial.begin(115200);



  
}

void loop() {
  // put your main code here, to run repeatedly:

  key_value = analogRead(key_pin);

  v = 1.0 * map(key_value, 0, 1024, 0, 500) / 100;

  // Отправляем значение в Serial Monitor
  Serial.print("Аналоговое значение: ");
  Serial.print(key_value);
  Serial.print(",  (");
  Serial.print(v);
  Serial.println("v).");
  if (v < 0.75){
  	if (v < 0.25){
  		Serial.println("PAS. R=None");
	} else {
		Serial.println("PAS. R=91kOm");
	}
	tp = "PAS";
  } else if (v > 0.75 && v < 1.25){
  	Serial.println("Free. R=39kOm");
  } else if (v > 1.25 && v < 1.75){
  	Serial.println("Free. R=24kOm");
  } else if (v > 1.75 && v < 2.25){
  	Serial.println("Free. R=15kOm");
  } else if (v > 2.25 && v < 2.75){
  	Serial.println("Free. R=10kOm");
  } else if (v > 2.75 && v < 3.25){
  	Serial.println("Free. R=6.8kOm");
  } else if (v > 3.25 && v < 3.75){
  	Serial.println("Free. R=4.3kOm");
  } else if (v > 3.75 && v < 4.25){
  	Serial.println("DOL. R=2.4kOm");
  	tp = "DOL";
  } else if (v > 4.25 && v < 4.75){
  	Serial.println("Free. R=1kOm");
  } else if (v > 4.75){
  	Serial.println("Free. R=?Om");
  }

  delay(1000);
}
