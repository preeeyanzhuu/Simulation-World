class TrafficLight:

    CYCLE = ["Red", "Green", "Yellow"]

    DURATIONS = {
        "Red": 8,
        "Green": 6,
        "Yellow": 2,
    }

    def __init__(self, initial_state="Red"):
        if initial_state not in self.CYCLE:
            raise ValueError(f"Invalid traffic light state: {initial_state}")
        self.current_state = initial_state
        self.ticks_in_state = 0

    def update(self):
        self.ticks_in_state += 1
        if self.ticks_in_state >= self.DURATIONS[self.current_state]:
            self._advance()
            self.ticks_in_state = 0
        return self.current_state

    def _advance(self):
        idx = self.CYCLE.index(self.current_state)
        self.current_state = self.CYCLE[(idx + 1) % len(self.CYCLE)]

    def is_stop(self):
        return self.current_state in ("Red", "Yellow")
