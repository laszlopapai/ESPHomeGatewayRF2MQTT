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

  #ifdef ESP32
  m_esp32 = true;
  #else
  m_esp32 = false;
  #endif

/*
  this->m_radio = new CC1101_dev::Radio(m_ss, m_sck, m_miso, m_mosi, m_gdo0, m_gdo2);
  CC1101_dev::Status s = this->m_radio->begin();
  if (s != CC1101_dev::STATUS_OK) {
    m_spi = (uint32_t)s;
  }
  else {
    m_spi = 0;
  }
*/

  ELECHOUSE_cc1101.setSpiPin(m_sck, m_miso, m_mosi, m_ss);
  ELECHOUSE_cc1101.setGDO(m_gdo0, m_gdo2);

  if (ELECHOUSE_cc1101.getCC1101()) {
    ESP_LOGCONFIG(TAG, "CC1101 SPI success");
    m_spi = 0;
  }
  else {
    ESP_LOGCONFIG(TAG, "CC1101 SPI failed");
    m_spi = 1;
  }
  ELECHOUSE_cc1101.Init();

  m_rcswitch.enableReceive(m_gdo2);
  m_rcswitch.enableTransmit(m_gdo0);

  if (m_spi == CC1101_dev::STATUS_OK) {
    ELECHOUSE_cc1101.SetRx();
    //m_radio->setState(CC1101_dev::STATE_RX);
  }
  
  m_lastTransmitTime = m_lastModeChangeTime = m_lastPulseTime = m_lastPulseDumpTime = millis();

  attachInterrupt(m_gdo2, interrupt, CHANGE);
}

std::vector<uint32_t> cc1101_mqtt::m_pulseLengthList {};

void cc1101_mqtt::interrupt() {
  static uint32_t lastPulseTime = 0;
  uint32_t time = micros();

  if (m_pulseLengthList.size() >= 2048) {
    lastPulseTime = time;
    return;
  }

  uint32_t pulseLength = time - lastPulseTime;
  m_pulseLengthList.push_back(pulseLength);
  lastPulseTime = time;
}

void cc1101_mqtt::loop() {
  uint32_t time = millis();

  // Dump pulse lengths
  if (m_receiveMode && time - m_lastPulseDumpTime >= 100) {
    m_lastPulseDumpTime = time;

    std::string pulseList = "";
    for (auto pulse : m_pulseLengthList) {
      pulseList += std::to_string(pulse) + " ";
    }
    if (m_pulseLengthList.size() > 0) {
      this->publish("rfproxys3/sensor/pulse_list", pulseList);
    }
    
    ESP_LOGCONFIG(TAG, "CC1101 loop spi_status: %d listcapacity: %d", m_spi, m_pulseLengthList.capacity());
    
    m_pulseLengthList.clear();
  }

  // Mode change
  if (time - m_lastModeChangeTime > 5000) {
    m_lastModeChangeTime = time;
    m_receiveMode = !m_receiveMode;
    m_receiveMode = true; // Always RX mode for now
    if (m_receiveMode) {
      ESP_LOGCONFIG(TAG, "CC1101 RX mode");
      ELECHOUSE_cc1101.SetRx();
    } else {
      ESP_LOGCONFIG(TAG, "CC1101 TX mode");
      ELECHOUSE_cc1101.SetTx();
    }
  }

  // Receive data
  if (m_receiveMode && m_rcswitch.available()) {    
    ESP_LOGCONFIG(TAG, "Received %d / %dbit Protocol: %d",
      m_rcswitch.getReceivedValue(),
      m_rcswitch.getReceivedBitlength(),
      m_rcswitch.getReceivedProtocol()
    );

    m_rcswitch.resetAvailable();
  }

  // Transmit data
  if (!m_receiveMode && time - m_lastTransmitTime > 1000) {
    m_lastTransmitTime = time;

    if (m_transmitRepeats > 2) {
      m_transmitRepeats++;
      m_rcswitch.send(13982723, 24);
      ESP_LOGCONFIG(TAG, "Transmitted 13982723 Off");
    }
    else {
      m_transmitRepeats++;
      m_rcswitch.send(13982732, 24);
      ESP_LOGCONFIG(TAG, "Transmitted 13982732 On");
    }

    if (m_transmitRepeats > 5) {
      m_transmitRepeats = 0;
    }
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
