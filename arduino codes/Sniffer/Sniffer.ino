#include <mcp2515.h>
#include <SPI.h>

MCP2515 mcp2515(10); // Set your CS pin here
 struct can_frame canMsg;
 struct can_frame canMsg1;

void setup() {
  Serial.begin(500000); // Initialize serial communication at 500000 baud rate
  SPI.begin();
  mcp2515.reset();
  mcp2515.setBitrate(CAN_1000KBPS, MCP_8MHZ); // Set bitrate to 1000kbps
  mcp2515.setNormalMode();
  Serial.println("CAN Sniffer ready");
}

void loop() {
  // Check for serial data
  if (Serial.available() > 0) {
    String serialData = Serial.readStringUntil('\n');
    if (serialData.length() == 6) { // 3 characters for ID and 3 characters for value
      String idString = serialData.substring(0, 3);
      String valueString = serialData.substring(3, 6);
    
      int canID = strtol(idString.c_str(), NULL, 16);
      int value = strtol(valueString.c_str(), NULL, 10);

      canMsg1.can_id = canID;
      canMsg1.can_dlc = 1; // Data length code, assuming we're only sending 1 byte
      canMsg1.data[0] = value;
  }}

  // Sniffer functionality remains unchanged
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

  if (canMsg1.data[0] != 0){
    mcp2515.sendMessage(&canMsg1);
  }
}
