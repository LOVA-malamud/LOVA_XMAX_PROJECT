import pytest
import tempfile
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database_manager import ScooterDB


@pytest.fixture
def db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    test_db = ScooterDB(db_path, "/nonexistent_migration.json")
    yield test_db
    os.unlink(db_path)


def test_init_creates_tables(db):
    import sqlite3
    with sqlite3.connect(db.db_path) as conn:
        tables = {row[0] for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()}
    expected = {
        "parts", "vehicle_stats", "maintenance_history", "tech_specs",
        "fuel_logs", "todo_list", "custom_mechanic_rules", "chat_history"
    }
    assert expected.issubset(tables)


def test_mileage_roundtrip(db):
    db.update_mileage(1000)
    assert db.get_mileage() == 1000


def test_mileage_backward_raises(db):
    db.update_mileage(5000)
    with pytest.raises(ValueError, match="cannot be less than"):
        db.update_mileage(4000)


def test_add_and_get_service_log(db):
    db.update_mileage(1000)
    db.add_service_log("2025-01-01", "Oil Change", 1000, 50.0, "Test note")
    history = db.get_history()
    assert len(history) == 1
    assert history[0]["task"] == "Oil Change"


def test_add_and_get_fuel_log(db):
    db.update_mileage(1200)
    db.add_fuel_log("2025-01-01", 1000, 5.0, 30.0)
    db.add_fuel_log("2025-01-15", 1200, 6.0, 36.0)
    fuel_df = db.get_fuel_history()
    assert len(fuel_df) == 2
    assert fuel_df.iloc[1]['km_diff'] == 200


def test_fuel_zero_diff_no_crash(db):
    db.update_mileage(1000)
    db.add_fuel_log("2025-01-01", 1000, 5.0, 30.0)
    db.add_fuel_log("2025-01-02", 1000, 3.0, 18.0)  # same km
    fuel_df = db.get_fuel_history()
    assert not fuel_df['l_100km'].isin([float('inf')]).any()


def test_seed_parts(db):
    parts = [("B6T-000", "Test Part", "Engine", 10.0, "No Image")]
    db.seed_parts(parts)
    results = db.search_parts("Test Part")
    assert not results.empty
    assert results.iloc[0]["Part_Number"] == "B6T-000"


def test_seed_parts_idempotent(db):
    parts = [("B6T-000", "Test Part", "Engine", 10.0, "No Image")]
    db.seed_parts(parts)
    db.seed_parts(parts)  # second call should be a no-op
    results = db.search_parts("Test Part")
    assert len(results) == 1


def test_todo_roundtrip(db):
    db.add_todo_item("Fix brake", "High")
    todo = db.get_todo_list()
    assert len(todo) == 1
    assert todo.iloc[0]["task"] == "Fix brake"

    db.complete_todo_item(todo.iloc[0]["id"])
    todo_after = db.get_todo_list()
    assert len(todo_after) == 0


def test_chat_history_persistence(db):
    db.save_chat_message("user", "Hello")
    db.save_chat_message("assistant", "Hi there!")
    history = db.get_chat_history()
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[1]["content"] == "Hi there!"

    db.clear_chat_history()
    assert db.get_chat_history() == []


def test_search_parts_parameterized(db):
    parts = [
        ("B6T-001", "Oil Filter", "Engine", 8.5, "No Image"),
        ("B6T-002", "Air Filter", "Engine", 22.0, "No Image"),
    ]
    db.seed_parts(parts)
    results = db.search_parts("Oil")
    assert len(results) == 1
    assert results.iloc[0]["Description"] == "Oil Filter"
