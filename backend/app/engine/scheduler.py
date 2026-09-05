from app.environment.daytime import get_time_period as _get_time_period

class SimClock:

    TICKS_PER_HOUR = 10
    HOURS_PER_DAY = 24

    def __init__(self):
        self.tick = 0
        self.hour = 6
        self.day = 1
        self.new_hour = False
        self.new_day = False

    def update(self):
        self.tick += 1
        self.new_hour = False
        self.new_day = False

        if self.tick % self.TICKS_PER_HOUR == 0:
            self.hour = (self.hour + 1)% self.HOURS_PER_DAY
            self.new_hour =True

            if self.hour == 0:
                self.day +=1
                self.new_day = True

    def get_time_period(self):
        return _get_time_period(self.hour)

if __name__ == "__main__":
    clock = SimClock()
    for i in range (250):
        clock.update()
        if clock.new_day:
            print(f"tick={clock.tick:4} day={clock.day} hour={clock.hour}"
                  f"period={clock.get_time_period()} <-- NEW DAY")

        else:
            print(f"tick={clock.tick:4} day={clock.day} hour={clock.hour}"
                  f"period={clock.get_time_period()} <-- NEW DAY")
