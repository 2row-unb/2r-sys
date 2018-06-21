#ifndef TWOROW_CONFIG
#define TWOROW_CONFIG

#include "udp.h"
#include "mqttsn.h"

// wifi connection variables
const char* wifi_ssid = "2ROW-PRIVATE";
const char* wifi_password = "xxx";

// Custom variables for TWOROW SYSTEM
char udp_host[] = "192.168.25.86";
unsigned int udp_port = 1885;
MQTTSNClient client = {"suit", udp_host, udp_port};
unsigned char ek_topic[] = "ek";

// boolean variables
bool wifiConnected = false;
bool udpConnected = false;

const long desired_delay = 10;

#endif
