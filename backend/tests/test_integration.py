from app.models.citizen import Citizen
from app.environment.weather import Weather
from app.events.rain import trigger_rain
from app.events.tax import TaxState, trigger_tax_hike
from app.ai.learning import get_state, build_event_flags, calculate_reward, QLearner


def make_citizen():
    c = Citizen(name="Test", age=25, occupation="learning_agent")
    c.hunger = 20
    c.energy = 80
    c.money = 5
    return c


def test_get_state_reflects_both_rain_and_tax():
    citizen = make_citizen()
    weather = Weather()
    tax = TaxState()

    flags = build_event_flags(weather, tax)
    state = get_state(citizen, "morning", events=flags)
    assert state[-2:] == (False, False)

    trigger_rain(weather, duration_ticks=5)
    flags = build_event_flags(weather, tax)
    state = get_state(citizen, "morning", events=flags)
    assert state[-2:] == (True, False)

    trigger_tax_hike(tax, duration_ticks=5)
    flags = build_event_flags(weather, tax)
    state = get_state(citizen, "morning", events=flags)
    assert state[-2:] == (True, True)

    print("PASS: get_state reflects rain + tax hike, independently and combined")


def test_reward_reduced_for_go_work_during_tax_hike():
    citizen = make_citizen()
    tax = TaxState()

    normal_reward = calculate_reward(citizen, "go_work", tax_state=tax)

    trigger_tax_hike(tax, duration_ticks=5, multiplier=0.7)
    hiked_reward = calculate_reward(citizen, "go_work", tax_state=tax)

    print(f"go_work reward, no hike:  {normal_reward}")
    print(f"go_work reward, w/ hike:  {hiked_reward}")

    assert hiked_reward < normal_reward, "reward should be lower for go_work during a tax hike"
    print("PASS: calculate_reward scales down go_work bonus during a tax hike\n")


def test_reward_unaffected_when_tax_state_omitted():
    """Backward compatibility: old calls with no tax_state arg still work."""
    citizen = make_citizen()
    reward = calculate_reward(citizen, "go_work")
    assert reward == -0.05 + 1
    print("PASS: calculate_reward still works with tax_state omitted (backward compatible)\n")


def test_full_training_step_with_real_environment():
    citizen = make_citizen()
    weather = Weather()
    tax = TaxState()
    learner = QLearner(actions=["go_home", "go_restaurant", "go_work", "idle"])

    trigger_rain(weather, duration_ticks=10)
    trigger_tax_hike(tax, duration_ticks=10)

    state = get_state(citizen, "morning", events=build_event_flags(weather, tax))
    action = learner.choose_action(state)
    reward = calculate_reward(citizen, action, tax_state=tax)
    next_state = get_state(citizen, "morning", events=build_event_flags(weather, tax))
    learner.update(state, action, reward, next_state)

    print(f"state:  {state}")
    print(f"action: {action}")
    print(f"reward: {reward}")
    print("PASS: full tick runs end-to-end with real environment + event objects\n")

if __name__ == "__main__":
    test_get_state_reflects_both_rain_and_tax()
    test_reward_reduced_for_go_work_during_tax_hike()
    test_reward_unaffected_when_tax_state_omitted()
    test_full_training_step_with_real_environment()
    print("All integration tests passed.")
