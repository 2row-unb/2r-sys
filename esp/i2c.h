#ifndef TWOROW_I2C
#define TWOROW_I2C

#include <Wire.h>

void void_write(uint8_t Address, uint8_t Register, uint8_t Data){
  Wire.beginTransmission(Address);
  Wire.write(Register);
  Wire.write(Data);
  Wire.endTransmission();
}

void void_read(uint8_t Address, uint8_t Register, uint8_t Nbytes, uint8_t* Data){
  Wire.beginTransmission(Address);
  Wire.write(Register);
  Wire.endTransmission();

  Wire.requestFrom(Address, Nbytes);
  uint8_t index = 0;
  while (Wire.available()) Data[index++] = Wire.read();
}

void initialize_i2c(void){
  Wire.begin();
}

#endif
