

#define key_pin 1



int key_value = 0;

void setup() {
  // put your setup code here, to run once:

  Serial.begin(115200);



  
}

void loop() {
  // put your main code here, to run repeatedly:

  key_value = analogRead(key_pin);

  // Отправляем значение в Serial Monitor
  Serial.print("Аналоговое значение: ");
  Serial.println(key_value);

  delay(1000);
}
