# database.py

from datetime import datetime
import sqlite3

def get_connection():
    conn = sqlite3.connect('study.db')
    conn.execute('PRAGMA foreign_keys = ON')

    return conn

def create_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS subjects
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS study_sessions
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        focus_scale INTEGER NOT NULL,
        duration INTEGER NOT NULL,
        right_answers INTEGER,
        total_questions INTEGER,
        date text NOT NULL,
        subject_id INTEGER NOT NULL,
        FOREIGN KEY (subject_id) REFERENCES subjects(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS study_target_weekly
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_id INTEGER NOT NULL,
        week_start_date TEXT NOT NULL,
        target_duration INTEGER NOT NULL,
        UNIQUE(subject_id, week_start_date),
        FOREIGN KEY (subject_id) REFERENCES subjects(id)
    )
    ''')
    
    conn.commit()
    conn.close()

def add_subject(name):
    try:
        name = name.strip().title()
    except AttributeError:
        return False, "Subject name must be a string."
    
    if not name:
        return False, "Subject name cannot be empty."
    
    conn = get_connection()
    cursor = conn.cursor()
    

    try:
        cursor.execute('INSERT INTO subjects (name) VALUES (?)', (name,))
        conn.commit()
    except sqlite3.IntegrityError:
        error_message = f"Subject '{name}' already exists."
        return False, error_message
    finally:
        conn.close()

    return True, f"Subject '{name}' added successfully."

def add_session(focus_scale, duration, date, subject_id, right_answers=None, total_questions=None):
    if focus_scale < 1 or focus_scale > 10:
        return False, "Focus scale must be between 1 and 10."
    if duration <= 0:
        return False, "Duration must be a positive integer."
    
    if right_answers is not None and (right_answers < 0 or (total_questions is not None and right_answers > total_questions)):
        return False, "Right answers must be a non-negative integer and cannot exceed total questions."
    if right_answers is not None and total_questions is None:
        return False, "Total questions must be provided if right answers are specified."
    if total_questions is not None and right_answers is None:
        return False, "Right answers must be provided if total questions are specified."
    if total_questions is not None and total_questions <= 0:
        return False, "Total questions must be a positive integer."

    try:
        date = datetime.strptime(date, '%Y-%m-%d').date().isoformat()
    except ValueError:
        return False, "Date must be in the format YYYY-MM-DD."
    except TypeError:
        return False, "Date must be a string in the format YYYY-MM-DD."
        
    if subject_id is None:
        return False, "Subject ID must be provided."

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO study_sessions (focus_scale, duration, right_answers, total_questions, date, subject_id)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (focus_scale, duration, right_answers, total_questions, date, subject_id))
        conn.commit()
    except sqlite3.IntegrityError as e:
        return False, f"Database error: {e}"
    finally:
        conn.close()

    return True, "Study session added successfully."

def get_subjects():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT id, name FROM subjects ORDER BY name')
    subjects = cursor.fetchall()

    conn.close()
    return subjects

def get_sessions():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
    SELECT study_sessions.id, study_sessions.focus_scale, study_sessions.duration, 
           study_sessions.right_answers, study_sessions.total_questions, 
           study_sessions.date, subjects.name
           FROM study_sessions
           JOIN subjects ON study_sessions.subject_id = subjects.id ORDER BY study_sessions.date DESC, study_sessions.id DESC
           ''')
    sessions = cursor.fetchall()

    conn.close()
    return sessions

def calculate_duration_minutes(start, end):
    if not isinstance(start, datetime) or not isinstance(end, datetime):
        raise TypeError("Start and end must be datetime objects.")
    
    if end < start:
        raise ValueError("End time must be after start time.")
    
    duration = end - start
    return int(duration.total_seconds() // 60)

if __name__ == '__main__':
    create_table()

