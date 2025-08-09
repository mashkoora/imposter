#include <Servo.h>

Servo servoX;
Servo servoY;
Servo extraServo;

const int extraServoNeutral = 180;
const int extraServoTriggeredPos = 150; // 30 degrees less

bool extraServoActive = false;
unsigned long extraServoStartTime = 0;
const unsigned long extraServoHoldDuration = 3000; // 3 seconds

void setup() {
  Serial.begin(9600);
  servoX.attach(9);
  servoY.attach(10);
  extraServo.attach(11);
  servoX.write(90);
  servoY.write(90);
  extraServo.write(extraServoNeutral);
}

void loop() {
  if (Serial.available() >= 3) {
    int posX = Serial.read();
    int posY = Serial.read();
    int extraTrigger = Serial.read();

    posX = constrain(posX, 0, 180);
    posY = constrain(posY, 0, 180);

    servoX.write(posX);
    servoY.write(posY);

    if (extraTrigger == 1 && !extraServoActive) {
      extraServo.write(extraServoTriggeredPos);
      extraServoStartTime = millis();
      extraServoActive = true;
    } 
    else if (extraTrigger == 0 && !extraServoActive) {
      extraServo.write(extraServoNeutral);
    }
  }

  // After holding for 3 seconds, return extra servo to neutral
  if (extraServoActive && (millis() - extraServoStartTime >= extraServoHoldDuration)) {
    extraServo.write(extraServoNeutral);
    extraServoActive = false;
  }
}
