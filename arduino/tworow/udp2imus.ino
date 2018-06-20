#include <Wire.h> // Biblioteca para permitir a comunicação com dispositivos I2C/TWI
#include <ESP8266WiFi.h> // biblioteca para usar as funções de Wifi do módulo ESP8266
#include <ArduinoJson.h>
#include <WiFiUdp.h>
#include <stdlib.h>

//----------------------------------------------------------------------------
//  FUNCAO ESCRITA DADOS [Endereco(8bits) | Regitrador(8bits) | Dado(8bits)]
//----------------------------------------------------------------------------
//Address = 0x68 (Endereco da MPU9250 "acel e giro") ou 0x0C (Endereco do Magnetômetro)
//Register = 0x1C ou 0x1B (Endereco do registrador a acessar na MPU9250 "acel e giro") ou 0x (Endereco do Magnetômetro)
//Data = Nome_Data (Dado que vai ser configurado)


// wifi connection variables
const char* ssid = "lappisair";
const char* password = "<%=lappiscontainer=%>";
boolean wifiConnected = false;

// UDP variables
unsigned int localPort = 1883;
WiFiUDP UDP;
boolean udpConnected = false;
char packetBuffer[UDP_TX_PACKET_MAX_SIZE]; //buffer to hold incoming packet,
char msg[100] = "acknowledged"; // a string to send back
char msg2[] = "OOOiiiii";
long lastMsg = 0;

void void_write(uint8_t Address, uint8_t Register, uint8_t Data){
  Wire.beginTransmission(Address); //Inicia comunicação com o endereço I2C do sensor   
  Wire.write(Register); //Define o endereço inicial
  Wire.write(Data); //Escreve o dado a configurar
  Wire.endTransmission(); //Deixa aberta a comunicação com o endereço I2C do sensor
}
//----------------------------------------------------------------------------
//  FUNCAO LEITURA DADOS [Endereco(8bits) | Regitrador(8bits) | N°Bytes(#) | Dado(8bits)]
//----------------------------------------------------------------------------
//Address = 0x68 (Endereco da MPU9250 "acel e giro") ou 0x0C (Endereco do Magnetômetro)
//Register = 0x3B (Endereco do registrador a acessar na MPU9250 "acel e giro") ou 0x03 (Endereco do Magnetômetro)
//Nbytes = 6 para acelerômetro + 2 termometro + 6 girôscopio ou 6 magnetometro (Numero de bytes a transportar)
//Data = Buffer (Nome da variavel onde vai ser salvados os bytes transportados)

void void_read(uint8_t Address, uint8_t Register, uint8_t Nbytes, uint8_t* Data){
  Wire.beginTransmission(Address); //Inicia comunicação com o endereço I2C do sensor   
  Wire.write(Register); //Define o endereço inicial
  Wire.endTransmission(); //Deixa aberta a comunicação com o endereço I2C do sensor

  // Read Nbytes
  Wire.requestFrom(Address, Nbytes); //Solicita os dados de 14 endereços de 8 bits do sensor (6 do Acelerômetro, 2 do Termometro e 6 do Girôscopio))
  uint8_t index = 0; // Índice do vetor, o qual chegará até Nbytes
  while (Wire.available()) //Enquanto fique disponível a conexao com os sensores
    Data[index++] = Wire.read(); //Vetor onde vai armazenar os dados dos sensores
}

//----------------------------------------------------------------------------
//                       DEFINICOES DO DATASHEET DA MPU9250
//----------------------------------------------------------------------------

// Enderecos dos escravos
#define    MPU6500_address            0x68 // Endereço da MPU6500 (giroscópio e acelerômetro)
#define    AK8963_address             0x0C // Endereço do magnetômetro AK8963

// Escalas do girôscopio
#define    GYRO_FULL_SCALE_250_DPS    0x00 // SCALE_250 (°/s) = 0 (0x00 = 000|00|000)
#define    GYRO_FULL_SCALE_500_DPS    0x08 // SCALE_500 (°/s) = 1 (0x08 = 000|01|000)
#define    GYRO_FULL_SCALE_1000_DPS   0x10 // SCALE_1000 (°/s) = 2 (0x10 = 000|10|000)
#define    GYRO_FULL_SCALE_2000_DPS   0x18 // SCALE_2000 (°/s) = 3 (0x18 = 000|11|000)

// Escalas do acelerômetro
#define    ACC_FULL_SCALE_2_G        0x00 // SCALE_2_G (g) = 0 (0x00 = 000|00|000)
#define    ACC_FULL_SCALE_4_G        0x08 // SCALE_4_G (g) = 1 (0x08 = 000|01|000)
#define    ACC_FULL_SCALE_8_G        0x10 // SCALE_8_G (g) = 2 (0x10 = 000|10|000)
#define    ACC_FULL_SCALE_16_G       0x18 // SCALE_16_G (g) = 3 (0x18 = 000|11|000)

// Escalas de conversao (As taxas de conversão são especificadas na documentação)
#define SENSITIVITY_ACCEL     2.0/32768.0             // Valor de conversão do Acelerômetro (g/LSB) para 2g e 16 bits de comprimento da palavra
#define SENSITIVITY_GYRO      250.0/32768.0           // Valor de conversão do Girôscopio ((°/s)/LSB) para 250 °/s e 16 bits de comprimento da palavra
#define SENSITIVITY_TEMP      333.87                  // Valor de sensitividade do Termometro (Datasheet: MPU-9250 Product Specification, pag. 12)
#define TEMP_OFFSET           21                      // Valor de offset do Termometro (Datasheet: MPU-9250 Product Specification, pag. 12)
#define SENSITIVITY_MAGN      (10.0*4800.0)/32768.0   // Valor de conversão do Magnetômetro (mG/LSB) para 4800uT, 16 bits de comprimento da palavra e conversao a Gauss (10mG = 1uT)

//----------------------------------------------------------------------------
//                           DECLARACAO DE VARIAVEIS
//----------------------------------------------------------------------------
bool newMagData = false;

// Offsets de calibração (AQUI DEVEM IR OS VALORES DETERMINADOS NA CALIBRACAO PREVIA COM O CÓDIGO "calibracao.ino")
double offset_accelx = 1124.0, offset_accely = 474.00, offset_accelz = 16208.00;
double offset_gyrox = -464.50, offset_gyroy = -473.50, offset_gyroz = -152.00;
double offset_magnx = 128.50, offset_magny = -252.00, offset_magnz = 421.50;
double scale_magnx = 1.01, scale_magny = 0.96, scale_magnz = 1.03;

// Valores "RAW" de tipo inteiro
int16_t raw_accelx, raw_accely, raw_accelz;
int16_t raw_gyrox, raw_gyroy, raw_gyroz;
int16_t raw_temp;
int16_t raw_magnx, raw_magny, raw_magnz;

//Para 2 Imus
int16_t raw_accelx, raw_accely, raw_accelz;
int16_t raw_gyrox, raw_gyroy, raw_gyroz;
int16_t raw_temp;
int16_t raw_magnx, raw_magny, raw_magnz;

// Valores "RAW" de tipo double
double Raw_accelx, Raw_accely, Raw_accelz;
double Raw_gyrox, Raw_gyroy, Raw_gyroz;
double Raw_temp;
double Raw_magnx, Raw_magny, Raw_magnz;

// Saídas calibradas
/*double accelx, accely, accelz;
double gyrox, gyroy, gyroz;
double temp;
double magnx, magny, magnz;
*/
//Para 2 Imus
double accelx, accely, accelz, accelx2, accely2, accelz2;
double gyrox, gyroy, gyroz, gyrox2, gyroy2, gyroz2;
double temp, temp2;
double magnx, magny, magnz,magnx2, magny2, magnz2;

// Bytes
uint8_t data[1];
uint8_t GirAcel[14];
uint8_t Mag[7];

// Tempos
unsigned long t_ini_config, t_fim_config, t_ini_leitura, t_fim_leitura, t;

//                                                                ----------------------------------------------------------------------------
//                                                                                           INICIO DA FUNCAO 'SETUP'
//                                                                ----------------------------------------------------------------------------
void setup() {
t_ini_config = millis();
//.....................................................................
//                        Inicializacao I2C
//.....................................................................
Wire.begin(); //Inicializando comunicacao I2C   
Serial.begin(115200); // Abrindo o canal de comunicação serial a 115200 baudios/segundo
delay(100);
Serial.println("INICIALIZANDO A COMUNICACAO I2C");
Serial.println();

// Desativa modo de hibernação do MPU9250
void_write(MPU6500_address, 0x6B, 0x00); //PWR_MGMT_1 0x6B e CLK_SEL_PWR_MGMT_1 0x00 (// Desativa modo de hibernação da MPU9250, habilitando a opcao (Internal 20MHz oscillator))

Serial.println("TESTE DE CONEXAO PARA O GIROSCOPIO E O ACELEROMETRO");
Serial.println();
//.....................................................................
//        Quem sou eu para a MPU6500 (giroscópio e acelerômetro)
//.....................................................................
Serial.println("1. Teste de conexao da MPU6500..."); // Verifica a conexao
void_read(MPU6500_address, 0x75, 1, data); //WHO_AM_I_MPU6500 0x75
if (data[0] != 0x71) { // DEFAULT_REGISTER_WHO_AM_I_MPU6500 0x71
  Serial.println(F("Erro de conexao com a MPU6500"));
  Serial.print(F("Opaaa. Eu nao sou a MPU6500, Quem sou eu? :S. I am "));
  Serial.println(data[0],HEX);
  Serial.println("");
  while (1);
}else 
  Serial.println(F("Conexao bem sucedida com a MPU6500"));
  Serial.println(F("Oi, tudo joia?... Eu sou a MPU6500 XD"));
  Serial.println("");

delay(100);  

//.....................................................................
//        Configuracao dos sensores giroscópio e acelerômetro
//.....................................................................

// Configura o Girôscopio (Full Scale Gyro Range  = 250 deg/s)
void_write(MPU6500_address, 0x1B, GYRO_FULL_SCALE_250_DPS); //GYRO_CONFIG 0x1B //Registrador de configuracao do Girôscopio
// Configura o Acelerômetro (Full Scale Accelerometer Range  = 2g)
void_write(MPU6500_address, 0x1C, ACC_FULL_SCALE_2_G); // ACCEL_CONFIG 0x1C //Registrador de configuracao do Acelerômetro

//.....................................................................
//                Configuracao do sensor magnetômetro
//.....................................................................

// Desativa modo de hibernação do AK8963 (Habilita o Magnetômetro)
void_write(MPU6500_address, 0x37, 0x02); //INT_PIN_CFG 0x37 e BYPASS_EN 0x02 (0x02 = 000000|1|0) Habilita o enable para acessar ao Magnetômetro
// Configura o Magnetometro para alta resolucao (16 bits) e leituras continuas (8Hz)
void_write(AK8963_address, 0x0A, 0x16); //MAGN_CNTL 0x0A e BITS_OUTPUT_and_CONTINUOUS_MEASUREMENT_MODE_1 0x11 // "(0001|0010) = 0x12" : (16 bits output | continuous measurement mode 1 para 8Hz para velocidade das amostras)
delay(10);


Serial.println("TESTE DE CONEXAO PARA O MAGNETOMETRO ");
Serial.println();
//.....................................................................
//                Quem sou eu para o magnetômetro (AK8963)
//.....................................................................
Serial.println("2. Teste de conexao do AK8963..."); // Verifica a conexao
void_read(AK8963_address, 0x00, 1, data); // AK8963_address 0x0C e WHO_AM_I_AK8963 0x00
if (data[0] != 0x48) { // DEFAULT_REGISTER_WHO_AM_I_AK8963 0x48
  Serial.println(F("Erro de conexao com o AK8963"));
  Serial.print(F("Opaaa. Eu nao sou o AK8963, Quem sou eu? :S. I am "));
  Serial.println(data[0],HEX);
  Serial.println("");
  while (1);
}else 
  Serial.println(F("Conexao bem sucedida com o AK8963"));
  Serial.println(F("E ai, blz?... Eu sou o AK8963 XD"));
  Serial.println("");
        
delay(100);

t_fim_config = millis() - t_ini_config;
Serial.print("Tempo de inicializacao e configuracao dos sensores (giroscopio, acelerometro e magnetometro): "); 
Serial.println(t_fim_config);
Serial.println();

//Deifne output pins for Mux
  pinMode(MUX_A, OUTPUT);
  pinMode(MUX_B, OUTPUT);
  pinMode(MUX_C, OUTPUT);


// Initialise wifi connection
wifiConnected = connectWifi();

// only proceed if wifi connection successful
  if(wifiConnected){
  udpConnected = connectUDP();
    if (udpConnected){
  
    }
  }

}

void changeMux(int c, int b, int a) {
  digitalWrite(MUX_A, a);
  digitalWrite(MUX_B, b);
  digitalWrite(MUX_C, c);
}

//                                                                ----------------------------------------------------------------------------
//                                                                                            FIM DA FUNCAO 'SETUP'
//                                                                ----------------------------------------------------------------------------

//                                                                ----------------------------------------------------------------------------
//                                                                                           INICIO DA FUNCAO 'LOOP'
//                                                                ----------------------------------------------------------------------------

void loop() {
  
//t_ini_leitura = millis(); //HABILITAR PARA MEDIR O TEMPO DE MUESTREO DOS SENSORES
//  .....................................................................
//                 Leitura do giroscópio e do acelerômetro
//  .....................................................................
void_read(MPU6500_address, 0x3B, 14, GirAcel); // 0x3B é o endereco do ACCEL_XOUT_H
raw_accelx = (GirAcel[0] << 8 | GirAcel[1]);
raw_accely = (GirAcel[2] << 8 | GirAcel[3]);
raw_accelz = GirAcel[4] << 8 | GirAcel[5];
raw_temp = (GirAcel[6] << 8 | GirAcel[7]);
raw_gyrox = (GirAcel[8] << 8 | GirAcel[9]);
raw_gyroy = (GirAcel[10] << 8 | GirAcel[11]);
raw_gyroz = GirAcel[12] << 8 | GirAcel[13];

//  .....................................................................
//                        Leitura do magnetômetro
//  .....................................................................            
//void_write(MAG_ADDRESS, 0x0A, 0x11); //MAGN_CNTL 0x0A e BITS_OUTPUT_and_SINGLE_MEASUREMENT_MODE 0x11 // "(0001|0001) = 0x11" : (16 bits output | single measurement mode)
//delay(10);
void_read(AK8963_address, 0x02, 1, data); // ST1=0x02
newMagData = data[0]& 0x01;
if(newMagData == true) { // Aguarda o bit 'ready' do magnetômetro para configurar
  void_read(AK8963_address, 0x03, 7, Mag); // MAGN_XOUT_L = 0x03
  uint8_t c = Mag[6]; // End data read by reading ST2 register
  if(!(c & 0x08)) { // Check if magnetic sensor overflow set, if not then report data
    raw_magnx = (Mag[3] << 8 | Mag[2]); 
    raw_magny = (Mag[1] << 8 | Mag[0]); 
    raw_magnz = -(Mag[5] << 8 | Mag[4]);
  }
}

//t_fim_leitura = (millis() - t_ini_leitura) / 1000; //HABILITAR PARA MEDIR O TEMPO DE MUESTREO DOS SENSORES
//Serial.print("Tempo de amostragem (ms): "); 
//Serial.println((double)(t_fim_leitura, 4)); //HABILITAR PARA MEDIR A FREQUÊNCIA DE AMOSTRAGEM DOS SENSORES
//Serial.print("Taxa de amostragem (Hz): "); 
//Serial.println((double)(1 / t_fim_leitura)); 

//  .....................................................................
//                    Valores RAW de enteiros a double
//  .....................................................................
Raw_accelx = raw_accelx; Raw_accely = raw_accely; Raw_accelz = raw_accelz; 
Raw_gyrox = raw_gyrox; Raw_gyroy = raw_gyroy; Raw_gyroz = raw_gyroz;
Raw_temp = raw_temp;
Raw_magnx = raw_magnx; Raw_magny = raw_magny; Raw_magnz = raw_magnz;

//  .....................................................................
//                    Valores (calibrados) e escalizados
//  .....................................................................
accelx = (Raw_accelx - offset_accelx)* SENSITIVITY_ACCEL; accely = (Raw_accely - offset_accely) * SENSITIVITY_ACCEL; accelz = (Raw_accelz - (offset_accelz - (32768/2))) * SENSITIVITY_ACCEL;//g (32768/2 = 1g para a escala configurada +-2g)
gyrox = (Raw_gyrox - offset_gyrox) * SENSITIVITY_GYRO; gyroy = (Raw_gyroy - offset_gyroy) * SENSITIVITY_GYRO; gyroz = (Raw_gyroz - offset_gyroz) * SENSITIVITY_GYRO;//°/s
temp = (Raw_temp/SENSITIVITY_TEMP) + TEMP_OFFSET; //°C
magnx = ((Raw_magnx - offset_magnx) * scale_magnx) * SENSITIVITY_MAGN; magny = ((Raw_magny - offset_magny) * scale_magnx) * SENSITIVITY_MAGN; magnz = ((Raw_magnz - offset_magnz) * scale_magnx) * SENSITIVITY_MAGN; //mG

//Segunda IMU
   changeMux(0, 1, 0);
  //t_ini_leitura = millis(); //HABILITAR PARA MEDIR O TEMPO DE MUESTREO DOS SENSORES
  //  .....................................................................
  //                 Leitura do giroscópio e do acelerômetro
  //  .....................................................................
  void_read(MPU6500_address, 0x3B, 14, GirAcel); // 0x3B é o endereco do ACCEL_XOUT_H
  raw_accelx = (GirAcel[0] << 8 | GirAcel[1]);
  raw_accely = (GirAcel[2] << 8 | GirAcel[3]);
  raw_accelz = GirAcel[4] << 8 | GirAcel[5];
  raw_temp = (GirAcel[6] << 8 | GirAcel[7]);
  raw_gyrox = (GirAcel[8] << 8 | GirAcel[9]);
  raw_gyroy = (GirAcel[10] << 8 | GirAcel[11]);
  raw_gyroz = GirAcel[12] << 8 | GirAcel[13];

  //  .....................................................................
  //                        Leitura do magnetômetro
  //  .....................................................................
  //void_write(MAG_ADDRESS, 0x0A, 0x11); //MAGN_CNTL 0x0A e BITS_OUTPUT_and_SINGLE_MEASUREMENT_MODE 0x11 // "(0001|0001) = 0x11" : (16 bits output | single measurement mode)
  //delay(10);
  void_read(AK8963_address, 0x02, 1, data); // ST1=0x02
  newMagData = data[0] & 0x01;
  if (newMagData == true) { // Aguarda o bit 'ready' do magnetômetro para configurar
    void_read(AK8963_address, 0x03, 7, Mag); // MAGN_XOUT_L = 0x03
    uint8_t c = Mag[6]; // End data read by reading ST2 register
    if (!(c & 0x08)) { // Check if magnetic sensor overflow set, if not then report data
      raw_magnx = (Mag[3] << 8 | Mag[2]);
      raw_magny = (Mag[1] << 8 | Mag[0]);
      raw_magnz = -(Mag[5] << 8 | Mag[4]);
    }
  }

  //t_fim_leitura = (millis() - t_ini_leitura) / 1000; //HABILITAR PARA MEDIR O TEMPO DE MUESTREO DOS SENSORES
  //Serial.print("Tempo de amostragem (ms): ");
  //Serial.println((double)(t_fim_leitura, 4)); //HABILITAR PARA MEDIR A FREQUÊNCIA DE AMOSTRAGEM DOS SENSORES
  //Serial.print("Taxa de amostragem (Hz): ");
  //Serial.println((double)(1 / t_fim_leitura));

  //  .....................................................................
  //                    Valores RAW de enteiros a double
  //  .....................................................................
  Raw_accelx = raw_accelx; Raw_accely = raw_accely; Raw_accelz = raw_accelz;
  Raw_gyrox = raw_gyrox; Raw_gyroy = raw_gyroy; Raw_gyroz = raw_gyroz;
  Raw_temp = raw_temp;
  Raw_magnx = raw_magnx; Raw_magny = raw_magny; Raw_magnz = raw_magnz;

  //  .....................................................................
  //                    Valores (calibrados) e escalizados
  //  .....................................................................
  accelx2 = (Raw_accelx - offset_accelx) * SENSITIVITY_ACCEL; accely2 = (Raw_accely - offset_accely) * SENSITIVITY_ACCEL; accelz2 = (Raw_accelz - (offset_accelz - (32768 / 2))) * SENSITIVITY_ACCEL; //g (32768/2 = 1g para a escala configurada +-2g)
  gyrox2 = (Raw_gyrox - offset_gyrox) * SENSITIVITY_GYRO; gyroy2 = (Raw_gyroy - offset_gyroy) * SENSITIVITY_GYRO; gyroz2 = (Raw_gyroz - offset_gyroz) * SENSITIVITY_GYRO;//°/s
  temp2 = (Raw_temp / SENSITIVITY_TEMP) + TEMP_OFFSET; //°C
  magnx2 = ((Raw_magnx - offset_magnx) * scale_magnx) * SENSITIVITY_MAGN; magny2 = ((Raw_magny - offset_magny) * scale_magnx) * SENSITIVITY_MAGN; magnz2 = ((Raw_magnz - offset_magnz) * scale_magnx) * SENSITIVITY_MAGN; //mG


//  ....................................................................
//                           Imprimir valores
//  .....................................................................
/*
#if 1 //Dados cruos "RAW"  
  // Acelerometro
  Serial.print(raw_accelx * SENSITIVITY_ACCEL); Serial.print(",");
  Serial.print(raw_accely * SENSITIVITY_ACCEL); Serial.print(",");
  Serial.print(raw_accelz * SENSITIVITY_ACCEL); Serial.print(",");
            
  // Giroscopio
  Serial.print(raw_gyrox * SENSITIVITY_GYRO); Serial.print(",");
  Serial.print(raw_gyroy * SENSITIVITY_GYRO); Serial.print(",");
  Serial.print(raw_gyroz * SENSITIVITY_GYRO); Serial.print(",");
            
  //Termometro
  Serial.print((Raw_temp/SENSITIVITY_TEMP) + TEMP_OFFSET); Serial.print(",");
            
  // Magnetometro
  Serial.print(raw_magnx * SENSITIVITY_MAGN); Serial.print(",");
  Serial.print(raw_magny * SENSITIVITY_MAGN); Serial.print(",");
  Serial.print(raw_magnz * SENSITIVITY_MAGN); Serial.print(",");


#endif
 */      
#if 1 //Dados escalizados "Sensivity Range Scale"  
  // Acelerometro
  Serial.print(accelx); Serial.print(",");
  Serial.print(accely); Serial.print(",");
  Serial.print(accelz); Serial.print(",");
            
  // Giroscopio
  Serial.print(gyrox); Serial.print(",");
  Serial.print(gyroy); Serial.print(",");
  Serial.print(gyroz); Serial.print(",");
            
  //Termometro
  //Serial.print(temp); Serial.print(",");
            
  // Magnetometro
  Serial.print(magnx); Serial.print(",");
  Serial.print(magny); Serial.print(",");
  Serial.println(magnz); 
  Serial.println();
#endif


// check if the WiFi and UDP connections were successful
if(wifiConnected){
  if(udpConnected){
/*
// if there’s data available, read a packet
int packetSize = UDP.parsePacket();
  if(packetSize)
    {
      Serial.println("");
      Serial.print("Received packet of size ");
      Serial.println(packetSize);
      Serial.print("From ");
      */
      IPAddress remote = UDP.remoteIP();
      /*for (int i =0; i < 4; i++)
        {
          Serial.print(remote[i], DEC);
          if (i < 3)
            {
              Serial.print(".");
            }
        }*/
      //Serial.print(", port ");
      //Serial.println(UDP.remotePort());
      /*
      
      // read the packet into packetBufffer
      UDP.read(packetBuffer,UDP_TX_PACKET_MAX_SIZE);
      Serial.println("Contents:");
      Serial.print(packetBuffer);
*/
      //float aux[9]={accelx, accely, accelz, gyrox, gyroy, gyroz, magnx, magny, magnz};
      float aux[18]={accelx, accely, accelz, degree_to_rad(gyrox), degree_to_rad(gyroy), degree_to_rad(gyroz), magnx, magny, magnz,accelx2, accely2, accelz2, degree_to_rad(gyrox2), degree_to_rad(gyroy2), degree_to_rad(gyroz2), magnx2, magny2, magnz2};
      // send a reply, to the IP address and port that sent us the packet we received
      UDP.beginPacket(UDP.remoteIP(), UDP.remotePort());

       char *ptr = msg;
  for(int i = 0; i < 18; i++) {
      sprintf(ptr, "%f", aux[i]); 
      //printf("%f ", aux[i]);
      ptr += sizeof(float);
      if(*(ptr - 1) == '.'){
        *ptr = '0';
        ptr++;
      }
      if(i < 17){
        *ptr = ';';
        ptr++;
      }
  }
  //printf("\n");
  *ptr = '\0';
  
  long now = millis();
  if (now - lastMsg > 10) {
    lastMsg = now;
      UDP.write(msg);
      UDP.write(msg2);
      Serial.println(msg);
      UDP.endPacket();
    }
//delay(10);
                }
              }
}

// connect to UDP – returns true if successful or false if not
boolean connectUDP(){
boolean state = false;

Serial.println("");
Serial.println("Connecting to UDP");

if(UDP.begin(localPort) == 1){
  Serial.println("Connection successful");
  state = true;
  }
  else{
  Serial.println("Connection failed");
  }

return state;
}
// connect to wifi – returns true if successful or false if not
boolean connectWifi(){
boolean state = true;
int i = 0;
WiFi.begin(ssid, password);
Serial.println("");
Serial.println("Connecting to WiFi");

// Wait for connection
Serial.print("Connecting");
while (WiFi.status() != WL_CONNECTED) {
delay(500);
Serial.print(".");
if (i > 1){
  state = false;
  break;
}
i++;
}
if (state){
  Serial.println("");
  Serial.print("Connected to ");
  Serial.println(ssid);
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}
else {
  Serial.println("");
  Serial.println("Connection failed.");
}
return state;
}
