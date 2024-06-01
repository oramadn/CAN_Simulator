#include <SPI.h>
#include <mcp2515.h>
#include <Servo.h>

const int POT_PIN = A5;   // Analog pin for potentiometer
const int SERVO_PIN = 6;  // Pin for Servo

struct CANMessage {
  uint32_t id;
  can_frame data[3];
  int dataCount;
};

can_frame createFrame(const String &dataString) {
  can_frame frame;
  frame.can_dlc = 8;
  for (int j = 0; j < 8; j++) {
    frame.data[j] = strtol(dataString.substring(2 * j, 2 * j + 2).c_str(), NULL, 16);
  }
  return frame;
}

CANMessage messages3[] = {
  { 0x00772, { createFrame("6f301fb62d592ab0") }, 1 },
  { 0x00132, { createFrame("40fc6e96aa269546"), createFrame("1d1364886c93719d") }, 2 },
  { 0x00206, { createFrame("39bde52b30c0c2d5"), createFrame("87fd05ab4da21605"), createFrame("4dc2ba5d3c97bad5") }, 3 },
  { 0x00579, { createFrame("fd45fb5c13fd8e16"), createFrame("2907f7625f523d00") }, 2 },
  { 0x00324, { createFrame("9eb0fe29fd619abb"), createFrame("dd43441ec2b70bb2") }, 2 },
  { 0x00002, { createFrame("81bd8ade55b7e79c") }, 1 },
  { 0x0028b, { createFrame("25594285eb349dd7") }, 1 },
  { 0x000b2, { createFrame("1bac08e23b808dd6"), createFrame("2889aa670eeab7d6") }, 2 },
  { 0x00463, { createFrame("53981e27e1aae357"), createFrame("7251cc3035d752e7") }, 2 },
  { 0x0008a, { createFrame("54964b7b31250d05"), createFrame("d435adb6cdc61060") }, 2 },
};

int messageCount3 = sizeof(messages3) / sizeof(messages3[0]);
struct can_frame canMsg3;
struct can_frame canPot3;
struct can_frame RecvCan3;
MCP2515 mcp2515_3(10);  // SPI CS Pin

Servo myServo;

void setup() {
  Serial.begin(500000);
  pinMode(POT_PIN, INPUT);
  myServo.attach(SERVO_PIN);  // Attach the servo to the specified pin

  SPI.begin();
  mcp2515_3.reset();
  mcp2515_3.setBitrate(CAN_1000KBPS, MCP_8MHZ);
  mcp2515_3.setNormalMode();

}

String byteToHex(byte b) {
  String hexStr = String(b, HEX);
  if (hexStr.length() < 2) {
    hexStr = "0" + hexStr;
  }
  return hexStr;
}

void loop() {
  for (int i = 0; i < messageCount3; i++) {
    CANMessage msg = messages3[i];
    int randomDataIndex = random(0, msg.dataCount);
    can_frame canMsg3 = msg.data[randomDataIndex];
    canMsg3.can_id = msg.id;

    if (msg.id == 0x00002) {
      int potValue = analogRead(5);                      // Read potentiometer value
      canMsg3.data[0] = map(potValue, 0, 1023, 0, 255);  // Map potentiometer value to 0-255 range
      canMsg3.can_id = 0x02;
      canMsg3.can_dlc = 8;
      mcp2515_3.sendMessage(&canMsg3);
      delay(20);
    } else {
      mcp2515_3.sendMessage(&canMsg3);
      delay(5);  // Random delay between 1 to 20 milliseconds
    }

    // Check for received CAN messages
    if (mcp2515_3.readMessage(&RecvCan3) == MCP2515::ERROR_OK) {
      if (RecvCan3.can_id == 0x03) {
        int angle1 = RecvCan3.data[0];
        int potByte = map(angle1, 0, 255, 0, 180);
        myServo.write(potByte);
        mcp2515_3.sendMessage(&RecvCan3);
        delay(2);
      }
    }
  }
}
