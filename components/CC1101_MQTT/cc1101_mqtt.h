#pragma once

#include <set>
#include <vector>
#include "cc1101.h"
#include "cc1101_dev.h"
#include "esphome/core/component.h"
#include "esphome/components/spi/spi.h"
#include "RCSwitch.h"
#include "esphome/components/mqtt/custom_mqtt_device.h"

namespace esphome {
namespace cc1101 {

class cc1101_mqtt
    : public Component
    , public spi::SPIDevice<spi::BIT_ORDER_MSB_FIRST, spi::CLOCK_POLARITY_LOW, spi::CLOCK_PHASE_LEADING, spi::DATA_RATE_200KHZ>
    , public mqtt::CustomMQTTDevice
{
public:
    void setup() override;
    
    void loop() override;
    
    void dump_config() override;

    void sendPulses();

    static void receivePulses();

    void set_pin(GPIOPin *pin) { pin_ = pin; }

    void set_spi(uint8_t sck, uint8_t miso, uint8_t mosi, uint8_t ss) {
        this->m_sck = sck;
        this->m_miso = miso;
        this->m_mosi = mosi;
        this->m_ss = ss;
    }

    void set_gdo0(uint8_t gdo0) {
        this->m_gdo0 = gdo0;
    }

    void set_gdo2(uint8_t gdo2) {
        this->m_gdo2 = gdo2;
    }

    float get_setup_priority() const override { return setup_priority::HARDWARE; }

private:
    uint8_t m_ss;
    uint8_t m_sck;
    uint8_t m_mosi;
    uint8_t m_miso;
    uint8_t m_gdo0;
    uint8_t m_gdo2;

    uint32_t m_lastPulseDumpTime = 0;
    uint32_t m_lastPulseTime = 0;
    bool m_lastPinState = false;
    uint32_t m_lastModeChangeTime = 0;
    bool m_receiveMode = true;
    bool m_transmitTriggered = false;
    uint32_t m_lastTransmitTime = 0;
    uint8_t m_transmitRepeats = 0;
    

    uint32_t m_spi = (uint32_t)(-1);
    GPIOPin *pin_;

    static std::vector<uint32_t> m_pulseLengthList;

    ELECHOUSE_CC1101 m_device;
    CC1101_dev::Radio *m_radio;
    
    bool m_esp32 = false;

    RCSwitch m_rcswitch;
};

}
}