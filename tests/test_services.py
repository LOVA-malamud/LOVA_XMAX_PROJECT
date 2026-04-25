import pytest
import sys
import os
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.maintenance import get_predictive_tasks, get_health_status, estimate_due_date
import config


def test_get_predictive_tasks_includes_vbelt_and_air():
    tasks = get_predictive_tasks(config.MAINTENANCE_INTERVALS)
    assert "V-Belt" in tasks
    assert "Air Filters" in tasks


def test_get_predictive_tasks_excludes_non_predictive():
    tasks = get_predictive_tasks(config.MAINTENANCE_INTERVALS)
    assert "Engine Oil (10W40)" not in tasks


def test_health_status_at_zero_km():
    status = get_health_status("Engine Oil (10W40)", 1000, 1000)
    assert status["pct_remaining"] == 100.0
    assert status["km_left"] == 5000
    assert status["status"] == "ok"


def test_health_status_overdue():
    # 10000 km since last oil change, interval 5000
    status = get_health_status("Engine Oil (10W40)", 10000, 0)
    assert status["pct_remaining"] == 0.0
    assert status["km_left"] == -5000
    assert status["status"] == "critical"


def test_health_status_warning():
    # km_since = 4000, interval = 5000 → pct = 20% → warning
    status = get_health_status("Engine Oil (10W40)", 4000, 0)
    assert 15.0 < status["pct_remaining"] <= 40.0
    assert status["status"] == "warning"


def test_health_status_critical_boundary():
    # km_since = 4300, interval = 5000 → pct = 14% → critical
    status = get_health_status("Engine Oil (10W40)", 4300, 0)
    assert status["pct_remaining"] <= 15.0
    assert status["status"] == "critical"


def test_estimate_due_date_normal():
    due = estimate_due_date(500, 20.0)
    expected = date.today() + timedelta(days=25)
    assert due == expected


def test_estimate_due_date_zero_avg_returns_none():
    assert estimate_due_date(500, 0.0) is None


def test_estimate_due_date_negative_km_returns_none():
    assert estimate_due_date(-100, 20.0) is None


def test_estimate_due_date_zero_km_returns_none():
    assert estimate_due_date(0, 20.0) is None
