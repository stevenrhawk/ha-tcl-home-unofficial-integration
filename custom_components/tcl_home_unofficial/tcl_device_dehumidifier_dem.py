"""."""

from homeassistant.core import HomeAssistant

from .calculations import try_get_value
from .data_storage import init_stored_device_data
from .device_enums import DehumidifierModeEnum
from .device_features import DeviceFeatureEnum


class TCL_Dehumidifier_DEM_DeviceData:
    def __init__(self, device_id: str, aws_thing_state: dict, delta: dict) -> None:
        self.device_id = device_id
        self.power_switch               = int(try_get_value(delta, aws_thing_state, "powerSwitch", -1))
        self.work_mode                  = int(try_get_value(delta, aws_thing_state, "workMode", -1))
        self.humidity                   = int(try_get_value(delta, aws_thing_state, "Humidity", -1))
        self.env_humidity               = int(try_get_value(delta, aws_thing_state, "envHumidity", -1))
        self.error_code                 = list[int](try_get_value(delta, aws_thing_state, "errorCode", []))



async def get_stored_dehumidifier_dem_data(
    hass: HomeAssistant, device_id: str
) -> dict[str, any]:
    return await init_stored_device_data(hass, device_id, [
        ("user_config.behavior.memorize_humidity_by_mode", False),
        ("humidity.Dry.value", 60),
        ("humidity.Turbo.value", 35),
        ("humidity.Comfort.value", 50),
        ("humidity.Continue.value", 15),
    ])


def handle_dehumidifier_dem_mode_change(desired_state:dict, value:DehumidifierModeEnum, supported_features: list[DeviceFeatureEnum], stored_data: dict) -> dict:
    match value:
        case DehumidifierModeEnum.DRY:
            pass
        case DehumidifierModeEnum.TURBO:
            pass
        case DehumidifierModeEnum.COMFORT:
            pass
        case DehumidifierModeEnum.CONTINUE:       
            pass
    return desired_state