#pragma once

#include <set>
#include <vector>
#include "cc1101.h"
#include "esphome/core/component.h"
#include "esphome/components/spi/spi.h"
//#include "esphome/components/mqtt/custom_mqtt_device.h"

namespace esphome {
namespace cc1101 {

class cc1101_mqtt
    : public Component
    , public spi::SPIDevice<spi::BIT_ORDER_MSB_FIRST, spi::CLOCK_POLARITY_LOW, spi::CLOCK_PHASE_LEADING, spi::DATA_RATE_200KHZ>
//    , public mqtt::CustomMQTTDevice
{
public:
    void setup() override;
    
    void loop() override;
    
    void dump_config() override;

    void set_pin(GPIOPin *pin) { pin_ = pin; }

    void set_spi(uint8_t sck, uint8_t miso, uint8_t mosi, uint8_t ss) {
        this->m_sck = sck;
        this->m_miso = miso;
        this->m_mosi = mosi;
        this->m_ss = ss;
        ELECHOUSE_cc1101.setSpiPin(sck, miso, mosi, ss);
        ELECHOUSE_cc1101.setGDO0(m_gdo0);
    }

    void set_tx(uint8_t tx) {
        this->m_gdo0 = tx;
    }

    void set_rx(uint8_t rx) {
        this->m_gdo2 = rx;
    }

private:
    uint8_t m_ss;
    uint8_t m_sck;
    uint8_t m_mosi;
    uint8_t m_miso;
    uint8_t m_gdo0;
    uint8_t m_gdo2;

    uint32_t m_time = 0;

    uint32_t m_change = 0;
    
    bool m_state = false;
    uint32_t m_stateTime = 0;

    uint32_t m_spi = 0;
    GPIOPin *pin_;

    std::set<uint8_t> m_pulseLengths;
    std::vector<uint8_t> m_pulseIndices;

    ELECHOUSE_CC1101 m_device;
};

}
}