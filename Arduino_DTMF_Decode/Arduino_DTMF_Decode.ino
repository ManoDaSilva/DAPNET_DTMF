/*
Original source: https://electropeak.com/learn/interfacing-mt8870-dtmf-decoder-module-with-arduino/

DTMF Decoder interface: connects to an MT8870 module, interprets the I/O and spits out single digit numbers via serial.

29/01/23 - Manoel ON6RF

*/

bool triggered = false;
bool fallen = false;

void setup() {
  Serial.begin(9600);
  pinMode(3, INPUT); //Q1
  pinMode(4, INPUT); //Q2 
  pinMode(5, INPUT); //Q3
  pinMode(6, INPUT); //Q4
  pinMode(7, INPUT); //STQ
}

void loop() {
  uint8_t number;
  bool signal;
  signal = digitalRead(7);
  if (signal == HIGH) /*When DTMF tone is detected, STQ will read HIGH for the duration of the tone*/
  {
    if (fallen == true) {
      triggered = true;
      fallen=false;
    }
  }
  else{
    fallen = true;
  }
  if (triggered) {
    number = (0x00 | (digitalRead(3) << 0) | (digitalRead(4) << 1) | (digitalRead(5) << 2) | (digitalRead(6) << 3));
    switch (number) {
      case 0x01:
        Serial.print("1");
        break;
      case 0x02:
        Serial.print("2");
        break;
      case 0x03:
        Serial.print("3");
        break;
      case 0x04:
        Serial.print("4");
        break;
      case 0x05:
        Serial.print("5");
        break;
      case 0x06:
        Serial.print("6");
        break;
      case 7:
        Serial.print("7");
        break;
      case 0x08:
        Serial.print("8");
        break;
      case 0x09:
        Serial.print("9");
        break;
      case 0x0A:
        Serial.print("0");
        break;
      case 0x0B:
        Serial.print("*");
        break;
      case 0x0C:
        Serial.print("#");
        break;
    }
    triggered = false;
  }
}