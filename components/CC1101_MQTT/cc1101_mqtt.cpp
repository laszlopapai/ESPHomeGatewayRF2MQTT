#include "cc1101_mqtt.h"
#include <utility>
#include <string>

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

  m_tSetup = millis();
  ELECHOUSE_cc1101.setSpiPin(m_sck, m_miso, m_mosi, m_ss);
  ELECHOUSE_cc1101.setGDO0(m_gdo0);
  if (ELECHOUSE_cc1101.getCC1101()) {
    ESP_LOGCONFIG(TAG, "CC1101 SPI success");
    m_spi = 1;
  }
  else {
    ESP_LOGCONFIG(TAG, "CC1101 SPI failed");
    m_spi = 2;
  }
  ELECHOUSE_cc1101.Init();
  ELECHOUSE_cc1101.SetRx();
  m_time = millis();
}

void cc1101_mqtt::loop() {
  uint32_t time = millis();
  uint32_t tDiff = time - m_time;

  bool state = pin_->digital_read();
  if (state != m_state) {
    m_pulseIndices.push_back(tDiff);



    m_change++;
    m_stateTime = time;
    m_state = state;
  }

  if (time - m_time >= 1000) {
    m_time = time;


    std::string pulses = "Pulses: ";
    for (auto pulse : m_pulseIndices) {
      pulses += std::to_string(pulse) + " ";
    }

    ESP_LOGCONFIG(TAG, "CC1101 loop %d spi_status: %d ts: %d tc: %d changes: %d %s", m_time, m_spi, m_tSetup, m_tConfig, m_change, pulses.c_str());
    m_change = 0;
    m_pulseIndices.clear();
    m_pulseLengths.clear();
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
