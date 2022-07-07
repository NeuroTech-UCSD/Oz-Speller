#define LEDPIN 11         //LED brightness (PWM) writing
#define LIGHTSENSORPIN A0 //Ambient light sensor reading 

void setup() {
  pinMode(LIGHTSENSORPIN,  INPUT);  
//  pinMode(LEDPIN, OUTPUT);  
  Serial.begin(19200);
//  Serial.begin(9600);
}

unsigned long t = 0;
unsigned long interval = 2497;
unsigned long previous_micro = 0;

void loop() {
//  float reading = analogRead(LIGHTSENSORPIN); //Read light level
//  float square_ratio = reading / 1023.0;      //Get percent of maximum value (1023)
//  square_ratio = pow(square_ratio, 2.0);      //Square to make response more obvious

//  analogWrite(LEDPIN, 255.0 * square_ratio);  //Adjust LED brightness relatively
//  t=micros();
//  if (t - previous_micro >= interval) {
//    previous_micro = t;
//    short reading = analogRead(LIGHTSENSORPIN); //Read light level
//    Serial.print(t);
//    Serial.print(", ");
//    Serial.println(reading);                    //Display reading in serial monitor
//  }
//  t=micros();
//  float reading = analogRead(LIGHTSENSORPIN);
//  Serial.print(t);
//  Serial.print(", ");
//  Serial.println(reading);
//  delayMicroseconds(interval-(t-previous_micro));
//  previous_micro = t;

  unsigned char reading = analogRead(LIGHTSENSORPIN); //Read light level
  Serial.write(reading);
  Serial.flush();
//  t=micros();
//  if (t - previous_micro >= interval) {
//    previous_micro = t;
//    unsigned char reading = analogRead(LIGHTSENSORPIN); //Read light level
//    Serial.write(reading);
//    Serial.flush();                 //Display reading in serial monitor
//  }
}
