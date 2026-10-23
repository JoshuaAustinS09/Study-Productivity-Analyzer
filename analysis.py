# analysis.py

import pandas as pd
from database import get_sessions

SESSIONS_COLUMNS=['id', 'focus_scale', 'duration', 'right_answers', 'total_questions', 'date', 'subject_name']
MIN_DAILY_MINUTES = 5
SUMMARY_COLUMNS = ['total_minute', 'total_sessions', 'average_duration_every_sessions', 'average_focus_scale', 'right_answers', 'total_questions', 'accuracy']
WEEKLY_COLUMNS = ['total_minute', 'total_sessions', 'average_focus_scale', 'total_active_days']
WEEKLY_CHANGE_COLUMNS = ["minute_change", "minute_change_pct", "session_change", "active_days_change"]

def get_sessions_dataframe():
    sessions = get_sessions()
    df = pd.DataFrame(sessions, columns=SESSIONS_COLUMNS)
    return df

def total_study_hours(df):
    return round(df['duration'].sum() / 60, 2)

def average_session_duration(df):
    if df.empty:
        return 0
    return df['duration'].mean()

def get_active_dates(df):
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])

    daily = df.groupby("date")['duration'].sum()
    active_days = daily[daily >= MIN_DAILY_MINUTES]

    return active_days.index.date.tolist()

def calculate_longest_streak(dates): # dates harus terurut naik dan tanpa duplikat
    if not dates:
        streak = 0
        longest_streak = 0
        return longest_streak
    
    streak = 1
    longest_streak = 1

    for i in range(1, len(dates)):
        if (dates[i] - dates[i - 1]).days == 1:
            streak += 1
            if streak > longest_streak:
                longest_streak = streak
        else:
            streak = 1

    return longest_streak

def calculate_current_streak(dates, today): # dates harus terurut naik dan tanpa duplikat
    if not dates:
        return 0
    
    if (today - dates[-1]).days > 1:
        return 0
    
    streak = 1
    for i in range(len(dates) - 1, 0, -1):
        if (dates[i] - dates[i - 1]).days == 1:
            streak += 1
        else:
            break

    return streak

def subject_summary(df):
    if df.empty:
        return pd.DataFrame([], columns=SUMMARY_COLUMNS)

    summary = df.groupby("subject_name").agg(
        total_minute = ("duration", "sum"),
        total_sessions = ("id", "count"), 
        average_duration_every_sessions = ("duration", "mean"),
        average_focus_scale = ("focus_scale", "mean"),
        right_answers = ("right_answers", "sum"),
        total_questions = ("total_questions", "sum"),
    )
    summary['accuracy'] = round((summary['right_answers']/summary['total_questions']) * 100, 1)
    summary = summary.sort_values('total_minute', ascending=False)

    return summary

def weekly_summary(df):
    if df.empty:
        return pd.DataFrame([], columns=WEEKLY_COLUMNS)

    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    
    df['week_start_date'] = df['date'].dt.to_period("W").dt.start_time

    daily = df.groupby("date")['duration'].sum()
    active_days = daily[daily >= MIN_DAILY_MINUTES]
    active_days = active_days.reset_index()
    active_days["week_start"] = active_days["date"].dt.to_period("W").dt.start_time
    active_per_week = active_days.groupby("week_start")["date"].count()
    
    summary = df.groupby(['week_start_date']).agg(
        total_minute = ("duration", "sum"),
        total_sessions = ("id", "count"),
        average_focus_scale = ("focus_scale", "mean"),
    )

    summary["total_active_days"] = active_per_week
    summary["total_active_days"] = summary["total_active_days"].fillna(0).astype(int)

    summary = summary.sort_values('week_start_date', ascending=True)
    return summary

def add_weekly_changes(weekly):
    if weekly.empty:
        return pd.DataFrame([], columns=WEEKLY_CHANGE_COLUMNS)


    weekly = weekly.copy()
    changes = weekly_summary(weekly)

    changes["minute_change"] = changes["total_minute"].diff()
    changes["minute_change_pct"] = round(changes["total_minute"].pct_change() * 100, 1)
    changes["session_change"] = changes["total_sessions"].diff()
    changes["active_days_change"] = changes["total_active_days"].diff()

    only_changes = changes[['minute_change', 'minute_change_pct', 'session_change', 'active_days_change']]

    return only_changes


if __name__ == "__main__":
    df = get_sessions_dataframe()
    sample_df = pd.DataFrame(
    [
        (1, 8, 60, 15, 20, "2026-10-01", "Fisika"),
        (2, 6, 40, 9, 10, "2026-10-02", "Fisika"),
        (3, 7, 30, None, None, "2026-10-03", "Fisika"),
        (4, 5, 45, None, None, "2026-10-01", "Sejarah"),
        (5, 9, 25, None, None, "2026-10-04", "Sejarah"),
        (6, 8, 3, None, None, "2026-10-13", "Fisika"),
        (6, 8, 3, None, None, "2026-10-14", "Fisika"),
        (6, 8, 3, None, None, "2026-10-14", "Fisika"),
    ],
        columns=SESSIONS_COLUMNS,
    )
    
    empty_df = pd.DataFrame([], columns=SESSIONS_COLUMNS)

    print(add_weekly_changes(df))
    print(add_weekly_changes(sample_df))
    print(add_weekly_changes(empty_df))
    
