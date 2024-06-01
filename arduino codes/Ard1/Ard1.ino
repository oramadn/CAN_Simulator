#include <SPI.h>
#include <mcp2515.h>

const int POT_PIN = A5;   // Analog pin for potentiometer
const int LED_PIN = 6;    // Pin for LED

struct CANMessage {
  uint32_t id;
  can_frame data[2];
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

CANMessage messages1[] = {
  { 0x00001, { createFrame("00cc8b6e5c0df0a8") }, 1 },  // Initial data with the first byte set to 00
  { 0x00261, { createFrame("c52456ed02862383"), createFrame("c41a8b1b7de3fe04") }, 2 },
  { 0x005c0, { createFrame("6309bfa48bf27022"), createFrame("5f92c560a0437e10") }, 2 },
  { 0x001fb, { createFrame("2289a3bbc29d987f"), createFrame("5fb983cd8030477e") }, 2 },
  { 0x0066a, { createFrame("bbcf776eab8c3528"), createFrame("7573de139e4b4250") }, 2 },
  { 0x00794, { createFrame("f747b6bfd203a5ff"), createFrame("474d7699e0623e7c") }, 2 },
  { 0x0049f, { createFrame("79c8417647511f29") }, 1 },
  { 0x0030f, { createFrame("08a4cc2a8f9af92f"), createFrame("c6cf73f4c539ce49") }, 2 },
  { 0x00095, { createFrame("cd27b98d9be41ac7"), createFrame("a9532c24d2be7a35") }, 2 },
  { 0x00381, { createFrame("36f9138aaefacac9"), createFrame("04e04ae97d1334d6") }, 2 },
};

int messageCount1 = sizeof(messages1) / sizeof(messages1[0]);
struct can_frame RecvCan1;
MCP2515 mcp2515_1(10);  // SPI CS Pin

void setup() {
  Serial.begin(500000);
  pinMode(POT_PIN, INPUT);
  pinMode(LED_PIN, OUTPUT);

  SPI.begin();
  mcp2515_1.reset();
  mcp2515_1.setBitrate(CAN_1000KBPS, MCP_8MHZ);
  mcp2515_1.setNormalMode();

  Serial.println("MCP2515 Initialized.");
}

String byteToHex(byte b) {
  String hexStr = String(b, HEX);
  if (hexStr.length() < 2) {
    hexStr = "0" + hexStr;
  }
  return hexStr;
}

void loop() {
  for (int i = 0; i < messageCount1; i++) {
    CANMessage msg = messages1[i];
    int randomDataIndex = random(0, msg.dataCount);
    can_frame canMsg1 = msg.data[randomDataIndex];
    canMsg1.can_id = msg.id;

    if (msg.id == 0x00001) {
      int potValue = analogRead(5);  // Read potentiometer value
      canMsg1.data[0] = map(potValue, 0, 1023, 0, 255);  // Map potentiometer value to 0-255 range
      canMsg1.can_id = 0x01;
      canMsg1.can_dlc = 8;
      mcp2515_1.sendMessage(&canMsg1);
      
      delay(5);
    } else {
      mcp2515_1.sendMessage(&canMsg1);
      delay(5);  // Random delay between 1 to 20 milliseconds
    }

      // Check for received CAN messages
  if (mcp2515_1.readMessage(&RecvCan1) == MCP2515::ERROR_OK) {
    if (RecvCan1.can_id == 0x02) {
      analogWrite(6,RecvCan1.data[0]);  // Set LED brightness
      mcp2515_1.sendMessage(&RecvCan1);
      delay(2);
    }
  }
  }


}
