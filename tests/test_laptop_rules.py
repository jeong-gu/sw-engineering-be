from services.laptop_rules import (
    is_valid_start_time,
    calculate_end_time,
    can_use_more_hours,
)


def test_is_valid_start_time():
    assert is_valid_start_time(9) is True
    assert is_valid_start_time(16) is True
    assert is_valid_start_time(8) is False
    assert is_valid_start_time(17) is False


def test_calculate_end_time():
    assert calculate_end_time(9) == 11
    assert calculate_end_time(14) == 16


def test_can_use_more_hours():
    assert can_use_more_hours(0) is True
    assert can_use_more_hours(2) is True
    assert can_use_more_hours(4) is False
    assert can_use_more_hours(3) is False
