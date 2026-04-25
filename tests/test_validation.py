import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.validation import Validator, ValidationError


def test_validate_task_strips_whitespace():
    assert Validator.validate_task("  Oil Change  ") == "Oil Change"


def test_validate_task_collapses_internal_whitespace():
    assert Validator.validate_task("Oil   Change") == "Oil Change"


def test_validate_task_empty_raises():
    with pytest.raises(ValidationError, match="empty"):
        Validator.validate_task("")


def test_validate_task_whitespace_only_raises():
    with pytest.raises(ValidationError, match="empty"):
        Validator.validate_task("   ")


def test_validate_task_too_long_raises():
    with pytest.raises(ValidationError, match="too long"):
        Validator.validate_task("x" * 201)


def test_validate_task_max_length_ok():
    Validator.validate_task("x" * 200)  # exactly at limit, should not raise


def test_validate_mileage_ok():
    assert Validator.validate_mileage(1500, 1000) == 1500


def test_validate_mileage_same_value_ok():
    assert Validator.validate_mileage(1000, 1000) == 1000


def test_validate_mileage_backward_raises():
    with pytest.raises(ValidationError, match="cannot be less than"):
        Validator.validate_mileage(900, 1000)


def test_validate_mileage_negative_raises():
    with pytest.raises(ValidationError, match="negative"):
        Validator.validate_mileage(-1, 0)


def test_validate_mileage_exceeds_max_raises():
    with pytest.raises(ValidationError, match="maximum"):
        Validator.validate_mileage(1_000_000, 0)


def test_validate_fuel_entry_ok():
    Validator.validate_fuel_entry(5.0, 30.0)  # should not raise


def test_validate_fuel_entry_zero_liters_raises():
    with pytest.raises(ValidationError, match="greater than zero"):
        Validator.validate_fuel_entry(0.0, 30.0)


def test_validate_fuel_entry_negative_liters_raises():
    with pytest.raises(ValidationError, match="greater than zero"):
        Validator.validate_fuel_entry(-1.0, 30.0)


def test_validate_fuel_entry_negative_price_raises():
    with pytest.raises(ValidationError, match="negative"):
        Validator.validate_fuel_entry(5.0, -10.0)


def test_validate_fuel_entry_zero_price_ok():
    Validator.validate_fuel_entry(5.0, 0.0)  # free fuel is unusual but valid
