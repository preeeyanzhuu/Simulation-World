class StreetLight:

    def __init__(self):
        self.is_on = False

    def turn_on(self):
        self.is_on = True

    def turn_off(self):
        self.is_on = False

    def update(self, hour):
        if hour >= 18 or hour < 6:
            self.turn_on()
        else:
            self.turn_off()
        return self.is_on


def get_time_period(hour):

    if not (0 <= hour <= 23):
        raise ValueError("hour must be between 0 and 23")
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 18:
        return "afternoon"
    else:
        return "evening"
