# analysis.py

import pandas as pd
from database import get_sessions

SESSIONS_COLUMNS=['id', 'focus_scale', 'duration', 'right_answers', 'total_questions', 'date', 'subject_name']
MIN_DAILY_MINUTES = 5
SUMMARY_COLUMNS = ['total_minute', 'total_sessions', 'average_duration_every_sessions', 'average_focus_scale', 'right_answers', 'total_questions', 'accuracy']
WEEKLY_COLUMNS = ['total_minute', 'total_sessions', 'average_focus_scale', 'total_active_days']

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


if __name__ == "__main__":
    df = get_sessions_dataframe()
    