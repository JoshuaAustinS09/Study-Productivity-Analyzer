from unittest import result

import pytest
import pandas as pd
from analysis import calculate_longest_streak, calculate_current_streak, goal_progress, SESSIONS_COLUMNS, TARGET_COLUMNS, PROGRESS_COLUMNS
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

@pytest.fixture(scope="module")
def goal_progress_result():
    sessions = pd.DataFrame(
        [
            (1, 7, 40, None, None, "2026-10-13", "Fisika"),
            (2, 7, 80, None, None, "2026-10-14", "Fisika"),
            (3, 7, 30, None, None, "2026-10-13", "Sejarah"),
        ],
        columns=SESSIONS_COLUMNS
    )
    targets = pd.DataFrame(
        [
            (1, "2026-10-12", 100, "Fisika"),
            (2, "2026-10-12", 60, "Kimia"),
        ],
        columns=TARGET_COLUMNS
    )
    return goal_progress(sessions, targets)

def test_goal_progress_fisika(goal_progress_result):
    result = goal_progress_result

    fisika = result[result["subject_name"] == "Fisika"].iloc[0]
    assert fisika["target_duration"] == 100
    assert fisika["achieved_duration"] == 120
    assert fisika["percentage"] == 120.0
    assert fisika["percentage_capped"] == 100.0

def test_goal_progress_kimia(goal_progress_result):
    result = goal_progress_result
    
    kimia = result[result["subject_name"] == "Kimia"].iloc[0]
    assert kimia["target_duration"] == 60
    assert kimia["achieved_duration"] == 0
    assert kimia["percentage"] == 0.0
    assert kimia["percentage_capped"] == 0.0

def test_goal_progress_sejarah(goal_progress_result):
    result = goal_progress_result
    
    sejarah = result[result["subject_name"] == "Sejarah"].iloc[0]
    assert pd.isna(sejarah["target_duration"])
    assert sejarah["achieved_duration"] == 30
    assert pd.isna(sejarah["percentage"])
    assert pd.isna(sejarah["percentage_capped"])

def test_goal_progress_empty():
    sessions = pd.DataFrame([], columns=SESSIONS_COLUMNS)
    targets = pd.DataFrame([], columns=TARGET_COLUMNS)
        
    result = goal_progress(sessions, targets)
    
    assert list(result.columns) == PROGRESS_COLUMNS
    assert len(result) == 0

def test_goal_progress_sessions_none():
    sessions = pd.DataFrame([], columns=SESSIONS_COLUMNS)

    targets = pd.DataFrame(
            [
                (1, "2026-10-12", 100, "Fisika"),
                (2, "2026-10-12", 60, "Kimia"),
            ],
            columns=TARGET_COLUMNS
        )
    result = goal_progress(sessions, targets)

    fisika = result[result["subject_name"] == "Fisika"].iloc[0]
    kimia = result[result["subject_name"] == "Kimia"].iloc[0]

    assert fisika["target_duration"] == 100
    assert fisika["achieved_duration"] == 0
    assert kimia["target_duration"] == 60
    assert kimia["achieved_duration"] == 0

def test_goal_progress_targets_none(goal_progress_result):
    sessions = pd.DataFrame(
            [
                (1, 7, 40, None, None, "2026-10-13", "Fisika"),
                (2, 7, 80, None, None, "2026-10-14", "Fisika"),
                (3, 7, 30, None, None, "2026-10-13", "Sejarah"),
            ],
            columns=SESSIONS_COLUMNS
        )
    
    targets = pd.DataFrame([], columns=TARGET_COLUMNS)

    result = goal_progress(sessions, targets)

    fisika = result[result["subject_name"] == "Fisika"].iloc[0]
    sejarah = result[result["subject_name"] == "Sejarah"].iloc[0]

    assert fisika["achieved_duration"] == 120
    assert sejarah["achieved_duration"] == 30
    assert pd.isna(fisika["target_duration"])
    assert pd.isna(sejarah["target_duration"])