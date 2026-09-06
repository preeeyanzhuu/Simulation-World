from app.engine.scheduler import SimClock


def test_starts_at_expected_defaults():
    c = SimClock()
    assert c.tick == 0
    assert c.hour == 6
    assert c.day == 1


def test_hour_advances_every_10_ticks():
    c = SimClock()
    for _ in range(9):
        c.update()
    assert c.hour == 6
    c.update()
    assert c.hour == 7


def test_new_hour_flag_only_true_on_the_boundary_tick():
    c = SimClock()
    for i in range(10):
        c.update()
        if i < 9:
            assert c.new_hour is False
        else:
            assert c.new_hour is True


def test_day_increments_and_wraps_hour_at_midnight():
    c = SimClock()
    for _ in range(180):
        c.update()
    assert c.hour == 0
    assert c.day == 2


def test_new_day_flag_only_true_once_per_day():
    c = SimClock()
    new_day_ticks = []
    for _ in range(250):
        c.update()
        if c.new_day:
            new_day_ticks.append(c.tick)
    assert new_day_ticks == [180]


def test_get_time_period_matches_hour():
    c = SimClock()
    assert c.get_time_period() == "morning"

    for _ in range(60):
        c.update()
    assert c.hour == 12
    assert c.get_time_period() == "afternoon"


if __name__ == "__main__":
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    for test in tests:
        test()
        print(f"PASS: {test.__name__}")
    print(f"\n{len(tests)}/{len(tests)} tests passed.")
