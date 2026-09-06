from app.models.citizen import Citizen, Doctor, Teacher, Shopkeeper, OfficeWorker, Student


def test_base_citizen_defaults():
    c = Citizen(name="Alex", age=40)
    assert c.occupation == "none"
    assert c.energy == 100
    assert c.hunger == 0
    assert c.money == 50
    assert c.happiness == 70
    assert c.is_alive is True
    assert c.cause_of_death is None


def test_doctor():
    d = Doctor(name="Dr. Rao", age=45)
    assert d.occupation == "doctor"
    assert d.workplace == "hospital"


def test_teacher():
    t = Teacher(name="Ms. Iyer", age=38)
    assert t.occupation == "teacher"
    assert t.workplace == "school"


def test_shopkeeper():
    s = Shopkeeper(name="Raj", age=50)
    assert s.occupation == "shopkeeper"
    assert s.workplace == "mall"


def test_office_worker():
    o = OfficeWorker(name="Priya", age=29)
    assert o.occupation == "office_worker"
    assert o.workplace == "office"


def test_student_and_allowance():
    st = Student(name="Aarav", age=16)
    assert st.occupation == "student"
    assert st.workplace == "school"
    assert st.money == 50   # starts like everyone else

    st.receive_allowance()
    assert st.money == 65   # +15 default daily_allowance


def test_death_status():
    c = Citizen(name="Test", age=30)
    assert c.is_alive is True
    c.die(reason="starvation")
    assert c.is_alive is False
    assert c.cause_of_death == "starvation"


if __name__ == "__main__":
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    for test in tests:
        test()
        print(f"PASS: {test.__name__}")

    print("\n--- one of each citizen, printed ---")
    for c in [
        Citizen(name="Generic", age=99),
        Doctor(name="Dr. Rao", age=45),
        Teacher(name="Ms. Iyer", age=38),
        Shopkeeper(name="Raj", age=50),
        OfficeWorker(name="Priya", age=29),
        Student(name="Aarav", age=16),
    ]:
        print(c)

    print(f"\n{len(tests)}/{len(tests)} tests passed.")
