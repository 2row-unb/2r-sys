// Datasheet definitions for MPU9250

#ifndef TWOROW_IMU
#define TWOROW_IMU

#include "i2c.h"
#include "mux.h"

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

typedef enum Coord{
  X, Y, Z
} Coord;

typedef enum Sensor{
  ACCEL, GYRO, MAGNET, MAGNET_SCALE
} Sensor;

typedef struct IMU{
  int id;
  Mux mux;
  float offsets[4][3];
  float data[3][3];
  float temp;
} IMU;

IMU *registered_imus[N_IMUS];
int n_imu = 0;
float raw_data[3][3];
float raw_temp;
uint8_t gir_acel_buffer[14];
uint8_t mag_buffer[7];
bool new_magnet_data = false;

void print_imu(IMU *imu){
  Serial.print("IMU (");
  Serial.print(imu->id);
  Serial.print(") ------> MUX: ");
  Serial.print(imu->mux.pins_states[0]);
  Serial.print(" | ");
  Serial.println(imu->mux.pins_states[1]);
}

void register_imu(IMU *imu){
  registered_imus[n_imu++] = imu;
  print_imu(imu);
}

void register_offsets(IMU *imu){
  switch(imu->id){
    case 1:
      imu->offsets[ACCEL][X] = -228.00;
      imu->offsets[ACCEL][Y] = 890.00;
      imu->offsets[ACCEL][Z] = 15586.00;

      imu->offsets[GYRO][X] = -427.50;
      imu->offsets[GYRO][Y] = 358.50;
      imu->offsets[GYRO][Z] = -50.00;

      imu->offsets[MAGNET][X] = 134.00;
      imu->offsets[MAGNET][Y] = -48.50;
      imu->offsets[MAGNET][Z] = 210.00;

      imu->offsets[MAGNET_SCALE][X] = 1.00;
      imu->offsets[MAGNET_SCALE][Y] = 0.97;
      imu->offsets[MAGNET_SCALE][Z] = 1.02;
      break;

    case 5:
      imu->offsets[ACCEL][X] = 794.00;
      imu->offsets[ACCEL][Y] = -904.00;
      imu->offsets[ACCEL][Z] = 16172.00;

      imu->offsets[GYRO][X] = 131.00;
      imu->offsets[GYRO][Y] = -308.50;
      imu->offsets[GYRO][Z] = 72.50;

      imu->offsets[MAGNET][X] = 288.00;
      imu->offsets[MAGNET][Y] = -61.00;
      imu->offsets[MAGNET][Z] = -192.00;

      imu->offsets[MAGNET_SCALE][X] = 1.01;
      imu->offsets[MAGNET_SCALE][Y] = 1.00;
      imu->offsets[MAGNET_SCALE][Z] = 1.00;
      break;
  }
}

void build_imu(IMU *imu, int id){
  uint8_t states[N_IMUS];
  switch(id){
    case 1:
      states[0] = 1;
      states[1] = 0;
      break;
    case 5:
      states[0] = 0;
      states[1] = 1;
      break;
  }
  imu->id = id;
  build_mux(&(imu->mux), states);
  register_offsets(imu);
}

void read_mpu(void){
  void_read(MPU6500_address, 0x3B, 14, gir_acel_buffer);
  raw_data[ACCEL][X] = (float) (gir_acel_buffer[0] << 8  | gir_acel_buffer[1]);
  raw_data[ACCEL][Y] = (float) (gir_acel_buffer[2] << 8  | gir_acel_buffer[3]);
  raw_data[ACCEL][Z] = (float) (gir_acel_buffer[4] << 8  | gir_acel_buffer[5]);
  raw_temp           = (float) (gir_acel_buffer[6] << 8  | gir_acel_buffer[7]);
  raw_data[GYRO][X]  = (float) (gir_acel_buffer[8] << 8  | gir_acel_buffer[9]);
  raw_data[GYRO][Y]  = (float) (gir_acel_buffer[10] << 8 | gir_acel_buffer[11]);
  raw_data[GYRO][Z]  = (float) (gir_acel_buffer[12] << 8 | gir_acel_buffer[13]);
}

void read_magnet(void){
  uint8_t data;
  void_read(AK8963_address, 0x02, 1, &data); // ST1=0x02
  new_magnet_data = data & 0x01;
  if(new_magnet_data == true) {
    void_read(AK8963_address, 0x03, 7, mag_buffer); // MAGN_XOUT_L = 0x03
    uint8_t c = mag_buffer[6];
    if(!(c & 0x08)) {
      raw_data[MAGNET][X] = (mag_buffer[3] << 8 | mag_buffer[2]); 
      raw_data[MAGNET][Y] = (mag_buffer[1] << 8 | mag_buffer[0]); 
      raw_data[MAGNET][Z] = -(mag_buffer[5] << 8 | mag_buffer[4]);
    }
  }
}

float degree_to_rad(float angle){
  return (angle * M_PI) / 180.0;
}

void update_imu_data(IMU *imu){
  imu->data[ACCEL][X] = (raw_data[ACCEL][X] - imu->offsets[ACCEL][X])* SENSITIVITY_ACCEL;
  imu->data[ACCEL][Y] = (raw_data[ACCEL][Y] - imu->offsets[ACCEL][Y]) * SENSITIVITY_ACCEL;
  imu->data[ACCEL][Z] = (raw_data[ACCEL][Z] - (imu->offsets[ACCEL][Z] - (32768/2))) * SENSITIVITY_ACCEL;

  imu->data[GYRO][X] = degree_to_rad((raw_data[GYRO][X] - imu->offsets[GYRO][X]) * SENSITIVITY_GYRO);
  imu->data[GYRO][Y] = degree_to_rad((raw_data[GYRO][Y] - imu->offsets[GYRO][Y]) * SENSITIVITY_GYRO);
  imu->data[GYRO][Z] = degree_to_rad((raw_data[GYRO][Z] - imu->offsets[GYRO][Z]) * SENSITIVITY_GYRO);//°/s

  imu->data[MAGNET][X] = ((raw_data[MAGNET][X] - imu->offsets[MAGNET][X]) * imu->offsets[MAGNET_SCALE][X]) * SENSITIVITY_MAGN;
  imu->data[MAGNET][Y] = ((raw_data[MAGNET][Y] - imu->offsets[MAGNET][Y]) * imu->offsets[MAGNET_SCALE][Y]) * SENSITIVITY_MAGN;
  imu->data[MAGNET][Z] = ((raw_data[MAGNET][Z] - imu->offsets[MAGNET][Z]) * imu->offsets[MAGNET_SCALE][Z]) * SENSITIVITY_MAGN;
}

void activate_imu(IMU *imu){
  activate_mux(&(imu->mux));
}

void update_imu(IMU *imu){
  activate_imu(imu);
  read_mpu();
  read_magnet();
  update_imu_data(imu);
}

void update_all_imus(void){
  for(int i = 0; i < N_IMUS; i++){
    update_imu(registered_imus[i]);
  }
}

void get_imu_serialized_data(float *serialized_data){
  IMU *current_imu;
  for(int i = 0; i < N_IMUS; i++){
    current_imu = registered_imus[i];
    for(int k = 0; k < 3; k++){
      for(int j = 0; j < 3; j++){
        *(serialized_data++) = current_imu->data[k][j];
      }
    } 
  }
}

void deactivate_mpu_hibernate_mode(void){
  for(int i = 0; i < N_IMUS; i++){
    activate_imu(registered_imus[i]);
    void_write(MPU6500_address, 0x6B, 0x00); //PWR_MGMT_1 0x6B e CLK_SEL_PWR_MGMT_1 0x00
  }
}

bool test_mpu_connection(void){
  uint8_t data;
  for(int i = 0; i < N_IMUS; i++){
    activate_imu(registered_imus[i]);
    void_read(MPU6500_address, 0x75, 1, &data); //WHO_AM_I_MPU6500 0x75
    if(data != 0x71) return false;
  }
  return true;
}

bool test_magnet_connection(void){
  uint8_t data;
  for(int i = 0; i < N_IMUS; i++){
    activate_imu(registered_imus[i]);
    void_read(AK8963_address, 0x00, 1, &data); // AK8963_address 0x0C e WHO_AM_I_AK8963 0x00
    if(data != 0x48) return false;
  }
  return true;
}

void setup_gyros(void){
  for(int i = 0; i < N_IMUS; i++){
    activate_imu(registered_imus[i]);
    void_write(MPU6500_address, 0x1B, GYRO_FULL_SCALE_250_DPS);
  }
}

void setup_accel(void){
  for(int i = 0; i < N_IMUS; i++){
    activate_imu(registered_imus[i]);
    void_write(MPU6500_address, 0x1C, ACC_FULL_SCALE_2_G);
  }
}

void setup_magnet(void){
  for(int i = 0; i < N_IMUS; i++){
    activate_imu(registered_imus[i]);
    void_write(MPU6500_address, 0x37, 0x02);
    void_write(AK8963_address, 0x0A, 0x16);
  }
}

void setup_imus(void){
  setup_gyros();
  setup_accel();
  setup_magnet();
}


#endif
