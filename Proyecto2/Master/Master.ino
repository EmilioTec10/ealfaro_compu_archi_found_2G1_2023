#include <SPI.h>

void setup (void)
{
  Serial.begin(115200);
  digitalWrite(SS, HIGH);  // ensure SS stays high for now
  SPI.begin ();
  delay(100);
  digitalWrite(SS, LOW);    // SS is pin 10
  SPI.setClockDivider(SPI_CLOCK_DIV128);  //125 kbits/sec
  //----------------------------------------------------
  SPDR = 0x23;
  while(bitRead(SPSR, SPIF) != HIGH)//wait until SPDR has got data
    ;
  byte RXBuffer = SPDR;
  Serial.println(RXBuffer, HEX);  //shows: 67 has come from Slave
}

void loop()
{
  
}
