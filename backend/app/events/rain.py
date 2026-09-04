
DEFAULT_RAIN_DURATION_TICKS = 20

def trigger_rain(weather, duration_ticks=DEFAULT_RAIN_DURATION_TICKS):
    weather.trigger_rain(duration_ticks=duration_ticks)
    return weather.current_state
