class SimClock:
    def __init__(self):
        self.tick = 0
        self.hour = 6

    def update(self):
        self.tick += 1
        if self.tick % 10 == 0:
            self.hour = (self.hour + 1) % 24

if __name__ == "__main__":
    clock = SimClock()
    for i in range (25):
        clock.update()
        print(clock.tick, clock.hour)

