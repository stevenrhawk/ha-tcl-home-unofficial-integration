def celsius_to_fahrenheit(celsius: int | float) -> int | float:
    return round((celsius * (9 / 5)) + 32)


def fahrenheit_to_celsius(fahrenheit: int | float) -> float:
    # Round to the nearest 0.5 °C, matching the device's native resolution
    # (e.g. 69 °F -> 20.5 °C, which is exactly what the unit reports back).
    return round(((fahrenheit - 32) * (5 / 9)) * 2) / 2


def is_fahrenheit_device(device) -> bool:
    """True when the unit is running in Fahrenheit mode (temperatureType == 1)."""
    return getattr(device.data, "temperature_type", 0) == 1


def fahrenheit_target_temp(device) -> int | float:
    """Authoritative °F setpoint: targetFahrenheitTemp as reported by the
    device, falling back to converting the Celsius setpoint."""
    tft = getattr(device.data, "target_fahrenheit_temp", -1)
    if tft is not None and tft != -1:
        return tft
    return celsius_to_fahrenheit(device.data.target_temperature)


def try_get_value(delta: dict, state: dict, key: str, default=any):
    if key in delta:
        return delta.get(key, default)

    if key in state:
        return state.get(key, default)

    return default
