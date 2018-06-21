#ifndef TWOROW_UDP
#define TWOROW_UDP

#include <WiFiUdp.h>
#include <ESP8266WiFi.h> // biblioteca para usar as funções de Wifi do módulo ESP8266

// wifi connection variables
const char* ssid = "example";
const char* password = "example";
bool wifiConnected = false;

// UDP variables
unsigned int localPort = 1885;
WiFiUDP UDP;
bool udpConnected = false;
char packetBuffer[UDP_TX_PACKET_MAX_SIZE]; //buffer to hold incoming packet,


bool connectUDP(){
  bool state = false;
  if(UDP.begin(localPort) == 1){
    state = true;
  }
  return state;
}

// connect to wifi – returns true if successful or false if not
bool connectWifi(){
  bool state = true;
  int i = 0;
  WiFi.begin(ssid, password);
  delay(1200);
  return (bool) (WiFi.status() == WL_CONNECTED);
}

bool wifi_connect(){
  wifiConnected = (bool) connectWifi(); 
  return wifiConnected;
}

bool udp_connect(){
  udpConnected = (bool) connectUDP();
  return udpConnected;
}

#endif
