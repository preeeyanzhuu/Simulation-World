class Citizen:

    def __init__(self, name, age, occupation="none"):
        self.name = name
        self.age = age
        self.occupation = occupation
        self.energy = 100
        self.hunger = 0
        self.money = 50
        self.happiness = 70
        self.is_alive = True
        self.cause_of_death = None

    def die(self, reason="unknown"):
        self.is_alive = False
        self.cause_of_death = reason

    def __repr__(self):
        status = "alive" if self.is_alive else f"dead ({self.cause_of_death})"
        return (f"{self.__class__.__name__}(name={self.name!r}, age={self.age}, "
                f"occupation={self.occupation!r}, energy={self.energy}, "
                f"hunger={self.hunger}, money={self.money}, "
                f"happiness={self.happiness}, status={status})")


class Doctor(Citizen):
    def __init__(self, name, age):
        super().__init__(name, age, occupation="doctor")
        self.workplace = "hospital"


class Teacher(Citizen):
    def __init__(self, name, age):
        super().__init__(name, age, occupation="teacher")
        self.workplace = "school"


class Shopkeeper(Citizen):
    def __init__(self, name, age):
        super().__init__(name, age, occupation="shopkeeper")
        self.workplace = "mall"


class OfficeWorker(Citizen):
    def __init__(self, name, age):
        super().__init__(name, age, occupation="office_worker")
        self.workplace = "office"


class Student(Citizen):
    def __init__(self, name, age, daily_allowance=15):
        super().__init__(name, age, occupation="student")
        self.workplace = "school"
        self.daily_allowance = daily_allowance

    def receive_allowance(self):
        self.money += self.daily_allowance
