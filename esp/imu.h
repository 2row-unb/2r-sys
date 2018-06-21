// Datasheet definitions for MPU9250

#ifndef TWOROW_IMU
#define TWOROW_IMU

#include "i2c.h"

// Number of IMUs
#define N_IMUS 2

// Chip address
#define MPU6500_address 0x68 // MPU6500 (gyros and accel)
#define AK8963_address  0x0C // Magnet AK8963 address

// Gyro scales
#define GYRO_FULL_SCALE_250_DPS  0x00 // SCALE_250 (°/s) = 0 (0x00 = 000|00|000)
#define GYRO_FULL_SCALE_500_DPS  0x08 // SCALE_500 (°/s) = 1 (0x08 = 000|01|000)
#define GYRO_FULL_SCALE_1000_DPS 0x10 // SCALE_1000 (°/s) = 2 (0x10 = 000|10|000)
#define GYRO_FULL_SCALE_2000_DPS 0x18 // SCALE_2000 (°/s) = 3 (0x18 = 000|11|000)

// Accel scales
#define ACC_FULL_SCALE_2_G  0x00 // SCALE_2_G (g) = 0 (0x00 = 000|00|000)
#define ACC_FULL_SCALE_4_G  0x08 // SCALE_4_G (g) = 1 (0x08 = 000|01|000)
#define ACC_FULL_SCALE_8_G  0x10 // SCALE_8_G (g) = 2 (0x10 = 000|10|000)
#define ACC_FULL_SCALE_16_G 0x18 // SCALE_16_G (g) = 3 (0x18 = 000|11|000)

// Conversion scales

#define SENSITIVITY_ACCEL 2.0/32768.0   // Valor de conversão do Acelerômetro (g/LSB) para 2g e 16 bits de comprimento da palavra
#define SENSITIVITY_GYRO  250.0/32768.0 // Valor de conversão do Girôscopio ((°/s)/LSB) para 250 °/s e 16 bits de comprimento da palavra
#define SENSITIVITY_TEMP  333.87        // Valor de sensitividade do Termometro (Datasheet: MPU-9250 Product Specification, pag. 12)
#define TEMP_OFFSET       21            // Valor de offset do Termometro (Datasheet: MPU-9250 Product Specification, pag. 12)
#define SENSITIVITY_MAGN  (10.0*4800.0)/32768.0 // Valor de conversão do Magnetômetro (mG/LSB) para 4800uT, 16 bits de comprimento da palavra e conversao a Gauss (10mG = 1uT)


bool newMagData = false;

double offset_accelx = 1124.0, offset_accely = 474.00, offset_accelz = 16208.00;
double offset_gyrox = -464.50, offset_gyroy = -473.50, offset_gyroz = -152.00;
double offset_magnx = 128.50, offset_magny = -252.00, offset_magnz = 421.50;
double scale_magnx = 1.01, scale_magny = 0.96, scale_magnz = 1.03;

int16_t raw_accelx, raw_accely, raw_accelz;
int16_t raw_gyrox, raw_gyroy, raw_gyroz;
int16_t raw_temp;
int16_t raw_magnx, raw_magny, raw_magnz;

double Raw_accelx, Raw_accely, Raw_accelz;
double Raw_gyrox, Raw_gyroy, Raw_gyroz;
double Raw_temp;
double Raw_magnx, Raw_magny, Raw_magnz;

double accelx[N_IMUS], accely[N_IMUS], accelz[N_IMUS];
double gyrox[N_IMUS], gyroy[N_IMUS], gyroz[N_IMUS];
double temp[N_IMUS];
double magnx[N_IMUS], magny[N_IMUS], magnz[N_IMUS];

uint8_t GirAcel[14];
uint8_t Mag[7];

unsigned long t_ini_config, t_fim_config, t_ini_leitura, t_fim_leitura, t;

void deactivate_mpu_hibernate_mode(void){
  void_write(MPU6500_address, 0x6B, 0x00); //PWR_MGMT_1 0x6B e CLK_SEL_PWR_MGMT_1 0x00
}

bool test_mpu_connection(void){
  uint8_t data;
  void_read(MPU6500_address, 0x75, 1, &data); //WHO_AM_I_MPU6500 0x75
  return (bool)(data == 0x71);
}

bool test_magnet_connection(void){
  uint8_t data;
  void_read(AK8963_address, 0x00, 1, &data); // AK8963_address 0x0C e WHO_AM_I_AK8963 0x00
  return (bool)(data == 0x48);
}

void setup_gyros(void){
  void_write(MPU6500_address, 0x1B, GYRO_FULL_SCALE_250_DPS);
}

void setup_accel(void){
  void_write(MPU6500_address, 0x1C, ACC_FULL_SCALE_2_G);
}

void setup_magnet(void){
  void_write(MPU6500_address, 0x37, 0x02);
  void_write(AK8963_address, 0x0A, 0x16);
}

void setup_imu(void){
  setup_gyros();
  setup_accel();
  setup_magnet();
}

void read_mpu(void){
  void_read(MPU6500_address, 0x3B, 14, GirAcel);
  raw_accelx = GirAcel[0] << 8  | GirAcel[1];
  raw_accely = GirAcel[2] << 8  | GirAcel[3];
  raw_accelz = GirAcel[4] << 8  | GirAcel[5];
  raw_temp   = GirAcel[6] << 8  | GirAcel[7];
  raw_gyrox  = GirAcel[8] << 8  | GirAcel[9];
  raw_gyroy  = GirAcel[10] << 8 | GirAcel[11];
  raw_gyroz  = GirAcel[12] << 8 | GirAcel[13];
}

void read_magnet(void){
  uint8_t data;
  void_read(AK8963_address, 0x02, 1, &data); // ST1=0x02
  newMagData = data & 0x01;
  if(newMagData == true) {
    void_read(AK8963_address, 0x03, 7, Mag); // MAGN_XOUT_L = 0x03
    uint8_t c = Mag[6];
    if(!(c & 0x08)) {
      raw_magnx = (Mag[3] << 8 | Mag[2]); 
      raw_magny = (Mag[1] << 8 | Mag[0]); 
      raw_magnz = -(Mag[5] << 8 | Mag[4]);
    }
  }
}

void update_imu_double(void){
  Raw_accelx = (double) raw_accelx;
  Raw_accely = (double) raw_accely;
  Raw_accelz = (double) raw_accelz; 
  Raw_gyrox  = (double) raw_gyrox;
  Raw_gyroy  = (double) raw_gyroy;
  Raw_gyroz  = (double) raw_gyroz;
  Raw_temp   = (double) raw_temp;
  Raw_magnx  = (double) raw_magnx;
  Raw_magny  = (double) raw_magny;
  Raw_magnz  = (double) raw_magnz;
}

void update_imu_normalized(int imu){
  accelx[imu] = (Raw_accelx - offset_accelx)* SENSITIVITY_ACCEL;
  accely[imu] = (Raw_accely - offset_accely) * SENSITIVITY_ACCEL;
  accelz[imu] = (Raw_accelz - (offset_accelz - (32768/2))) * SENSITIVITY_ACCEL;

  gyrox[imu] = (Raw_gyrox - offset_gyrox) * SENSITIVITY_GYRO;
  gyroy[imu] = (Raw_gyroy - offset_gyroy) * SENSITIVITY_GYRO;
  gyroz[imu] = (Raw_gyroz - offset_gyroz) * SENSITIVITY_GYRO;//°/s

  magnx[imu] = ((Raw_magnx - offset_magnx) * scale_magnx) * SENSITIVITY_MAGN;
  magny[imu] = ((Raw_magny - offset_magny) * scale_magnx) * SENSITIVITY_MAGN;
  magnz[imu] = ((Raw_magnz - offset_magnz) * scale_magnx) * SENSITIVITY_MAGN; //mG

  temp[imu] = (Raw_temp/SENSITIVITY_TEMP) + TEMP_OFFSET; //°C
}

double degree_to_rad(double angle){
  return (angle * M_PI) / 180.0;
}

void get_serialized_data(double *serialized_data){
  double *ptr = serialized_data;
  for(int i = 0; i < N_IMUS; i++){
    *(ptr++) = accelx[i];
    *(ptr++) = accely[i];
    *(ptr++) = accelz[i];
    *(ptr++) = degree_to_rad(gyrox[i]);
    *(ptr++) = degree_to_rad(gyroy[i]);
    *(ptr++) = degree_to_rad(gyroz[i]);
    *(ptr++) = magnx[i];
    *(ptr++) = magny[i];
    *(ptr++) = magnz[i];
  }
}

void update_imu_data(int imu){
  read_mpu();
  read_magnet();
  update_imu_double();
  update_imu_normalized(imu);
}

#endif
