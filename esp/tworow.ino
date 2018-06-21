#include <Wire.h> // Biblioteca para permitir a comunicação com dispositivos I2C/TWI
#include <ESP8266WiFi.h> // biblioteca para usar as funções de Wifi do módulo ESP8266
#include <WiFiUdp.h>
#include <stdlib.h>

#include "imu.h"
#include "i2c.h"
#include "mux.h"
#include "helpers.h"

double serialized_data[N_IMUS * 9];
unsigned char msg[MSG_SIZE] = "acknowledged";
unsigned char *msg_ptr;

long now = millis();
long last_msg_time = 0;
long tmp = 0;

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

void setup_imus(){
  deactivate_mpu_hibernate_mode();

  test("MPU6500", test_mpu_connection, 1000);
  delay(100);  

  setup_imu();
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

  now = millis();
  long elapsed = now - last_msg_time;
  long now_delay = elapsed > desired_delay ? 0 : desired_delay - elapsed;
  delay(now_delay);

  tmp = last_msg_time;
  last_msg_time = millis();

  Serial.println(last_msg_time - tmp);
  tworow_write(msg);
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

