#ifndef TWOROW_MUX
#define TWOROW_MUX

#define MUX_A D5
#define MUX_B D6
#define MUX_C D7  

void setup_mux_pins(void){
  pinMode(MUX_A, OUTPUT);
  pinMode(MUX_B, OUTPUT);
  pinMode(MUX_C, OUTPUT);
}

void changeMux(int c, int b, int a) {
  digitalWrite(MUX_A, a);
  digitalWrite(MUX_B, b);
  digitalWrite(MUX_C, c);
}

#endif
