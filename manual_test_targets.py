# manual_test_targets.py

import os
from datetime import date

import database

TEST_DB = "test_study.db"
database.DB_NAME = TEST_DB          # semua koneksi sekarang menuju file uji
if os.path.exists(TEST_DB):
    os.remove(TEST_DB)              # mulai dari database kosong setiap kali dijalankan

# Kalau nama function-mu berubah, cukup ubah dua baris ini
set_target = database.set_weekly_targets
get_targets = database.get_weekly_targets

MONDAY = "2026-10-12"
NEXT_MONDAY = "2026-10-19"
THURSDAY = "2026-10-15"


def query(sql, params=()):
    """Baca database langsung, tanpa lewat function-mu."""
    conn = database.get_connection()
    try:
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()


def report(name, passed, detail=""):
    print(f"[{'PASS' if passed else 'FAIL'}] {name} {detail}")


def call(name, func, *args, expected_ok=None):
    """Jalankan function, bandingkan True/False dengan harapan, dan tangkap crash."""
    try:
        ok, message = func(*args)
    except Exception as e:
        report(name, False, f"-> CRASH: {type(e).__name__}: {e}")
        return None
    passed = True if expected_ok is None else ok == expected_ok
    report(name, passed, f"-> {ok}, {message}")
    return ok, message


database.create_table()
database.add_subject("Fisika")      # id 1
database.add_subject("Kimia")       # id 2

SELECT_TARGET = (
    "SELECT target_duration FROM study_target_weekly "
    "WHERE subject_id = ? AND week_start_date = ?"
)

print("--- set_weekly_targets ---")

# 1. Target normal, dan benar-benar tersimpan
call("1. target normal", set_target, 1, MONDAY, 120, expected_ok=True)
rows = query(SELECT_TARGET, (1, MONDAY))
report("1b. tersimpan di database", len(rows) == 1 and rows[0][0] == 120, f"-> {rows}")

# 2. Target kedua di mapel dan minggu yang sama: ditimpa (bukan dobel)
call("2. target kedua (menimpa)", set_target, 1, MONDAY, 180, expected_ok=True)
rows = query(SELECT_TARGET, (1, MONDAY))
report("2b. satu baris, nilai 180", len(rows) == 1 and rows[0][0] == 180, f"-> {rows}")

# 3. Tanggal Kamis: boleh ditolak ATAU disesuaikan ke Senin, tapi tidak boleh disimpan apa adanya
call("3. tanggal Kamis", set_target, 2, THURSDAY, 90)
stored = query("SELECT week_start_date FROM study_target_weekly WHERE subject_id = 2")
all_monday = all(date.fromisoformat(r[0]).weekday() == 0 for r in stored)
report("3b. tidak ada tanggal non-Senin tersimpan", all_monday, f"-> tersimpan: {stored}")

# 4. Target nol dan negatif ditolak, dan tidak ada yang tersimpan
call("4a. target 0", set_target, 1, NEXT_MONDAY, 0, expected_ok=False)
call("4b. target negatif", set_target, 1, NEXT_MONDAY, -30, expected_ok=False)
stored = query("SELECT * FROM study_target_weekly WHERE week_start_date = ?", (NEXT_MONDAY,))
report("4c. tidak ada yang tersimpan", len(stored) == 0, f"-> {stored}")

# 5. Mapel tidak ada: ditolak dengan pesan, bukan crash
call("5. mapel tidak ada", set_target, 999, MONDAY, 60, expected_ok=False)

# 6. Format tanggal salah
call("6. tanggal 'besok'", set_target, 1, "besok", 60, expected_ok=False)

print("--- get_weekly_targets ---")

try:
    targets = get_targets()
except Exception as e:
    report("7. get_weekly_targets", False, f"-> CRASH: {type(e).__name__}: {e}")
else:
    total_rows = query("SELECT COUNT(*) FROM study_target_weekly")[0][0]
    report("7a. jumlah baris sama dengan isi tabel", len(targets) == total_rows,
           f"-> function: {len(targets)}, tabel: {total_rows}")
    report("7b. nama mapel muncul (bukan angka)", any("Fisika" in row for row in targets))
    for row in targets:
        print("    ", row)