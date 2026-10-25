import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import spi
from esphome import pins
from esphome.const import (
    CONF_ID,
    CONF_PIN,
    CONF_CS_PIN
)
from esphome.core import coroutine_with_priority

CONF_SS = "ss_pin"
CONF_CLK = "clk_pin"
CONF_MOSI = "mosi_pin"
CONF_MISO = "miso_pin"
CONF_GDO0 = "GDO0_pin"
CONF_GDO2 = "GDO2_pin"

DEPENDENCIES = ["spi", "mqtt"]

empty_spi_component_ns = cg.esphome_ns.namespace("cc1101")
EmptySPIComponent = empty_spi_component_ns.class_(
    "cc1101_mqtt", cg.Component, spi.SPIDevice
)

CONFIG_SCHEMA = (
    cv.Schema({
        cv.GenerateID(): cv.declare_id(EmptySPIComponent),
        cv.Required(CONF_SS): cv.int_range(min=0, max=50),
        cv.Required(CONF_CLK): cv.int_range(min=0, max=50),
        cv.Required(CONF_MOSI): cv.int_range(min=0, max=50),
        cv.Required(CONF_MISO): cv.int_range(min=0, max=50),
        cv.Optional(CONF_GDO0): cv.int_range(min=0, max=50),
        cv.Optional(CONF_GDO2): cv.int_range(min=0, max=50),
        cv.Required(CONF_PIN): pins.gpio_input_pin_schema
#        cv.Optional("test", default = "0.5"): cv.positive_not_null_float
    })
    .extend(cv.COMPONENT_SCHEMA)
    .extend(spi.spi_device_schema(cs_pin_required=True))
)

@coroutine_with_priority(1.0)
async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await spi.register_spi_device(var, config)

    cg.add(var.set_spi(config[CONF_CLK], config[CONF_MISO], config[CONF_MOSI], config[CONF_SS]))
    
    pin = await cg.gpio_pin_expression(config[CONF_PIN])
    cg.add(var.set_pin(pin))

    if CONF_GDO0 in config:
        cg.add(var.set_gdo0(config[CONF_GDO0]))
        cg.add_define("USE_RX")

    if CONF_GDO2 in config:
        cg.add(var.set_gdo2(config[CONF_GDO2]))
        cg.add_define("USE_TX")