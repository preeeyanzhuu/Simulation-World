DEFAULT_CLOSURE_DURATION_TICKS = 20

class RoadClosureState:
    def __init__(self):
        self._closed_roads = {}

    def close_road(self, road_id, duration_ticks=DEFAULT_CLOSURE_DURATION_TICKS):
        self._closed_roads[road_id] = duration_ticks

    def reopen_road(self, road_id):
        self._closed_roads.pop(road_id, None)

    def is_closed(self, road_id):
        return road_id in self._closed_roads

    def closed_road_ids(self):
        return list(self._closed_roads.keys())

    def update(self):
        expired = []
        for road_id in self._closed_roads:
            self._closed_roads[road_id] -= 1
            if self._closed_roads[road_id] <= 0:
                expired.append(road_id)
        for road_id in expired:
            del self._closed_roads[road_id]
        return self.closed_road_ids()

def trigger_road_closure(road_state, road_id, duration_ticks=DEFAULT_CLOSURE_DURATION_TICKS):
    road_state.close_road(road_id, duration_ticks=duration_ticks)
    return road_state.is_closed(road_id)
