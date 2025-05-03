#include "cc1101_mqtt.h"

using namespace esphome;
using namespace esphome::cc1101;

static const char *TAG = "c1101_mqtt.sensor";

void cc1101_mqtt::setup() {
  ESP_LOGCONFIG(TAG, "Setting up CC1101 SPI...");
  ESP_LOGCONFIG(TAG, "SPI SCK: %d", this->m_sck);
  ESP_LOGCONFIG(TAG, "SPI MISO: %d", this->m_miso);
  ESP_LOGCONFIG(TAG, "SPI MOSI: %d", this->m_mosi);
  ESP_LOGCONFIG(TAG, "SPI SS: %d", this->m_ss);
  ESP_LOGCONFIG(TAG, "GDO0: %d", this->m_gdo0);
  ESP_LOGCONFIG(TAG, "GDO2: %d", this->m_gdo2);
  // Initialize SPI pins
  
}

void cc1101_mqtt::loop() {
  
}

void cc1101_mqtt::dump_config() {
  ESP_LOGCONFIG(TAG, "CC1101 SPI Configuration:");
}
