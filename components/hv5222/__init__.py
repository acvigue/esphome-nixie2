import esphome.codegen as cg
import esphome.config_validation as cv
from esphome import pins
from esphome.components import spi
from esphome.const import (
    CONF_ID,
    CONF_SPI_ID,
    CONF_NUMBER,
    CONF_INVERTED,
    CONF_OUTPUT,
    CONF_COUNT,
)

MULTI_CONF = True

CODEOWNERS = ["@acvigue"]
DEPENDENCIES = ["spi"]

HV5222_ns = cg.esphome_ns.namespace("hv5222")
HV5222component = HV5222_ns.class_("HV5222component", cg.Component, spi.SPIDevice)
HV5222Pin = HV5222_ns.class_(
    "HV5222Pin", cg.GPIOPin, cg.Parented.template(HV5222component)
)

CONF_HV5222 = "hv5222"

CONFIG_SCHEMA = cv.All(
    cv.Schema(
        {
            cv.Required(CONF_ID): cv.declare_id(HV5222component),
            cv.Optional(CONF_COUNT, default=1): cv.int_range(min=1, max=4),
            cv.Required(CONF_SPI_ID): cv.use_id(spi.SPIComponent),
        }
    )
    .extend(cv.COMPONENT_SCHEMA)
    .extend(spi.spi_device_schema(cs_pin_required=False))
)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await spi.register_spi_device(var, config)
    cg.add(var.set_chip_count(config[CONF_COUNT]))


def _validate_output_mode(value):
    if value.get(CONF_OUTPUT) is not True:
        raise cv.Invalid("Only output mode is supported")
    return value


HV5222_PIN_SCHEMA = pins.gpio_base_schema(
    HV5222Pin,
    cv.int_range(min=0, max=128),
    modes=[CONF_OUTPUT],
    mode_validator=_validate_output_mode,
    invertible=True,
).extend(
    {
        cv.Required(CONF_HV5222): cv.use_id(HV5222component),
    }
)


def hv5222_pin_final_validate(pin_config, parent_config):
    max_pins = parent_config[CONF_COUNT] * 32
    if pin_config[CONF_NUMBER] >= max_pins:
        raise cv.Invalid(f"Pin number must be less than {max_pins}")


@pins.PIN_SCHEMA_REGISTRY.register(
    CONF_HV5222, HV5222_PIN_SCHEMA, hv5222_pin_final_validate
)
async def hv5222_pin_to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_parented(var, config[CONF_HV5222])
    cg.add(var.set_pin(config[CONF_NUMBER]))
    cg.add(var.set_inverted(config[CONF_INVERTED]))
    return var
