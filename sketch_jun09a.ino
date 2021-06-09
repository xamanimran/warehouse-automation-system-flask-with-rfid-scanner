/*
PINOUT:
RC522 MODULE    Uno/Nano     MEGA
SDA             D10          D9
SCK             D13          D52
MOSI            D11          D51
MISO            D12          D50
IRQ             N/A          N/A
GND             GND          GND
RST             D9           D8
3.3V            3.3V         3.3V
*/

#include <SPI.h>
#include <MFRC522.h>
constexpr uint8_t SS_PIN = 9;
constexpr uint8_t RST_PIN = 8;

MFRC522 rfid(SS_PIN,RST_PIN);
MFRC522::MIFARE_Key key;
String tag;

void setup() {
  Serial.begin(9600);
  Serial.println("Starting the RFID Reader...");
  SPI.begin();
  rfid.PCD_Init();
}
void loop() {

  if(! rfid.PICC_IsNewCardPresent())
  {
    return;
  }
  if(rfid.PICC_ReadCardSerial())
  {
    for(byte i=0;i<4;i++)
    {
      tag +=rfid.uid.uidByte[i];
    }
    Serial.println(tag);
    tag="";
    rfid.PICC_HaltA();
    rfid.PCD_StopCrypto1();
  }
  
  }
