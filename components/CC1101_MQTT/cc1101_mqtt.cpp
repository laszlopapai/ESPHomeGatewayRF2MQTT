#include "cc1101_mqtt.h"

using namespace esphome;
using namespace esphome::cc1101;

static const char *TAG = "cc1101_mqtt.component";

void cc1101_mqtt::setup() {
  ESP_LOGCONFIG(TAG, "Setting up CC1101 SPI...");
  ESP_LOGCONFIG(TAG, "SPI SCK: %d", (uint32_t)m_sck);
  ESP_LOGCONFIG(TAG, "SPI MISO: %d", (uint32_t)m_miso);
  ESP_LOGCONFIG(TAG, "SPI MOSI: %d", (uint32_t)m_mosi);
  ESP_LOGCONFIG(TAG, "SPI SS: %d", (uint32_t)m_ss);
  ESP_LOGCONFIG(TAG, "GDO0: %d", (uint32_t)m_gdo0);
  ESP_LOGCONFIG(TAG, "GDO2: %d", (uint32_t)m_gdo2);

  if (m_device.getCC1101()) {
    ESP_LOGCONFIG(TAG, "CC1101 SPI success");
    m_spi = 1;
    m_device.Init();
    m_device.SetRx();
  }
  else {
    ESP_LOGCONFIG(TAG, "CC1101 SPI failed");
    m_spi = 2;
  }
  m_time = millis();
}

void cc1101_mqtt::loop() {

  bool state = pin_->digital_read();
  if (state != m_state) {
    m_state = state;
    m_change++;    
  }

  uint32_t time = millis();
  if (time - m_time > 1000) {
    m_time = time;

    ESP_LOGCONFIG(TAG, "CC1101 loop %d spi_status: %d changes: %d", m_time, m_spi, m_change);
    m_change = 0;
  }
}

void cc1101_mqtt::dump_config() {
  ESP_LOGCONFIG(TAG, "CC1101 SPI Configuration:");
  ESP_LOGCONFIG(TAG, "SPI SCK: %d", (uint32_t)m_sck);
  ESP_LOGCONFIG(TAG, "SPI MISO: %d", (uint32_t)m_miso);
  ESP_LOGCONFIG(TAG, "SPI MOSI: %d", (uint32_t)m_mosi);
  ESP_LOGCONFIG(TAG, "SPI SS: %d", (uint32_t)m_ss);
  ESP_LOGCONFIG(TAG, "GDO0: %d", (uint32_t)m_gdo0);
  ESP_LOGCONFIG(TAG, "GDO2: %d", (uint32_t)m_gdo2);
}
