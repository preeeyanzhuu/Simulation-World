from app.models.citizen import Citizen, Student
from app.ai.currency import get_currency
from app.ai.decision import decide
from app.ai.learning import get_state, calculate_reward


def make_worker(money=5, energy=80, hunger=20, happiness=70):
    c = Citizen(name="Worker", age=30, occupation="office_worker")
    c.hunger = hunger
    c.energy = energy
    c.money = money
    c.happiness = happiness
    return c


def make_student(money=5, energy=80, hunger=20, happiness=70):
    st = Student(name="Student", age=16)
    st.hunger = hunger
    st.energy = energy
    st.money = money
    st.happiness = happiness
    return st


def test_get_currency_returns_money_for_everyone():
    worker = make_worker(money=42)
    student = make_student(money=17)

    assert get_currency(worker) == 42
    assert get_currency(student) == 17
    print("PASS: get_currency reads money for both workers and students\n")


def test_decide_sends_worker_to_work_and_student_to_school():
    worker = make_worker(money=5)
    student = make_student(money=5)

    worker_action = decide(worker)
    student_action = decide(student)

    print(f"Broke worker decides: {worker_action}")
    print(f"Broke student decides: {student_action}")

    assert worker_action == "go_work"
    assert student_action == "go_school"
    print("PASS: decide() routes worker->go_work, student->go_school\n")


def test_decide_sends_low_happiness_citizen_to_mall():
    citizen = make_worker(money=50, happiness=10)
    action = decide(citizen)
    print(f"Rich but unhappy citizen decides: {action}")
    assert action == "go_mall"
    print("PASS: decide() sends low-happiness citizens to the mall\n")


def test_student_allowance_increases_money():
    student = make_student(money=5)
    student.receive_allowance()
    print(f"Student money after allowance: {student.money}")
    assert student.money == 5 + student.daily_allowance
    print("PASS: receive_allowance() correctly adds to money\n")


def test_reward_school_vs_work_are_occupation_gated():
    worker = make_worker(money=5)
    student = make_student(money=5)

    worker_school_reward = calculate_reward(worker, "go_school")
    student_work_reward = calculate_reward(student, "go_work")
    worker_work_reward = calculate_reward(worker, "go_work")
    student_school_reward = calculate_reward(student, "go_school")

    print(f"worker doing go_school (wrong):  {worker_school_reward}")
    print(f"student doing go_work (wrong):   {student_work_reward}")
    print(f"worker doing go_work (right):    {worker_work_reward}")
    print(f"student doing go_school (right): {student_school_reward}")

    assert worker_work_reward > worker_school_reward
    assert student_school_reward > student_work_reward
    print("PASS: reward correctly gates go_work/go_school by occupation\n")


if __name__ == "__main__":
    test_get_currency_returns_money_for_everyone()
    test_decide_sends_worker_to_work_and_student_to_school()
    test_decide_sends_low_happiness_citizen_to_mall()
    test_student_allowance_increases_money()
    test_reward_school_vs_work_are_occupation_gated()
    print("All currency/occupation tests passed.")
