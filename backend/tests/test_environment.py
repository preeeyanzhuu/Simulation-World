from app.environment.weather import Weather
from app.environment.daytime import StreetLight, get_time_period
from app.events.traffic_light import TrafficLight
from app.events.rain import trigger_rain
from app.events.tax import TaxState, trigger_tax_hike
from app.events.traffic import RoadClosureState, trigger_road_closure

def test_weather_starts_at_given_state():
    w = Weather(initial_state="Sunny")
    assert w.current_state == "Sunny"
    assert w.is_raining() is False


def test_weather_does_not_change_on_its_own():
    w = Weather(initial_state="Sunny")
    for _ in range(100):
        w.update()
    assert w.current_state == "Sunny"


def test_weather_set_state_and_is_raining():
    w = Weather()
    w.set_state("Rain")
    assert w.current_state == "Rain"
    assert w.is_raining() is True


def test_weather_rejects_invalid_state():
    try:
        Weather(initial_state="Snow")
        assert False, "should have raised ValueError"
    except ValueError:
        pass


def test_weather_rain_reverts_after_duration():
    w = Weather()
    w.trigger_rain(duration_ticks=3)
    assert w.is_raining() is True

    w.update()
    assert w.is_raining() is True
    w.update()
    assert w.is_raining() is True
    w.update()
    assert w.is_raining() is False
    assert w.current_state == "Sunny"


def test_weather_untimed_state_persists():
    w = Weather()
    w.set_state("Cloudy")
    for _ in range(50):
        w.update()
    assert w.current_state == "Cloudy"

def test_trigger_rain_event_starts_rain():
    w = Weather()
    trigger_rain(w, duration_ticks=5)
    assert w.is_raining() is True
    assert w.ticks_remaining == 5


def test_trigger_rain_event_reverts_after_duration():
    w = Weather()
    trigger_rain(w, duration_ticks=2)
    w.update()
    w.update()
    assert w.is_raining() is False

def test_tax_hike_starts_inactive():
    t = TaxState()
    assert t.active is False
    assert t.multiplier == 1.0


def test_trigger_tax_hike_activates_and_reduces_multiplier():
    t = TaxState()
    trigger_tax_hike(t, duration_ticks=4, multiplier=0.7)
    assert t.active is True
    assert t.multiplier == 0.7


def test_tax_hike_reverts_after_duration():
    t = TaxState()
    trigger_tax_hike(t, duration_ticks=2)
    t.update()
    assert t.active is True
    t.update()
    assert t.active is False
    assert t.multiplier == 1.0


def test_street_light_on_at_night():
    light = StreetLight()
    light.update(hour=20)
    assert light.is_on is True


def test_street_light_off_during_day():
    light = StreetLight()
    light.update(hour=14)
    assert light.is_on is False


def test_street_light_boundary_hours():
    light = StreetLight()
    light.update(hour=18)
    assert light.is_on is True
    light.update(hour=17)
    assert light.is_on is False
    light.update(hour=5)
    assert light.is_on is True
    light.update(hour=6)
    assert light.is_on is False


def test_get_time_period_buckets():
    assert get_time_period(7) == "morning"
    assert get_time_period(11) == "morning"
    assert get_time_period(12) == "afternoon"
    assert get_time_period(17) == "afternoon"
    assert get_time_period(18) == "evening"
    assert get_time_period(2) == "evening"


def test_get_time_period_rejects_bad_hour():
    try:
        get_time_period(25)
        assert False, "should have raised ValueError"
    except ValueError:
        pass

def test_road_closure_starts_empty():
    r = RoadClosureState()
    assert r.is_closed("road_1") is False
    assert r.closed_road_ids() == []


def test_trigger_road_closure_blocks_road():
    r = RoadClosureState()
    trigger_road_closure(r, "road_1", duration_ticks=5)
    assert r.is_closed("road_1") is True
    assert r.is_closed("road_2") is False


def test_road_closure_reopens_after_duration():
    r = RoadClosureState()
    trigger_road_closure(r, "road_1", duration_ticks=2)
    r.update()
    assert r.is_closed("road_1") is True
    r.update()
    assert r.is_closed("road_1") is False


def test_multiple_roads_close_independently():
    r = RoadClosureState()
    trigger_road_closure(r, "road_1", duration_ticks=2)
    trigger_road_closure(r, "road_2", duration_ticks=5)
    r.update()
    r.update()
    assert r.is_closed("road_1") is False
    assert r.is_closed("road_2") is True

def test_traffic_light_starts_red():
    t = TrafficLight()
    assert t.current_state == "Red"
    assert t.is_stop() is True


def test_traffic_light_cycles_correctly():
    t = TrafficLight(initial_state="Red")
    for _ in range(TrafficLight.DURATIONS["Red"]):
        t.update()
    assert t.current_state == "Green"
    assert t.is_stop() is False

    for _ in range(TrafficLight.DURATIONS["Green"]):
        t.update()
    assert t.current_state == "Yellow"
    assert t.is_stop() is True

    for _ in range(TrafficLight.DURATIONS["Yellow"]):
        t.update()
    assert t.current_state == "Red"


if __name__ == "__main__":
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    passed = 0
    for test in tests:
        test()
        passed += 1
        print(f"PASS: {test.__name__}")
    print(f"\n{passed}/{len(tests)} tests passed.")
