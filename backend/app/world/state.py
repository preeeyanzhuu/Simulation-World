from app.world.city import create_grid
from app.engine.scheduler import SimClock
from app.environment.weather import Weather
from app.environment.daytime import StreetLight
from app.events.tax import TaxState
from app.events.traffic import RoadClosureState


class CityState:
    def __init__(self):
        self.grid = create_grid()
        self.clock = SimClock()
        self.weather = Weather()
        self.tax_state = TaxState()
        self.road_closures = RoadClosureState()
        self.street_light = StreetLight()
        self.citizens = []
        self.buildings = []
        self.building_entrances = {}
        self.entrance_by_building = {}  
        self.roads = []
        self.intersections = set()  
        self.reward_history = []

    def add_citizen(self, citizen):
        self.citizens.append(citizen)

    def update(self):
        self.clock.update()
        self.weather.update()
        self.tax_state.update()
        self.road_closures.update()
        self.street_light.update(self.clock.hour)


city_state = CityState()
