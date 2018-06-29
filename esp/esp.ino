#include <Wire.h> // Biblioteca para permitir a comunicação com dispositivos I2C/TWI
#include <ESP8266WiFi.h> // biblioteca para usar as funções de Wifi do módulo ESP8266
#include <ArduinoJson.h>
#include <WiFiUdp.h>
#include <stdlib.h>

#include "i2c.h"
#include "imu.h"
#include "helpers.h"

float serialized_data[N_IMUS * 9 + 1];
unsigned char msg[MSG_SIZE] = "acknowledged";
unsigned char *msg_ptr;

IMU imu;

long now = millis();
long last_msg_time = 0;
long tmp;

void err_connection(char *stuff, int wait){
  Serial.print(F("[ERROR] Connection failed for "));
  Serial.println(stuff);
  Serial.print(F("Retrying in "));
  Serial.print(wait/1000.0);
  Serial.println(wait/1000.0 < 2 ? " second." : " seconds");
  delay(wait);
}

void succ_connection(char *stuff){
  Serial.print(F("[SUCCESS] Connected with "));
  Serial.println(stuff);
  Serial.println();
}

void test(char *stuff, bool (*testfunc)(void), int wait){
  Serial.print(F("Testing connection for "));
  Serial.println(stuff);
  while(!testfunc()) err_connection(stuff, wait);
  succ_connection(stuff);
}

void setup_suit(){
  build_imu(&imu, 5);
  register_imus();
  deactivate_mpu_hibernate_mode();

  test("MPU6500", test_mpu_connection, 1000);
  delay(100);  

  setup_imus();
  delay(10);

  test("AK8963", test_magnet_connection, 1000);
  delay(100);
}

void setup_i2c(){
  Serial.println("Starting I2C");
  initialize_i2c();
  Serial.println();
}

void setup_serial(){
  Serial.begin(115200); // Abrindo o canal de comunicação serial a 115200 baudios/segundo
  delay(100);
}

void setup_wifi(){
  test("Wifi", wifi_connect, 5000);
  test("UDP", udp_connect, 1000);
}

void setup_tworow(){
  test("2RSystem", tworow_connect, 1000);
}

void write_message(){
  get_imu_serialized_data(serialized_data);
  msg_ptr = msg;
  for(int i = 0; i < N_IMUS * 9; i++) {
    sprintf((char *) msg_ptr, "%f", serialized_data[i]); 
    msg_ptr += sizeof(float);
    if(*(msg_ptr - 1) == '.'){
      *msg_ptr = '0';
      msg_ptr++;
    }

    if(i < N_IMUS * 9){
      *msg_ptr = ';';
      msg_ptr++;
    }
  }
  *(msg_ptr++) = '0';
  *(msg_ptr) = '\0';

  now = millis();
  long elapsed = now - last_msg_time;
  long now_delay = elapsed > desired_delay ? 0 : desired_delay - elapsed;
  delay(now_delay);

  tmp = last_msg_time;
  last_msg_time = millis();

  Serial.print(last_msg_time - tmp);
  Serial.print(": ");
  Serial.println((char *) msg);
  tworow_write(msg);
}

void register_imus(){
  register_imu(&imu);
}

void setup() {
  delay(2000);
  setup_serial();
  Serial.println("Starting 2RE-Kernel");
  Serial.println();
  setup_i2c();
  setup_wifi();
  setup_suit(); 
  setup_tworow();
}

void loop() {
  update_all_imus();
  write_message();
  delay(5);
}

