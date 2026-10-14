from database import add_subject, add_session, create_table, get_subjects


SUBJECTS = [
    "Mtk",
    "Fisika",
    "Kimia",
    "Biologi",
    "Mtk Advanced",
    "Coding",
]

SEED_SESSIONS = [
    ("Mtk", "2026-09-21", 8, 70, 18, 20),
    ("Mtk", "2026-09-30", 4, 45, None, None),
    ("Mtk", "2026-10-06", 6, 52, 13, 15),

    ("Fisika", "2026-09-23", 3, 35, None, None),
    ("Fisika", "2026-10-01", 8, 65, 16, 18),
    ("Fisika", "2026-10-07", 7, 58, 12, 15),

    ("Kimia", "2026-09-25", 6, 50, 12, 15),
    ("Kimia", "2026-10-02", 5, 40, None, None),
    ("Kimia", "2026-10-08", 8, 70, 17, 20),

    ("Biologi", "2026-09-27", 2, 30, None, None),
    ("Biologi", "2026-10-03", 7, 55, 14, 16),
    ("Biologi", "2026-10-09", 4, 42, None, None),

    ("Mtk Advanced", "2026-09-28", 9, 80, 20, 22),
    ("Mtk Advanced", "2026-10-04", 9, 90, 23, 25),
    ("Mtk Advanced", "2026-10-10", 8, 85, 19, 22),

    ("Coding", "2026-09-29", 7, 60, 15, 20),
    ("Coding", "2026-10-05", 3, 25, None, None),
    ("Coding", "2026-10-11", 9, 75, 18, 20),
]


def seed_data():
    create_table()

    existing_subjects = {}
    for subject_id, subject_name in get_subjects():
        existing_subjects[subject_name] = subject_id

    for subject_name in SUBJECTS:
        if subject_name not in existing_subjects:
            ok, message = add_subject(subject_name)
            print(message)
            if ok:
                existing_subjects[subject_name] = get_subjects()[-1][0]

    all_subjects = get_subjects()
    subject_map = {name: subject_id for subject_id, name in all_subjects}

    for subject_name, date, focus_scale, duration, right_answers, total_questions in SEED_SESSIONS:
        subject_id = subject_map.get(subject_name)
        if subject_id is None:
            continue

        ok, message = add_session(
            focus_scale=focus_scale,
            duration=duration,
            date=date,
            subject_id=subject_id,
            right_answers=right_answers,
            total_questions=total_questions,
        )
        print(f"{subject_name} {date}: {message}")


if __name__ == "__main__":
    print("Seeding test data...")
    seed_data()
    print("Seeding complete.")