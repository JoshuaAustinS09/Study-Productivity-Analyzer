import pytest
from analysis import calculate_longest_streak, calculate_current_streak
from datetime import date

@pytest.mark.parametrize("dates, expected", [
    ([], 0),
    ([date(2026, 10, 1)], 1),
    ([date(2026, 10, 1), date(2026, 10, 2), date(2026, 10, 3), date(2026, 10, 4)], 4),
    ([date(2026, 10, 1), date(2026, 10, 3), date(2026, 10, 5)], 1),
    ([date(2026, 10, 1), date(2026, 10, 2), date(2026, 10, 3), date(2026, 10, 4), date(2026, 10, 7), date(2026, 10, 9)], 4),
    ([date(2026, 10, 1), date(2026, 10, 3), date(2026, 10, 5), date(2026, 10, 6), date(2026, 10, 7), date(2026, 10, 8)], 4)
])

def test_longest_streak(dates, expected):
    assert calculate_longest_streak(dates) == expected

@pytest.mark.parametrize("dates, today, expected", [
    ([date(2026, 10, 8), date(2026, 10, 9), date(2026, 10, 10)], date(2026, 10, 10), 3),
    ([date(2026, 10, 8), date(2026, 10, 9), date(2026, 10, 10)], date(2026, 10, 11), 3),
    ([date(2026, 10, 8), date(2026, 10, 9), date(2026, 10, 10)], date(2026, 10, 12), 0),
    ([], date(2026, 10, 12), 0),
    ([date(2026, 10, 7), date(2026, 10, 8), date(2026, 10, 9), date(2026, 10, 10), date(2026, 10, 12), date(2026, 10, 13), date(2026, 10, 14)], date(2026, 10, 15), 3),
])

def test_current_streak(dates, today, expected):
    assert calculate_current_streak(dates, today) == expected