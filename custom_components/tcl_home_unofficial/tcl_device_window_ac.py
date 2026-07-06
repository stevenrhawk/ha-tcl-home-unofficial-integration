"""."""

from homeassistant.core import HomeAssistant

from .calculations import try_get_value
from .data_storage import init_stored_device_data
from .device_enums import ModeEnum
from .device_features import DeviceFeatureEnum


class TCL_WindowAC_DeviceData:
    def __init__(self, device_id: str, aws_thing_state: dict, delta: dict) -> None:
        self.device_id = device_id
        self.power_switch = int(
            try_get_value(delta, aws_thing_state, "powerSwitch", -1)
        )
        self.wind_speed = int(try_get_value(delta, aws_thing_state, "windSpeed", -1))
        self.work_mode = int(try_get_value(delta, aws_thing_state, "workMode", -1))
        self.target_temperature = float(
            try_get_value(delta, aws_thing_state, "targetTemperature", -1)
        )
        self.current_temperature = float(
            try_get_value(delta, aws_thing_state, "currentTemperature", -1)
        )
        self.sleep = int(try_get_value(delta, aws_thing_state, "sleep", -1))
        self.eco = int(try_get_value(delta, aws_thing_state, "ECO", -1))
        self.beep_switch = int(try_get_value(delta, aws_thing_state, "beepSwitch", -1))
        self.screen = int(try_get_value(delta, aws_thing_state, "screen", -1))


async def get_stored_window_ac_data(
    hass: HomeAssistant, device_id: str
) -> dict[str, any]:
    default_wind_speed = "Auto"
    return await init_stored_device_data(hass, device_id, [
        ("user_config.behavior.memorize_temp_by_mode", False),
        ("user_config.behavior.memorize_fan_speed_by_mode", False),
        ("user_config.behavior.silent_beep_when_turn_on", False),
        ("target_temperature.Cool.value", 22),
        ("user_config.settings.native_temp_step", 1.0),
        ("user_config.settings.min_temp", 16),
        ("user_config.settings.max_temp", 31),
        ("fan_speed.Cool.value", default_wind_speed),
        ("fan_speed.Dehumidification.value", default_wind_speed),
        ("fan_speed.Fan.value", default_wind_speed),
        ("fan_speed.Auto.value", default_wind_speed),
    ])


def handle_window_ac_mode_change(
    desired_state: dict,
    value: ModeEnum,
    supported_features: list[DeviceFeatureEnum],
    stored_data: dict,
) -> dict:
    match value:
        case ModeEnum.AUTO:
            desired_state["ECO"] = 0
            desired_state["windSpeed"] = 0
            desired_state["sleep"] = 0
        case ModeEnum.COOL:
            desired_state["ECO"] = 1
            desired_state["windSpeed"] = 0
            desired_state["sleep"] = 0
        case ModeEnum.DEHUMIDIFICATION:
            desired_state["ECO"] = 1
            desired_state["windSpeed"] = 2
            desired_state["sleep"] = 0
        case ModeEnum.FAN:
            desired_state["ECO"] = 0
            desired_state["windSpeed"] = 0
            desired_state["sleep"] = 0
    return desired_state
