def is_valid_start_time(start_time: int) -> bool:
    """열람실 시작 시간은 09~16시만 가능"""
    return 9 <= start_time <= 16


def calculate_end_time(start_time: int) -> int:
    """열람실은 항상 2시간 이용"""
    return start_time + 2


def can_use_more_hours(used_hours: int, new_hours: int = 2) -> bool:
    """하루 최대 4시간 제한"""
    return used_hours + new_hours <= 4
