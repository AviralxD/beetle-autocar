#include <Servo.h>

#define THROTTLE_SERVO_PIN 9
#define STEERING_SERVO_PIN 10

#define SERIAL_BAUD_RATE 115200
#define SERIAL_COMMAND_TIMEOUT_MS 500
#define SERIAL_BUFFER_SIZE 40

#define RC_MIN_PULSE_US 1200
#define RC_NEUTRAL_PULSE_US 1500
#define RC_MAX_PULSE_US 1800

Servo throttle_servo;
Servo steering_servo;
char serial_buffer[SERIAL_BUFFER_SIZE];
size_t serial_buffer_length = 0;
unsigned long last_command_time = 0;

void set_neutral() {
  throttle_servo.writeMicroseconds(RC_NEUTRAL_PULSE_US);
  steering_servo.writeMicroseconds(RC_NEUTRAL_PULSE_US);
}

bool parse_value(const char *input, const char **next, float &value) {
  bool negative = false;
  bool has_digits = false;
  float parsed = 0.0f;

  if (*input == '-' || *input == '+') {
    negative = *input == '-';
    ++input;
  }
  while (*input >= '0' && *input <= '9') {
    has_digits = true;
    parsed = parsed * 10.0f + static_cast<float>(*input - '0');
    ++input;
  }
  if (*input == '.') {
    float place = 0.1f;
    ++input;
    while (*input >= '0' && *input <= '9') {
      has_digits = true;
      parsed += static_cast<float>(*input - '0') * place;
      place *= 0.1f;
      ++input;
    }
  }
  if (!has_digits) {
    return false;
  }

  value = negative ? -parsed : parsed;
  *next = input;
  return true;
}

bool parse_command(const char *command, float &throttle, float &steering) {
  if (command[0] != 'T' || command[1] != ':') {
    return false;
  }

  const char *end = nullptr;
  if (!parse_value(command + 2, &end, throttle)) {
    return false;
  }
  if (end[0] != ',' || end[1] != 'S' || end[2] != ':') {
    return false;
  }
  if (!parse_value(end + 3, &end, steering) || end[0] != '\0') {
    return false;
  }

  return throttle >= -1.0f && throttle <= 1.0f &&
         steering >= -1.0f && steering <= 1.0f;
}

int command_to_pulse(float command) {
  command = constrain(command, -1.0f, 1.0f);
  if (command >= 0.0f) {
    return RC_NEUTRAL_PULSE_US + static_cast<int>(
        command * (RC_MAX_PULSE_US - RC_NEUTRAL_PULSE_US));
  }
  return RC_NEUTRAL_PULSE_US + static_cast<int>(
      command * (RC_NEUTRAL_PULSE_US - RC_MIN_PULSE_US));
}

void process_serial() {
  while (Serial.available() > 0) {
    const char received = static_cast<char>(Serial.read());
    if (received == '\n' || received == '\r') {
      if (serial_buffer_length == 0) {
        continue;
      }

      serial_buffer[serial_buffer_length] = '\0';
      float throttle = 0.0f;
      float steering = 0.0f;
      if (parse_command(serial_buffer, throttle, steering)) {
        throttle_servo.writeMicroseconds(command_to_pulse(-throttle));
        steering_servo.writeMicroseconds(command_to_pulse(steering));
        last_command_time = millis();
      } else {
        set_neutral();
      }
      serial_buffer_length = 0;
    } else if (serial_buffer_length < SERIAL_BUFFER_SIZE - 1) {
      serial_buffer[serial_buffer_length++] = received;
    } else {
      serial_buffer_length = 0;
      set_neutral();
    }
  }
}

void setup() {
  throttle_servo.attach(THROTTLE_SERVO_PIN, RC_MIN_PULSE_US, RC_MAX_PULSE_US);
  steering_servo.attach(STEERING_SERVO_PIN, RC_MIN_PULSE_US, RC_MAX_PULSE_US);
  set_neutral();
  Serial.begin(SERIAL_BAUD_RATE);
  last_command_time = millis();
}

void loop() {
  process_serial();
  if (millis() - last_command_time > SERIAL_COMMAND_TIMEOUT_MS) {
    set_neutral();
  }
}