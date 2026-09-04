class Weather:

    STATES = ["Sunny", "Cloudy", "Rain"]

    def __init__(self, initial_state="Sunny"):
        if initial_state not in self.STATES:
            raise ValueError(f"Invalid weather state: {initial_state}")
        self.current_state = initial_state
        self.ticks_remaining = 0 
        self.revert_to = "Sunny"         

    def set_state(self, state, duration_ticks=0):

        if state not in self.STATES:
            raise ValueError(f"Invalid weather state: {state}")
        self.current_state = state
        self.ticks_remaining = duration_ticks

    def trigger_rain(self, duration_ticks=20):
        self.set_state("Rain", duration_ticks=duration_ticks)

    def update(self):
        if self.ticks_remaining > 0:
            self.ticks_remaining -= 1
            if self.ticks_remaining == 0:
                self.current_state = self.revert_to
        return self.current_state

    def is_raining(self):
        return self.current_state == "Rain"
