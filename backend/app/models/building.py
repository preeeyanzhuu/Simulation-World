
class Building :
    def __init__(self, building_type, location, capacity, opening_time, closing_time, width, height):
        self.building_type = building_type
        self.location = location
        self.capacity = capacity
        self.opening_time = opening_time
        self.closing_time = closing_time
        self.width = width
        self.height = height

    def get_occupied_cells(self):
        row = self.location[0]
        col = self.location[1]
        cells = []
        for r in range(row, row + self.height):
            for c in range(col, col + self.width):
                cells.append((r, c))
        return cells

    def to_dict(self):
        return {
            "building_type": self.building_type,
            "location": self.location,
            "capacity": self.capacity,
            "opening_time": self.opening_time,
            "closing_time": self.closing_time,
            "width": self.width,
            "height": self.height
        }

class Hospital(Building):
    def __init__(self, location, capacity,):
        super().__init__("hospital", location, capacity, 0, 23, 2, 2)

class School(Building):
    def __init__(self, location, capacity,):
        super().__init__("school", location, capacity, 8, 15, 2, 2)

class Office(Building):
    def __init__(self, location, capacity):
        super().__init__("office", location, capacity, 9, 17, 2, 2)

class Park(Building):
    def __init__(self, location, capacity):
        super().__init__("park", location, capacity, 6, 22, 2, 3)

class Restaurant(Building):
    def __init__(self, location, capacity):
        super().__init__("restaurant", location, capacity, 11, 22, 2, 1)

class Shop(Building):
    def __init__(self, location, capacity):
        super().__init__("shop", location, capacity, 9, 20, 1, 1)

class House(Building):
    def __init__(self, location, capacity):
        super().__init__("house", location, capacity, 0, 23, 1, 1)






