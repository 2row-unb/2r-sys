#include <Wire.h> // Biblioteca para permitir a comunicação com dispositivos I2C/TWI
#include <ESP8266WiFi.h> // biblioteca para usar as funções de Wifi do módulo ESP8266
#include <ArduinoJson.h>
#include <WiFiUdp.h>
#include <stdlib.h>

#include "imu.h"
#include "i2c.h"
#include "mux.h"
#include "udp.h"
#include "mqttsn.h"

#define MSG_SIZE 200

double serialized_data[N_IMUS * 9];
unsigned char msg[MSG_SIZE] = "acknowledged";
unsigned char *msg_ptr;

long now = millis();
long last_msg_time = 0;

void err_connection(char *stuff){
  Serial.print(F("[ERROR] Connection failed for "));
  Serial.println(stuff);
  Serial.println(F("Retrying in 1 second."));
  delay(1000);
}

void succ_connection(char *stuff){
  Serial.print(F("[SUCCESS] Connected with "));
  Serial.println(stuff);
  Serial.println();
}

void test(char *stuff, bool (*testfunc)(void)){
  Serial.print(F("Testing connection for "));
  Serial.println(stuff);
  while(!testfunc()) err_connection(stuff);
  succ_connection(stuff);
}

void setup_imus(){
  deactivate_mpu_hibernate_mode();

  test("MPU6500", test_mpu_connection);
  delay(100);  

  setup_imu();
  delay(10);

  test("AK8963", test_magnet_connection);
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
  test("Wifi", wifi_connect);
  test("UDP", udp_connect);
}

void setup_tworow(){
  test("2RSystem", tworow_connect);
}

void write_message(){
  get_serialized_data(serialized_data);
  msg_ptr = msg;
  for(int i = 0; i < 18; i++) {
    sprintf((char *) msg_ptr, "%f", serialized_data[i]); 
    msg_ptr += sizeof(double);
    if(*(msg_ptr - 1) == '.'){
      *msg_ptr = '0';
      msg_ptr++;
    }

    if(i < 17){
      *msg_ptr = ';';
      msg_ptr++;
    }
  }

  *msg_ptr = '\0';
  long now = millis();
  if (now - last_msg_time > 2) {
    Serial.print("Time elapsed: ");
    Serial.println(now - last_msg_time);
    last_msg_time = now;
    tworow_write(msg);
    Serial.println((char *) msg);
  }
}

void setup() {
  delay(2000);
  Serial.println("Starting 2RE-Kernel");
  Serial.println();
  setup_serial();
  setup_i2c();
  setup_imus(); 
  setup_mux_pins();
  setup_wifi();
  setup_tworow();
}

void loop() {
  changeMux(1, 0, 0);
  update_imu_data(0);
  changeMux(0, 1, 0);
  update_imu_data(1);
  write_message();
}

