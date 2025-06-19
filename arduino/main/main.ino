
#include <String.h>

#define key_pin 6

// ============================================================================
// ===  KEY  ==================================================================
// ============================================================================
int key_value = 0;
float v = 0;

String tp = "";

// ============================================================================
// ===  PAS  ==================================================================
// ============================================================================

#define clk 8
#define mosi 9
#define ss_pin 12
#define u_pin 10
#define imp_pin 11

#define async_delay 1

//int ss_ar[5] = {12};
unsigned long int x;

void setup_PAS() {
  x = 21846;
  Serial.begin(115200);
  Serial.setTimeout(1);
  
  pinMode(clk, OUTPUT);
  pinMode(mosi, OUTPUT);
  pinMode(ss_pin, OUTPUT);
//  for(int i = 0; i<5; i++){
//    pinMode(ss_ar[i], OUTPUT);
//  }
  pinMode(u_pin, OUTPUT);
  pinMode(imp_pin, OUTPUT);


  digitalWrite(clk, LOW);
  digitalWrite(mosi, LOW);
  digitalWrite(ss_pin, HIGH);
//  for(int i = 0; i<5; i++){
//    digitalWrite(ss_ar[i], HIGH);
//  }
  analogWrite(imp_pin, 0);
  analogWrite(u_pin, 255);
}

void clocks(byte n){
  for(byte i = 0; i < n; i++){
    delay(async_delay);
    digitalWrite(clk, HIGH);
    delay(async_delay*2);
    digitalWrite(clk, LOW);
    delay(async_delay);
  }
}


void send_bit(bool b){
  if(b){
    digitalWrite(mosi, HIGH);
  }else{
    digitalWrite(mosi, LOW);
  }
//  delay(async_delay);
  
  clocks(16);
}


void transfer_async(unsigned int data){
//  Serial.print("data: ");
//  Serial.println(data, HEX);
  digitalWrite(mosi, HIGH);
  digitalWrite(clk, LOW);
  delay(async_delay);

  clocks(8);
  send_bit(false);
  
  for(byte i = 15; i >= 0; i--){
    bool b = (data>>i)&1;
    send_bit(b);
    if (i == 0) break;
  }
  send_bit(true);
  digitalWrite(mosi, LOW);
  clocks(8);
  delay(async_delay);
  
  digitalWrite(mosi, HIGH);
  digitalWrite(clk, HIGH);
}



void transfer_3wire(unsigned int data){
//  Serial.print("data: ");
//  Serial.println(data, HEX);
    delay(1);
  for(byte i = 15; i >= 0; i--){
    bool b = (data>>i)&1;
    digitalWrite(clk, LOW);
    delay(1);
    if(b){
      digitalWrite(mosi, HIGH);
    }else{
      digitalWrite(mosi, LOW);
    }
    delay(1);
    digitalWrite(clk, HIGH);
    delay(1);
    if (i == 0) break;
  }
  digitalWrite(ss_pin, LOW);
  digitalWrite(ss_pin, HIGH);
//  for(int i = 0; i<5; i++){
//    digitalWrite(ss_ar[i], LOW);
//  }
//  for(int i = 0; i<5; i++){
//    digitalWrite(ss_ar[i], HIGH);
//  }
  digitalWrite(mosi, LOW);
  digitalWrite(clk, LOW);
}

void loop_PAS() {
  if (Serial.available()){ 
    x = Serial.readString().toInt();
    if(x == 0xffffffff){
      Serial.print("PAS");
    } else {
      Serial.print(x, HEX);
    }
    
//    Serial.print(", ");
    unsigned int i_value = x&0xffff;
    byte u_value = (x>>16)&0xff;
    u_value ^= 0xff;
    byte imp_value = (x>>24)&0xff;
//    if(u_value < 0x2D){u_value = 0x2D;}
//    Serial.print("(");
//    Serial.print(imp_value, HEX);
//    Serial.print(", ");
//    Serial.print(i_value, HEX);
//    Serial.print(", ");
//    Serial.print(u_value, HEX);
//    Serial.print(")");
    transfer_3wire(i_value);
    analogWrite(u_pin, u_value);
    analogWrite(imp_pin, imp_value);
//    Serial.println(".");
  }
  
  
//  transfer_async(x);
delay(10);
}

// ============================================================================
// ===  DOL  ==================================================================
// ============================================================================
#define pul_pin 20
#define dir_pin 19
#define ena_pin 18

#define MIN_ICED 190 // 150 is working, but there is DOPM (need 180), lower for DOL100
#define MAX_ICED 1300


bool dir = false;


void setup_DOL() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial.setTimeout(1);

  
  pinMode(pul_pin, OUTPUT);
  pinMode(dir_pin, OUTPUT);
  pinMode(ena_pin, OUTPUT);

  digitalWrite(ena_pin, LOW);
  delay(1);
  digitalWrite(dir_pin, LOW);
  delay(1);
  digitalWrite(pul_pin, HIGH);
  delay(1);

}


void spin_old(int n){
  float d = 1;
  for(int i = 0; i < n; i++){
    digitalWrite(pul_pin, LOW);
//    delay(d);
    digitalWrite(pul_pin, HIGH);
    delay(d);
  }
}

// n - number of steps, dly - delay in ms/10 for semistep, it's means 20dly == 2ms for one step
void spin(int n, int dly){
  int pass = 0;
  n *= 2;
  bool state = true;
//  unsigned long int last_ms = millis();
  while(n > 0){
//    unsigned long int current_ms = millis();
//    last_ms = current_ms();
//    if (current_ms > 0){
//      pass = pass - (pass % 10) + 10;
//    } 
//    pass++;
    if(++pass > dly){
//      Serial.println(pass);
      pass = 0;
      if(state){
        digitalWrite(pul_pin, LOW);
      } else {
        digitalWrite(pul_pin, HIGH);
      }
      state = !state;
      n--;
    }
//    Serial.println(pass);
    
    
  }
}


void spin2(int n, int dly){
  int pass = 0;
//  unsigned long int last_ms = millis();
  while(n > 0){
//    unsigned long int current_ms = millis();
//    last_ms = millis();
    if (++pass > dly){
//      pass = pass - (pass % 10) + 10;
//      Serial.println(pass);
      pass = 0;
    } 
//    else {
//      pass++;
//      if (pass > dly){
//        pass = 0;
//      }
//    }
//    pass++;
//    last_ms = current_ms;
    if(pass == 0){
      digitalWrite(pul_pin, LOW);
      digitalWrite(pul_pin, HIGH);
      n--;
    }
  }
}


void runner(int min_speed, int max_speed, void (*spin)(int, int)){
  for(int i = min_speed; i >= max_speed; i--){
    spin(50, i);
  }
  for(int i = max_speed; i <= min_speed; i++){
    spin(50, i);
  }
}


// ice table
int table_iced[] =  {1200, 1000, 850, 700, 600, 500, 400, 300, 350, 200, 150, 125, 100};
int table_steps[] = {   3,   5,  10,  15,  20,  35,  50,  70,  100, 200, 300, 400, 500};


void fly(bool direction, int32_t duration, void (*spin)(int, int)){
  int32_t log = -1;
  if(direction){
    //    dir = false;
    digitalWrite(dir_pin, HIGH);
    delay(1);
  } else {
    //    dir = true;
    digitalWrite(dir_pin, LOW);
    delay(1);
  }

  int32_t current_duration = duration / 2;
  // duration -= current_duration;

  byte pos = 0;
  int steps = table_steps[pos];
  int iced = table_iced[pos];

  // speed up
  bool key_done = false;
  int min_i = MIN_ICED;
  int32_t step_counter = 0;
  for(int i = MAX_ICED; i >= MIN_ICED; i--){
    current_duration -= steps;
    if(current_duration<0){
      steps += current_duration;
      current_duration = 0;
      key_done = true;
    }
    spin(steps, i);
    step_counter += steps;
    if(key_done){
      min_i = i;
      break;
    }
    if(i < table_iced[pos] && sizeof(table_iced)-1 > pos){
      steps = table_steps[++pos];
    }
  }
  // max speed
  duration -= step_counter * 2;
  log = duration;
  while(duration > 0){
    if(duration<1000){
      spin(duration, min_i);
      break;
    } else {
      spin(1000, min_i);
      duration -= 1000;
    }
    
  }
  duration = step_counter;

  



  // slow down
  key_done = false;
  int32_t down_counter = 0;
  for(int i = min_i; i <= MAX_ICED; i++){
    duration -= steps;
    if(duration < 0){
      steps += duration;
      duration = 0;
      key_done = true;
    }
    spin(steps, i);
    down_counter += steps;
    if(key_done){
      break;
    }
    if(i > table_iced[pos] && pos > 0){
      steps = table_steps[--pos];
    }
  }
  spin(duration, table_iced[0]);
  down_counter += duration;


  Serial.print("Speed up takes ");
  Serial.print(step_counter);
  Serial.println(" steps.");

  Serial.print("High speed takes ");
  Serial.print(log);
  Serial.println(" steps.");

  Serial.print("Slow down takes ");
  Serial.print(down_counter);
  Serial.println(" steps.");

  Serial.print("Log: (duration)"); Serial.println(duration);


}


bool debug_log = false;

int32_t ss = 100;
void loop_DOL() {
  // put your main code here, to run repeatedly:

  if (Serial.available()){ 
    if (debug_log){
      Serial.println(ss);
    }
      // ss = Serial.readString().toInt();
    int32_t st = Serial.parseInt();
    if (st > 0){
      // Serial.println(ss);
      ss = 100 * st;
      
      // ss = 100 * Serial.parseInt();
        // uint32_t xx = 0-1;
      if (debug_log){
        Serial.print("--------------------- \nSet steps: "); Serial.println(ss);
      }
      
        
    // runner(1200, ss, spin); 
      fly(dir, ss, spin);
      if (debug_log){
        Serial.println("-----------------");
      }
      if(!debug_log){
        Serial.print(ss);
      }
      
    } else {
      if (st == 0){
        dir = !dir;
        if (debug_log){
          Serial.print("dir: ");
        }
        Serial.print(dir);
        if (debug_log){
          Serial.println(".");
        }
      } else {
        Serial.print("DOL");
      }
      
    }
  }


}

// ============================================================================
// ===  MAIN SETUP  ===========================================================
// ============================================================================
void setup() {
  setup_PAS();
}

// ============================================================================
// ===  MAIN LOOP  ============================================================
// ============================================================================
void loop() {
  // put your main code here, to run repeatedly:

  key_value = analogRead(key_pin);

  v = 1.0 * map(key_value, 0, 1024, 0, 500) / 100;

  // Serial.print("Аналоговое значение: ");
  // Serial.print(key_value);
  // Serial.print(",  (");
  // Serial.print(v);
  // Serial.println("v).");
  if (v < 0.75){
  	// if (v < 0.25){
  	// 	Serial.println("PAS. R=None");
    // } else {
    //   Serial.println("PAS. R=91kOm");
    // }
    if(tp != "PAS"){
      setup_PAS();
      tp = "PAS";
    }
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
  	// Serial.println("DOL. R=2.4kOm");
    if(tp != "DOL"){
      setup_DOL();
      tp = "DOL";
    }
  } else if (v > 4.25 && v < 4.75){
  	Serial.println("Free. R=1kOm");
  } else if (v > 4.75){
  	Serial.println("Free. R=?Om");
  }

  if (tp == "PAS"){
    loop_PAS();
  } else if (tp == "DOL"){
    loop_DOL();
  }
}
