import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import spi
from esphome.const import CONF_ID

CONF_SS = "ss_pin"
CONF_CLK = "clk_pin"
CONF_MOSI = "mosi_pin"
CONF_MISO = "miso_pin"
CONF_RX = "rx_pin"
CONF_TX = "tx_pin"

DEPENDENCIES = ["spi"]

empty_spi_component_ns = cg.esphome_ns.namespace("cc1101")
EmptySPIComponent = empty_spi_component_ns.class_(
    "cc1101_mqtt", cg.Component, spi.SPIDevice
)

CONFIG_SCHEMA = (
    cv.Schema({
        cv.GenerateID(): cv.declare_id(EmptySPIComponent),
        cv.Required(CONF_SS): cv.int_range(min=0, max=20),
        cv.Required(CONF_CLK): cv.int_range(min=0, max=20),
        cv.Required(CONF_MOSI): cv.int_range(min=0, max=20),
        cv.Required(CONF_MISO): cv.int_range(min=0, max=20),
        cv.Required(CONF_RX): cv.int_range(min=0, max=20),
        cv.Required(CONF_TX): cv.int_range(min=0, max=20),

        cv.Optional("test", default = "0.5"): cv.positive_not_null_float
    })
    .extend(cv.COMPONENT_SCHEMA)
    .extend(spi.spi_device_schema(cs_pin_required=True))
)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await spi.register_spi_device(var, config)

    cg.add(var.set_spi(config[CONF_CLK], config[CONF_MOSI], config[CONF_MISO], config[CONF_SS]))
    
    if CONF_RX in config:
        rx = await cg.get_variable(config[CONF_RX])
        cg.add(var.set_rx(rx))
        cg.add_define("USE_RX")

    if CONF_TX in config:
        tx = await cg.get_variable(config[CONF_TX])
        cg.add(var.set_tx(tx))
        cg.add_define("USE_TX")