// PotaDAR Power Board Code
// Artifact ID: POWSFT-001
// Revision: A
// Revision Date: 24 February 2024
// Prepared By: Joel Kartchner
// Checked By: Collin Lambert

// Code to turn on and off the the up and down converter.
// When the device is plugged into the wall, the arduino will be powered on, but not the up and down converters.
// When the power switch is turned on, the arduino powers on the up and down converters. When the switch is turned off, the arduino powers them off
// When the switch is powered on:
// - Arduino reads voltage on the V_MEAS pin (pin that reads the switch state)
// - it turns on the up and down converters. 
// - This involves driving the two JUMP pins to ground, 
// - then drive the POW_NEG pin HIGH, then drive the POW_POS pin HIGH. 
// - After that, drive the two JUMP pins high.
// - Writes data to LO board TODO
// When the V_MEAS pin goes low, 
// - drive the POW_POS pin LOW, 
// - and then drive the POW_NEG pin LOW.

// Includes
#include <SPI.h>

#define DEBUG 0

#define LED_RED 5
#define LED_GREEN 6
#define LED_BLUE 7
// SPI Pins
#define JUMP1 8
#define JUMP2 9
#define POW_POS 3
#define POW_NEG 2
#define V_MEAS A7
// Delay time (in milliseconds)
#define DELAY 500

// SPI Stuff
#define SCK 13
#define MISO 12
#define MOSI 11
#define SS 10 
// data masks
#define ADDRESS_MASK 0xFF0000
#define DATA_UPPER_MASK 0x00FF00
#define DATA_LOWER_MASK 0x0000FF

#define EXTERNAL_TRIGGER_PIN A4  // Define the pin you are using

typedef enum {
  INIT,
  WAIT,
  TRIGGERED
} external_trigger_state_t;

static external_trigger_state_t external_trigger_state;

// register Values
// 14 GHz
uint32_t registers[113] = {0x700000, 0x6F0000, 0x6E0000, 0x6D0000, 0x6C0000, 0x6B0000, 0x6A0000, 0x690021, 0x680000, 0x670000, 0x663F80, 0x650011, 0x640000, 0x630000, 0x620200, 0x610888, 0x600000, 0x5F0000, 0x5E0000, 0x5D0000, 0x5C0000, 0x5B0000, 0x5A0000, 0x590000, 0x580000, 0x570000, 0x56FFFF, 0x55D2FF, 0x540001, 0x530000, 0x521E00, 0x510000, 0x506666, 0x4F0026, 0x4E0003, 0x4D0000, 0x4C000C, 0x4B0800, 0x4A0000, 0x49003F, 0x480001, 0x470081, 0x46C350, 0x450000, 0x4403E8, 0x430000, 0x4201F4, 0x410000, 0x401388, 0x3F0000, 0x3E0322, 0x3D00A8, 0x3C0000, 0x3B0001, 0x3A9001, 0x390020, 0x380000, 0x370000, 0x360000, 0x350000, 0x340820, 0x330080, 0x320000, 0x314180, 0x300300, 0x2F0300, 0x2E07FD, 0x2DC8DF, 0x2C1F23, 0x2B0000, 0x2A0000, 0x290000, 0x280000, 0x2703E8, 0x260000, 0x250404, 0x240046, 0x230004, 0x220000, 0x211E21, 0x200393, 0x1F43EC, 0x1E318C, 0x1D318C, 0x1C0488, 0x1B0002, 0x1A0DB0, 0x190C2B, 0x18071A, 0x17007C, 0x160001, 0x150401, 0x14E048, 0x1327B7, 0x120064, 0x11012C, 0x100080, 0x0F064F, 0x0E1E70, 0x0D4000, 0x0C5001, 0x0B0018, 0x0A10D8, 0x091604, 0x082000, 0x0740B2, 0x06C802, 0x0500C8, 0x040A43, 0x030642, 0x020500, 0x010808, 0x00251C};


byte buf[3] = {0x00, 0x00, 0x00};

bool isOn = false;
int onThreshold = 500;
long curr_time = 0;
long on_time = 0;
long off_time = 0;
long jump_time = 0;



void setup() {

  Serial.begin(9600);
  external_trigger_state = INIT;
  pinMode(EXTERNAL_TRIGGER_PIN, INPUT);
  // Define pinmodes for the pins we are using
  pinMode(V_MEAS, INPUT);
  pinMode(LED_RED, OUTPUT);
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_BLUE, OUTPUT);
  pinMode(JUMP1, OUTPUT);
  pinMode(JUMP2, OUTPUT);
  pinMode(POW_POS, OUTPUT);
  pinMode(POW_NEG, OUTPUT);
  // SPI setup
  pinMode(SCK, OUTPUT);
  pinMode(MISO, INPUT);
  pinMode(MOSI, OUTPUT);
  pinMode(SS, OUTPUT);
  // Disable SPI on Startup
  digitalWrite(SS, HIGH);
  SPI.setClockDivider(SPI_CLOCK_DIV32);
  SPI.begin();
  // Write Initial Values
  digitalWrite(POW_POS, LOW);
  digitalWrite(POW_NEG, LOW);
  digitalWrite(JUMP1, LOW);
  digitalWrite(JUMP2, LOW);
  digitalWrite(LED_GREEN, LOW);
  digitalWrite(LED_RED, HIGH);
  digitalWrite(LED_BLUE, LOW);
  // Debug the LEDS
  #if DEBUG
  // Turn on red
  digitalWrite(LED_GREEN, LOW);
  digitalWrite(LED_RED, HIGH);
  digitalWrite(LED_BLUE, LOW);
  delay(DELAY);
  // Turn on Green
  digitalWrite(LED_GREEN, HIGH);
  digitalWrite(LED_RED, LOW);
  digitalWrite(LED_BLUE, LOW);
  delay(DELAY);
  // Turn on Blue
  digitalWrite(LED_GREEN, LOW);
  digitalWrite(LED_RED, LOW);
  digitalWrite(LED_BLUE, HIGH);
  delay(DELAY);
  #endif
  
}

void trigger_tick() {
  //Serial.println(analogRead(EXTERNAL_TRIGGER_PIN));
  switch (external_trigger_state) {
    case INIT:
      external_trigger_state = WAIT;
      break;

    case WAIT:
      if (analogRead(EXTERNAL_TRIGGER_PIN) >= 100) {
        Serial.write(0xFF);
        //Serial.println("received!");
        external_trigger_state = TRIGGERED;
      }
      break;

    case TRIGGERED:
      if (analogRead(EXTERNAL_TRIGGER_PIN) < 100) {
        external_trigger_state = WAIT;
      }
      break;
  }
}

void loop() {
  if(analogRead(V_MEAS)<onThreshold && isOn) {
    turnOff();
  }
  if(analogRead(V_MEAS)>onThreshold && !isOn) {
    turnOn();
  }

  trigger_tick();
}

void turnOn() {
  // Drive the JUMP pins to ground (Disconnect jumpers from pins)
  digitalWrite(JUMP1, LOW);
  digitalWrite(JUMP2, LOW);
  delay(DELAY);
  // Drive power supplies high
  digitalWrite(POW_NEG, HIGH);
  delay(DELAY);
  digitalWrite(POW_POS, HIGH);
  delay(DELAY);
  // Drive JUMP pins HIGH (Connect jumpers)
  digitalWrite(JUMP1, HIGH);
  digitalWrite(JUMP2, HIGH);
  delay(DELAY);
  // write registers
  writeRegisters();
  // Turn on led green
  digitalWrite(LED_GREEN, HIGH);
  digitalWrite(LED_RED, LOW);
  digitalWrite(LED_BLUE, LOW);
  isOn = true;
}

void turnOff() {
  // Turn off +5 power supply
  digitalWrite(POW_POS, LOW);
  delay(DELAY);
  // Turn off -5 power supply
  digitalWrite(POW_NEG, LOW);
  // Disconnect Jumpers
  digitalWrite(JUMP1, LOW);
  digitalWrite(JUMP2, LOW);
  delay(DELAY);
  // Turn on the LED red
  digitalWrite(LED_GREEN, LOW);
  digitalWrite(LED_RED, HIGH);
  digitalWrite(LED_BLUE, LOW);
  isOn = false;
}

void writeRegisters() {
  digitalWrite(LED_GREEN, LOW);
  digitalWrite(LED_RED, LOW);
  digitalWrite(LED_BLUE, HIGH);
  // Function to write the registers
  for (int i = 0; i < 113; ++i) {
    buf[0] = (registers[i] & ADDRESS_MASK) >> 16;
    //Serial.printf("%d buf[0]: %02X ", i, buf[0]);
    buf[1] = (registers[i] & DATA_UPPER_MASK) >> 8;
    //Serial.printf("buf[1]: %02X ", buf[1]);
    buf[2] = registers[i] & DATA_LOWER_MASK;
    //Serial.printf("buf[2]: %02X\n", buf[2]);

    digitalWrite(SS, LOW);
    SPI.transfer(buf, 3);
    digitalWrite(SS, HIGH);
    delay(1);
  }
  delay(DELAY);
}





