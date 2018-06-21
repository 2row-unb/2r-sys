#ifndef TWOROW_HELPERS
#define TWOROW_HELPERS

#include "udp.h"
#include "mqttsn.h"
#include "tworow_config.h"

void tworow_write(unsigned char *buff){
  mqttsn_publish(&client, ek_topic, buff);
}

bool tworow_connect(){
  return mqttsn_connect(&client);
}

bool wifi_connect(){
  wifiConnected = (bool) connectWifi(wifi_ssid, wifi_password); 
  return wifiConnected;
}

bool udp_connect(){
  udpConnected = (bool) connectUDP(udp_port);
  return udpConnected;
}

#endif
