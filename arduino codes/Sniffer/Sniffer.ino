#include <mcp2515.h>
#include <SPI.h>

MCP2515 mcp2515(10);  // Set your CS pin here
void setup() {
  Serial.begin(500000);  // Initialize serial communication at 500000 baud rate
  while (Serial.available() > 0) {
    Serial.read(); // Clear the buffer
  }
  SPI.begin();
  mcp2515.reset();
  mcp2515.setBitrate(CAN_1000KBPS, MCP_8MHZ);  // Set bitrate to 500kbps
  mcp2515.setNormalMode();
  Serial.println("CAN Sniffer ready");
}

void loop() {
  struct can_frame canMsg;
  if (mcp2515.readMessage(&canMsg) == MCP2515::ERROR_OK) {
    // Successfully received a CAN message
    char output[128];
    int len = sprintf(output, "{\"id\":\"%03X\",\"data\":\"", canMsg.can_id);
    for (int i = 0; i < canMsg.can_dlc; i++) {
      len += sprintf(output + len, "%02X", canMsg.data[i]);
    }
    sprintf(output + len, "\"}");
    Serial.println(output);
  }
  
}

