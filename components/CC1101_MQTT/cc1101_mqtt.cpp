#include "cc1101_mqtt.h"

using namespace esphome;
using namespace esphome::cc1101;

static const char *TAG = "c1101_mqtt.sensor";

void cc1101_mqtt::setup() {
  ESP_LOGCONFIG(TAG, "Setting up CC1101 SPI...");
  
}

void cc1101_mqtt::loop() {
  
}

void cc1101_mqtt::dump_config() {
  ESP_LOGCONFIG(TAG, "CC1101 SPI Configuration:");
}
