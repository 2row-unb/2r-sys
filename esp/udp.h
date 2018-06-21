#ifndef TWOROW_UDP
#define TWOROW_UDP

#include <WiFiUdp.h>
#include <ESP8266WiFi.h> // biblioteca para usar as funções de Wifi do módulo ESP8266


WiFiUDP UDP;
char packetBuffer[UDP_TX_PACKET_MAX_SIZE]; //buffer to hold incoming packet,


bool connectUDP(int udp_port){
  bool state = false;
  if(UDP.begin(udp_port) == 1){
    state = true;
  }
  return state;
}

// connect to wifi – returns true if successful or false if not
bool connectWifi(const char *ssid, const char *password){
  bool state = true;
  int i = 0;
  WiFi.begin(ssid, password);
  delay(1200);
  return (bool) (WiFi.status() == WL_CONNECTED);
}

#endif
