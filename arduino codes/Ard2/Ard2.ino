#include <SPI.h>
#include <mcp2515.h>

const int POT_PIN = A5;   // Analog pin for potentiometer
const int MOTOR_PIN = 6;  // Pin for Motor

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

CANMessage messages2[] = {
  { 0x003cb, { createFrame("36c6cfa851bcf5a6"), createFrame("321c2efd9f277e14") }, 2 },
  { 0x00003, { createFrame("00ec48ff010cd67c") }, 1 },
  { 0x00004, { createFrame("b35c8320c3c0d67c") }, 1 },
  { 0x00201, { createFrame("6a27619d34e267f3"), createFrame("85025930fffebb0c") }, 2 },
  { 0x001e0, { createFrame("c827ecc77ac161a3"), createFrame("4f78ca00af144163") }, 2 },
  { 0x000c8, { createFrame("b44537645a32987c"), createFrame("a26188f3b5875801") }, 2 },
  { 0x0007b, { createFrame("a7c3a177468fe06f") }, 1 },
  { 0x005a4, { createFrame("0dd4744ccc4f10e8"), createFrame("050a246263ee8971"), createFrame("593991e31a14ad1d") }, 3 },
  { 0x00340, { createFrame("e10ba1f9498c67aa") }, 1 },
  { 0x0031c, { createFrame("e923b8786ce3b28d"), createFrame("0a2487be1e1db296"), createFrame("2de992e30ece8538") }, 3 },
};

int messageCount2 = sizeof(messages2) / sizeof(messages2[0]);
struct can_frame RecvCan2;
MCP2515 mcp2515_2(10);  // SPI CS Pin

void setup() {
  Serial.begin(500000);
  pinMode(POT_PIN, INPUT);
  pinMode(MOTOR_PIN, OUTPUT);

  SPI.begin();
  mcp2515_2.reset();
  mcp2515_2.setBitrate(CAN_1000KBPS, MCP_8MHZ);
  mcp2515_2.setNormalMode();

}

String byteToHex(byte b) {
  String hexStr = String(b, HEX);
  if (hexStr.length() < 2) {
    hexStr = "0" + hexStr;
  }
  return hexStr;
}

void loop() {
  int potValue = analogRead(POT_PIN);             // Read potentiometer value
  int potByte = map(potValue, 0,1023, 0, 255);

  for (int i = 0; i < messageCount2; i++) {
    CANMessage msg = messages2[i];
    int randomDataIndex = random(0, msg.dataCount);
    can_frame canMsg2 = msg.data[randomDataIndex];
    canMsg2.can_id = msg.id;

    if (msg.id == 0x00003) {
      canMsg2.can_id = 0x03;
      canMsg2.data[0] = potByte;
      mcp2515_2.sendMessage(&canMsg2);
      delay(20);
    } 
    else {
      mcp2515_2.sendMessage(&canMsg2);
    }
    delay(5);  // Random delay between 1 to 10 milliseconds

    // Check for received CAN messages
    if (mcp2515_2.readMessage(&RecvCan2) == MCP2515::ERROR_OK) {
      if (RecvCan2.can_id == 0x01) {
        analogWrite(6, RecvCan2.data[0]);  // Map byte 0 value to motor
        mcp2515_2.sendMessage(&RecvCan2);
        delay(5);
      }
    }
  }
}
