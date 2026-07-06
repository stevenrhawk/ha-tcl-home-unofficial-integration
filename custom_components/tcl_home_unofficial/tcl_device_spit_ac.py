"""."""

from homeassistant.core import HomeAssistant

from .calculations import try_get_value
from .data_storage import init_stored_device_data
from .device_enums import ModeEnum
from .device_features import DeviceFeatureEnum


class TCL_SplitAC_DeviceData:
    def __init__(self, device_id: str, aws_thing_state: dict, delta: dict) -> None:
        self.device_id = device_id
        self.power_switch               = int(try_get_value(delta, aws_thing_state, "powerSwitch", -1))
        self.beep_switch                = int(try_get_value(delta, aws_thing_state, "beepSwitch", -1))
        self.screen                     = int(try_get_value(delta, aws_thing_state, "screen", -1))
        self.target_temperature         = float(try_get_value(delta, aws_thing_state, "targetTemperature", -1))
        self.current_temperature        = float(try_get_value(delta, aws_thing_state, "currentTemperature", -1))
        self.target_fahrenheit_temp     = int(try_get_value(delta, aws_thing_state, "targetFahrenheitTemp", -1))
        self.temperature_type           = int(try_get_value(delta, aws_thing_state, "temperatureType", 0))
        self.work_mode                  = int(try_get_value(delta, aws_thing_state, "workMode", -1))
        self.high_temperature_wind      = int(try_get_value(delta, aws_thing_state, "highTemperatureWind", -1))
        self.turbo                      = int(try_get_value(delta, aws_thing_state, "turbo", -1))
        self.silence_switch             = int(try_get_value(delta, aws_thing_state, "silenceSwitch", -1))
        self.wind_speed                 = int(try_get_value(delta, aws_thing_state, "windSpeed", -1))
        self.vertical_switch            = int(try_get_value(delta, aws_thing_state, "verticalSwitch", -1))
        self.vertical_direction         = int(try_get_value(delta, aws_thing_state, "verticalDirection", -1))
        self.horizontal_switch          = int(try_get_value(delta, aws_thing_state, "horizontalSwitch", -1))
        self.horizontal_direction       = int(try_get_value(delta, aws_thing_state, "horizontalDirection", -1))
        self.eight_add_hot              = int(try_get_value(delta, aws_thing_state, "eightAddHot", -1))
        self.sleep                      = int(try_get_value(delta, aws_thing_state, "sleep", -1))
        self.eco                        = int(try_get_value(delta, aws_thing_state, "ECO", -1))
        self.healthy                    = int(try_get_value(delta, aws_thing_state, "healthy", -1))
        self.anti_moldew                = int(try_get_value(delta, aws_thing_state, "antiMoldew", -1))
        self.self_clean                 = int(try_get_value(delta, aws_thing_state, "selfClean", -1))
        self.wind_speed_auto_switch     = int(try_get_value(delta, aws_thing_state, "windSpeedAutoSwitch", -1))
        self.wind_speed_7_gear          = int(try_get_value(delta, aws_thing_state, "windSpeed7Gear", -1))
        self.soft_wind                  = int(try_get_value(delta, aws_thing_state, "softWind", -1))
        self.ai_eco                     = int(try_get_value(delta, aws_thing_state, "AIECOSwitch", -1))
        self.external_unit_temperature  = int(try_get_value(delta, aws_thing_state, "externalUnitTemperature", -1))
        self.generator_mode             = int(try_get_value(delta, aws_thing_state, "generatorMode", -1))
        self.sensor_TVOC_level          = int(try_get_value(delta, aws_thing_state, "sensorTVOCLevel", -1))
        self.new_wind_switch            = int(try_get_value(delta, aws_thing_state, "newWindSwitch", -1))
        self.new_wind_auto_switch       = int(try_get_value(delta, aws_thing_state, "newWindAutoSwitch", -1))
        self.new_wind_strength          = int(try_get_value(delta, aws_thing_state, "newWindStrength", -1))
        self.sensor_TVOC_value          = float(try_get_value(delta, aws_thing_state, "sensorTVOCValue", -1))

async def get_stored_spit_ac_data(
    hass: HomeAssistant, device_id: str
) -> dict[str, any]:
    default_wind_speed = "Auto"
    return await init_stored_device_data(hass, device_id, [
        ("user_config.behavior.memorize_temp_by_mode", False),
        ("user_config.behavior.memorize_fan_speed_by_mode", False),
        ("user_config.behavior.silent_beep_when_turn_on", False),
        ("user_config.settings.native_temp_step", 1.0),
        ("user_config.settings.min_temp", 16),
        ("user_config.settings.max_temp", 36),
        ("target_temperature.Cool.value", 24),
        ("target_temperature.Heat.value", 36),
        ("target_temperature.Dehumidification.value", 24),
        ("target_temperature.Fan.value", 24),
        ("target_temperature.Auto.value", 24),
        ("fan_speed.Cool.value", default_wind_speed),
        ("fan_speed.Heat.value", default_wind_speed),
        ("fan_speed.Dehumidification.value", default_wind_speed),
        ("fan_speed.Fan.value", default_wind_speed),
        ("fan_speed.Auto.value", default_wind_speed),
    ])

def handle_split_ac_mode_change(desired_state:dict, value:ModeEnum, supported_features: list[DeviceFeatureEnum], stored_data: dict) -> dict:
    match value:
        case ModeEnum.AUTO:
            if (DeviceFeatureEnum.INTERNAL_HAS_TURBO_PROPERTY in supported_features):
                desired_state["turbo"] = 0
                desired_state["ECO"] = 0
            if (DeviceFeatureEnum.SWITCH_8_C_HEATING in supported_features):
                desired_state["eightAddHot"] = 0
            if (DeviceFeatureEnum.SELECT_WIND_SPEED_7_GEAR in supported_features):
                desired_state["windSpeedAutoSwitch"] = 1
                desired_state["windSpeed7Gear"] = 0
            if (DeviceFeatureEnum.SELECT_WIND_SPEED in supported_features):
                desired_state["windSpeed"] = 0                                    
        case ModeEnum.COOL:
            if (DeviceFeatureEnum.INTERNAL_HAS_TURBO_PROPERTY in supported_features):
                desired_state["turbo"] = 0
                desired_state["ECO"] = 0
                desired_state["targetTemperature"] = 24
            if (DeviceFeatureEnum.SWITCH_8_C_HEATING in supported_features):
                desired_state["eightAddHot"] = 0
            if (DeviceFeatureEnum.SELECT_WIND_SPEED_7_GEAR in supported_features):
                desired_state["windSpeedAutoSwitch"] = 1
                desired_state["windSpeed7Gear"] = 0
            if (DeviceFeatureEnum.SELECT_WIND_SPEED in supported_features):
                desired_state["windSpeed"] = 0
        case ModeEnum.DEHUMIDIFICATION:
            if (DeviceFeatureEnum.INTERNAL_HAS_TURBO_PROPERTY in supported_features):
                desired_state["turbo"] = 0
                desired_state["ECO"] = 0
            if (DeviceFeatureEnum.SWITCH_8_C_HEATING in supported_features):
                desired_state["eightAddHot"] = 0
            if (DeviceFeatureEnum.SELECT_WIND_SPEED_7_GEAR in supported_features):
                desired_state["windSpeed7Gear"] = 2
                desired_state["windSpeedAutoSwitch"] = 0
            if (DeviceFeatureEnum.SELECT_WIND_SPEED in supported_features):
                desired_state["windSpeed"] = 2
        case ModeEnum.FAN:            
            if (DeviceFeatureEnum.INTERNAL_HAS_TURBO_PROPERTY in supported_features):
                desired_state["turbo"] = 0
                desired_state["ECO"] = 0
            if (DeviceFeatureEnum.SWITCH_8_C_HEATING in supported_features):
                desired_state["eightAddHot"] = 0
            if (DeviceFeatureEnum.SELECT_WIND_SPEED_7_GEAR in supported_features):
                desired_state["windSpeedAutoSwitch"] = 1
                desired_state["windSpeed7Gear"] = 0
            if (DeviceFeatureEnum.SELECT_WIND_SPEED in supported_features):
                desired_state["windSpeed"] = 0
        case ModeEnum.HEAT:
            if (DeviceFeatureEnum.INTERNAL_HAS_TURBO_PROPERTY in supported_features):
                desired_state["turbo"] = 0
                desired_state["ECO"] = 0
                desired_state["targetTemperature"] = 26
            if (DeviceFeatureEnum.SWITCH_8_C_HEATING in supported_features):
                desired_state["eightAddHot"] = 0
            if (DeviceFeatureEnum.SELECT_WIND_SPEED_7_GEAR in supported_features):
                desired_state["windSpeedAutoSwitch"] = 1
                desired_state["windSpeed7Gear"] = 0
            if (DeviceFeatureEnum.SELECT_WIND_SPEED in supported_features):
                desired_state["windSpeed"] = 0
    return desired_state