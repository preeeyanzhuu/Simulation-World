from app.ai.memory import Memory

def test_memory_keeps_only_recent_items():
    m = Memory(max_size=3)
    for i in range(5):
        m.add(f"event_{i}")
    assert m.recent() == ["event_2", "event_3", "event_4"]
