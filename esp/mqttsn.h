#ifndef TWOROW_MQTTSN
#define TWOROW_MQTTSN

//#include <stdio.h>
#include <string.h>
#include "udp.h"

#define MSG_SIZE 200

typedef enum MsgType {
  ADVERTISE, SEARCHGW, GWINFO, reserved_,
  CONNECT, CONNACK, WILLTOPICREQ, WILLTOPIC,
  WILLMSGREQ, WILLMSG, REGISTER, REGACK,
  PUBLISH, PUBACK, PUBCOMP, PUBREC, PUBREL, reserved__,
  SUBSCRIBE, SUBACK, UNSUBSCRIBE, UNSUBACK, PINGREQ,
  PINGRESP, DISCONNECT, reserved___, WILLTOPICUPD,
  WILLTOPICRESP, WILLMSGUPD, WILLMSGRESP
} MsgType;

typedef enum ReturnCode {
  ACCEPTED, CONGESTION, INVALID_TOPIC_ID, REJECTED
} ReturnCode;


typedef struct Flags {
  int dup;
  int qos;
  int retain;
  int will;
  int clean_session;
  int topic_id_type;
} Flags;

typedef struct MessageHeader {
  unsigned char len;
  unsigned short fixed_len;
  MsgType msg_type;
} MessageHeader;

typedef struct Publish {
  MessageHeader mh;
  Flags flags;
  unsigned char topic_id[2];
  unsigned short msg_id;
  unsigned char buff[MSG_SIZE];
} Publish;

typedef struct Connect {
  MessageHeader mh;
  Flags flags;
  unsigned char protocol_id;
  unsigned short duration;
  unsigned char client_id[23];
} Connect;

typedef struct Connack {
  MessageHeader mh;
  ReturnCode rc;
} Connack;

typedef struct MQTTSNClient {
  unsigned char client_id[23];
  char *host;
  unsigned int port;
} MQTTSNClient;



// Custom variables for TWOROW SYSTEM
char udp_host[] = "192.168.25.99";
MQTTSNClient client = {"luan", udp_host , 1885};
unsigned char ek_topic[] = "ek";


void encode_flags(Flags *flags, unsigned char *s_flags){
  *s_flags = (unsigned char) 0;
  *s_flags |= (flags->dup << 7);
  *s_flags |= (flags->qos << 5);
  *s_flags |= (flags->retain << 4);
  *s_flags |= (flags->will << 3);
  *s_flags |= (flags->clean_session << 2);
  *s_flags |= (flags->topic_id_type);
}

MessageHeader decode_message_header(unsigned char *s_mh){
  MessageHeader mh;
  unsigned int len = (unsigned int) *s_mh;
  s_mh++;
  if(len == 1){
    mh.len = 1;
    mh.fixed_len = (unsigned short) (256 * s_mh[0] + s_mh[1]);
    mh.msg_type = (MsgType) s_mh[2];
  } else {
    mh.msg_type = (MsgType) *s_mh;
  }

  return mh;
}

Connack decode_connack(unsigned char * buff){
  Connack connack; 
  connack.mh = decode_message_header(buff);
  connack.rc = (ReturnCode) buff[2];
  return connack;
}

int encode_message_header(MessageHeader *mh, unsigned char *s_mh){
  *s_mh = mh->len;
  s_mh++;
  if(mh->len == (char) 1){
    *s_mh = mh->fixed_len;
    s_mh+=2;
    *s_mh = mh->msg_type;
    return 4;
  } else {
    *s_mh = mh->msg_type;
    return 2;
  }
}

int trace_cpy(unsigned char *src, unsigned char* dest){
  strcpy((char *) dest, (char *) src);
  return (int) strlen((char *) src);
}

void encode_connect(Connect *conn, unsigned char *msg){
  msg += encode_message_header(&(conn->mh), msg);
  encode_flags(&(conn->flags), msg);
  msg++;
  *msg = (char) conn->protocol_id;
  msg++;
  *(msg++)= conn->duration / 256;
  *(msg++)= conn->duration % 256;
  strcpy((char *) msg, (char *) conn->client_id);
}

void build_tworow_flags(Flags *flags){
  flags->dup = 0;
  flags->qos = 0;
  flags->retain = 0;
  flags->will = 0;
  flags->clean_session = 1;
  flags->topic_id_type = 0b10;
}

void set_mh_len(MessageHeader *mh, unsigned short header_max_size,
  unsigned char *volatile_src, unsigned char *volatile_dest){
  mh->fixed_len = header_max_size + trace_cpy(volatile_src, volatile_dest);
  if(mh->fixed_len < 257){
    mh->len = mh->fixed_len - 2;
    mh->fixed_len -= 2;
  } else {
    mh->len = 1;
  }
  
}

void build_tworow_connection(Connect *conn, MQTTSNClient *client){
  conn->mh.msg_type = CONNECT;
  set_mh_len(&(conn->mh), 8, client->client_id, conn->client_id);
  build_tworow_flags(&(conn->flags));
  conn->protocol_id = 1;
  conn->duration = 511;
}

bool mqttsn_connect(MQTTSNClient *client){
  Connect conn;
  unsigned char buff[500];
  build_tworow_connection(&conn, client);
  encode_connect(&conn, buff);
  UDP.beginPacket(client->host, client->port);
  UDP.write((char *) buff);
  UDP.endPacket();

  delay(500);
  UDP.read(buff, 500);
  Connack cann = decode_connack(buff);
  return cann.rc == ACCEPTED;
}

void encode_publish(Publish *pub, unsigned char * buff){
  buff += encode_message_header(&(pub->mh), buff);
  encode_flags(&(pub->flags), buff);
  buff++;
  *(buff++)= pub->topic_id[0];
  *(buff++)= pub->topic_id[1];
  *(buff++)= pub->msg_id;
  buff++;
  strcpy((char *) buff, (char *) pub->buff);
}

void build_tworow_publish(Publish *pub, unsigned char *topic, unsigned char *buff){
  pub->mh.msg_type = PUBLISH;
  set_mh_len(&(pub->mh), 9, buff, pub->buff);
  build_tworow_flags(&(pub->flags));
  pub->topic_id[0] = topic[0]; pub->topic_id[1] = topic[1];
  pub->msg_id = 0;
}

bool mqttsn_publish(MQTTSNClient *client, unsigned char * topic, unsigned char * buff){
  Publish pub;
  unsigned char encoded_pub[500];
  build_tworow_publish(&pub, topic, buff);
  encode_publish(&pub, encoded_pub);
  UDP.beginPacket(client->host, client->port);
  UDP.write((char *) encoded_pub, pub.mh.fixed_len);
  UDP.endPacket();
}

void tworow_write(unsigned char *buff){
  mqttsn_publish(&client, ek_topic, buff);
}

bool tworow_connect(){
  return mqttsn_connect(&client);
}

#endif
