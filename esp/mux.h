#ifndef TWOROW_MUX
#define TWOROW_MUX

#define MUX_SIZE 2
#define MUX_A D7  
#define MUX_B D6

uint8_t mux_pins[MUX_SIZE];

typedef struct Mux {
  uint8_t pins_states[MUX_SIZE];
  bool is_active;
} Mux;

Mux *active_mux;

void activate_mux_pins(void){
  mux_pins[0] = MUX_A; pinMode(MUX_A, OUTPUT);
  mux_pins[1] = MUX_B; pinMode(MUX_B, OUTPUT);
}

void build_mux(Mux *mux, uint8_t *states){
  for(int i = 0; i < MUX_SIZE; i++){
    mux->pins_states[i] = states[i];
  }
}

void write_mux_pins(Mux *mux){
  for(int i = 0; i < MUX_SIZE; i++){
    digitalWrite(mux_pins[i], mux->pins_states[i]);
  }
}

void activate_mux(Mux *mux) {
  if(active_mux != NULL){
    active_mux->is_active = false;
  }

  active_mux = mux;
  mux->is_active = true;
  write_mux_pins(mux);
}

#endif
