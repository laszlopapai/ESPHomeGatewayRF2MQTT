#pragma once

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
};

}
}