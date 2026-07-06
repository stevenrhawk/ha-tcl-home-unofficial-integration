"""Cylindrical AC device data.

This file defines how the integration reads and controls a Cylindrical AC unit.
It maps the AWS IoT Thing State fields (from the TCL cloud API) to Python attributes,
and handles mode-change logic (what state to send when the user switches modes).

The field names (e.g. "powerSwitch", "windSpeed7Gear") come directly from the
device's diagnostic data and must match the TCL API exactly.
"""

from homeassistant.core import HomeAssistant

from .calculations import try_get_value
from .data_storage import init_stored_device_data
from .device_enums import ModeEnum
from .device_features import DeviceFeatureEnum


class TCL_CylindricalAC_DeviceData:
    """Parses the AWS Thing State for a Cylindrical AC device.

    Each attribute corresponds to a key in the device's reported state.
    The try_get_value function checks the 'delta' dict first (pending changes),
    then falls back to 'aws_thing_state' (last known state), and finally
    uses the default value if neither has the key.
    """

    def __init__(self, device_id: str, aws_thing_state: dict, delta: dict) -> None:
        self.device_id = device_id

        # --- Core controls ---
        self.power_switch               = int(try_get_value(delta, aws_thing_state, "powerSwitch", -1))
        self.work_mode                  = int(try_get_value(delta, aws_thing_state, "workMode", -1))
        self.sleep                      = int(try_get_value(delta, aws_thing_state, "sleep", -1))

        # --- Temperature ---
        self.target_temperature         = int(try_get_value(delta, aws_thing_state, "targetTemperature", -1))
        self.current_temperature        = int(try_get_value(delta, aws_thing_state, "currentTemperature", -1))
        self.target_fahrenheit_temp     = int(try_get_value(delta, aws_thing_state, "targetFahrenheitTemp", -1))
        self.temperature_type           = int(try_get_value(delta, aws_thing_state, "temperatureType", -1))

        # --- Fan / Wind ---
        # Note: This device uses "windSpeed7Gear" (0-6) instead of "windSpeed" (0-2).
        self.wind_speed_7_gear          = int(try_get_value(delta, aws_thing_state, "windSpeed7Gear", -1))
        self.wind_speed_auto_switch     = int(try_get_value(delta, aws_thing_state, "windSpeedAutoSwitch", -1))

        # --- Swing / Air direction ---
        # Note: This device uses "verticalWind" / "horizontalWind" (on/off toggles)
        # instead of "verticalSwitch" / "horizontalSwitch" found on standard Split ACs.
        self.vertical_wind              = int(try_get_value(delta, aws_thing_state, "verticalWind", -1))
        self.horizontal_wind            = int(try_get_value(delta, aws_thing_state, "horizontalWind", -1))
        self.vertical_direction         = int(try_get_value(delta, aws_thing_state, "verticalDirection", -1))
        self.horizontal_direction       = int(try_get_value(delta, aws_thing_state, "horizontalDirection", -1))

        # --- Switches / Features ---
        self.beep_switch                = int(try_get_value(delta, aws_thing_state, "beepSwitch", -1))
        self.screen                     = int(try_get_value(delta, aws_thing_state, "screen", -1))
        self.ai_eco                     = int(try_get_value(delta, aws_thing_state, "AIECOSwitch", -1))
        self.healthy                    = int(try_get_value(delta, aws_thing_state, "healthy", -1))
        self.anti_moldew                = int(try_get_value(delta, aws_thing_state, "antiMoldew", -1))
        self.anti_direct_blow           = int(try_get_value(delta, aws_thing_state, "antiDirectBlow", -1))
        self.generator_mode             = int(try_get_value(delta, aws_thing_state, "generatorMode", -1))

        # --- Sensors / Diagnostics ---
        self.internal_unit_coil_temperature = int(try_get_value(delta, aws_thing_state, "internalUnitCoilTemperature", -1))
        self.external_unit_temperature      = int(try_get_value(delta, aws_thing_state, "externalUnitTemperature", -1))
        self.self_clean_status              = int(try_get_value(delta, aws_thing_state, "selfCleanStatus", -1))
        self.error_code                     = list(try_get_value(delta, aws_thing_state, "errorCode", []))


async def get_stored_cylindrical_ac_data(
    hass: HomeAssistant, device_id: str
) -> dict[str, any]:
    """Initialize persisted settings with sensible defaults.

    These stored values remember user preferences across restarts,
    e.g. the last temperature set in each mode, or the fan speed per mode.
    """
    default_wind_speed = "Auto"
    return await init_stored_device_data(hass, device_id, [
        # User-configurable behaviors (can be toggled via HA switches)
        ("user_config.behavior.memorize_temp_by_mode", False),
        ("user_config.behavior.memorize_fan_speed_by_mode", False),
        ("user_config.behavior.silent_beep_when_turn_on", False),
        ("user_config.settings.native_temp_step", 1.0),
        ("user_config.settings.min_temp", 16),
        ("user_config.settings.max_temp", 31),
        # Default temperatures per mode
        ("target_temperature.Cool.value", 24),
        ("target_temperature.Heat.value", 24),
        ("target_temperature.Dehumidification.value", 24),
        ("target_temperature.Fan.value", 24),
        ("target_temperature.Auto.value", 24),
        # Default fan speed per mode
        ("fan_speed.Cool.value", default_wind_speed),
        ("fan_speed.Heat.value", default_wind_speed),
        ("fan_speed.Dehumidification.value", default_wind_speed),
        ("fan_speed.Fan.value", default_wind_speed),
        ("fan_speed.Auto.value", default_wind_speed),
    ])


def handle_cylindrical_ac_mode_change(
    desired_state: dict, value: ModeEnum,
    supported_features: list[DeviceFeatureEnum], stored_data: dict
) -> dict:
    """Define what state changes to send when the user switches AC modes.

    Each mode sets specific defaults for fan speed, temperature, etc.
    The workMode integer value is already set by the caller via mode_enum_to_value_mapp.
    This function adds mode-specific side effects.
    """
    match value:
        case ModeEnum.AUTO:
            # Auto mode: let the device decide fan speed
            if DeviceFeatureEnum.SELECT_WIND_SPEED_7_GEAR in supported_features:
                desired_state["windSpeedAutoSwitch"] = 1
                desired_state["windSpeed7Gear"] = 0
        case ModeEnum.COOL:
            # Cool mode: set target temperature from stored preferences
            if DeviceFeatureEnum.SELECT_WIND_SPEED_7_GEAR in supported_features:
                desired_state["windSpeedAutoSwitch"] = 1
                desired_state["windSpeed7Gear"] = 0
        case ModeEnum.DEHUMIDIFICATION:
            # Dehumidification: fixed fan speed, device controls temperature
            if DeviceFeatureEnum.SELECT_WIND_SPEED_7_GEAR in supported_features:
                desired_state["windSpeed7Gear"] = 2
                desired_state["windSpeedAutoSwitch"] = 0
        case ModeEnum.FAN:
            # Fan only: no compressor, auto fan speed
            if DeviceFeatureEnum.SELECT_WIND_SPEED_7_GEAR in supported_features:
                desired_state["windSpeedAutoSwitch"] = 1
                desired_state["windSpeed7Gear"] = 0
        case ModeEnum.HEAT:
            # Heat mode: similar to cool but with heating
            if DeviceFeatureEnum.SELECT_WIND_SPEED_7_GEAR in supported_features:
                desired_state["windSpeedAutoSwitch"] = 1
                desired_state["windSpeed7Gear"] = 0
    return desired_state
