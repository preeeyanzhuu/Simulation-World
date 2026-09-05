class Memory:
    def __init__(self, max_size=5):
        self.history = []
        self.max_size = max_size

    def add(self, event):
        self.history.append(event)
        if len(self.history) > self.max_size:
            self.history.pop(0)

    def recent(self):
        return self.history
