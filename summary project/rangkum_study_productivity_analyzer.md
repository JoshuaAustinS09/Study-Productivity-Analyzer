# Rangkuman Proyek: Study Productivity Analyzer

> Terakhir diperbarui: 29 Oktober 2026 (chat berjalan 11 Okt - 29 Okt 2026)
> Cara lanjut: tempel file ini di chat baru, lalu lanjut dari bagian "9. To-do berikutnya" (mulai dari `goal_progress` di `analysis.py`). Gaya mengajar yang dipakai ada di bagian 8.

## 1. Ringkasan proyek

- **Nama:** Study Productivity Analyzer.
- **Fungsi:** mencatat sesi belajar, lalu mengubahnya jadi statistik, grafik, dan insight tentang kebiasaan belajar.
- **Pengguna:** user sendiri (Josh, pelajar), nanti mungkin orang lain yang ingin melacak belajarnya.
- **Masalah yang diselesaikan:** "Aku merasa sudah rajin belajar, tapi apakah datanya mendukung?" Contoh pertanyaan: apakah Fisika terlalu sedikit dibanding Matematika, apakah durasi belajar lebih lama benar-benar menaikkan nilai latihan.
- **Output akhir yang direncanakan:** database riwayat belajar, dashboard statistik, grafik per mapel dan per minggu, pelacak target mingguan.
- **Tingkat kesulitan:** Intermediate. Project sebelumnya, Personal Finance Tracker, sudah selesai.
- **Skill yang dilatih:** Python (functions, modules, OOP hanya jika perlu, `datetime`), SQLite (desain tabel, SQL dasar), Pandas, NumPy, descriptive statistics (mean, median, std, korelasi), Matplotlib (membaca dan menjelaskan grafik), error handling, input validation, pytest, struktur project, Git.
- **Project lanjutan (belum jadi fokus):** Student Performance Predictor. Baru dipikirkan setelah Study Productivity Analyzer selesai. Desain data diharapkan bisa dipakai ulang di sana.
- **Prinsip arsitektur yang disepakati:** bangun "otak" (data dan analisis) sebagai kode yang terpisah dari tampilan. Keputusan UI ditunda sampai akhir.

## 2. Tech stack & environment

| Teknologi | Fungsi di project | Status pemakaian |
|---|---|---|
| Python 3.10+ | Bahasa utama | versi pasti di komputer user `[belum jelas]` |
| `sqlite3` | Menyimpan sesi belajar, mapel, target | ✅ dipakai |
| `datetime` | Tanggal, minggu, streak, durasi | ✅ dipakai |
| Pandas | Mengolah data dari DB (groupby, merge, per minggu) | ✅ dipakai (user baru pertama kali memakai Pandas di project ini) |
| NumPy | Perhitungan statistik | ⏳ terpasang di rencana, belum dipakai |
| Matplotlib | Grafik | ✅ dipakai |
| pytest | Menguji fungsi | ⏳ Phase 6 |
| Git | Riwayat perubahan | ⏳ disebut di rencana, belum dikonfirmasi di chat apakah repo sudah dibuat `[belum jelas]` |

- **Instalasi library:** `pip install pandas numpy matplotlib` di dalam virtual environment (`venv`). pytest belum diinstal.
- **Lingkungan user:** Windows, project di folder `Study Productivity Analyzer` dalam `E:\Coding\Project\`, virtual environment di dalam folder project, editor VS Code yang punya AI agent (agent dipakai untuk membuat data uji awal).
- **Struktur file saat ini (satu folder, belum ada subfolder):**
  - `database.py`: semua urusan SQLite (koneksi, tabel, tulis, baca).
  - `analysis.py`: semua perhitungan Pandas (statistik, streak, ringkasan mapel, ringkasan mingguan, perubahan mingguan).
  - `charts.py`: semua pembuatan grafik Matplotlib.
  - `manual_test_targets.py`: skrip uji manual untuk fungsi target mingguan (dibuat bersama Claude).
  - `seed_data.py`: skrip pengisi data uji (dibuat oleh AI agent di VS Code atas instruksi dari chat ini).
  - `latihan.py`: file latihan Pandas dasar (contoh buku, terpisah dari kode project).
  - `study.db`: database utama. `test_study.db`: database khusus pengujian target.
  - Gambar hasil: `weekly_minutes.png`, `weekly_minutes_sample.png`, `weekly_minutes_empty.png`, `weekly_summary.png`.
- **Cara menjalankan:** `python database.py` membuat tabel. `python analysis.py` dan `python charts.py` menjalankan blok `if __name__ == "__main__"` masing-masing (isinya kode uji/cek, bukan aplikasi utama). Belum ada program utama atau menu CLI.

## 3. Database

### 3.1 Konfigurasi

- File database: `study.db`, di folder yang sama dengan kode. Nama file disimpan di konstanta `DB_NAME` di `database.py`.
- `get_connection()` membuka koneksi ke `DB_NAME`, menjalankan `PRAGMA foreign_keys = ON`, dan **mengembalikan `conn` tanpa menutupnya**. Pemakai function wajib menutup koneksi.
- `PRAGMA foreign_keys = ON` harus dijalankan **di setiap koneksi baru** karena SQLite tidak menegakkan foreign key secara default. Karena itu semua function memakai `get_connection()`, bukan `sqlite3.connect` langsung.
- Untuk pengujian, `DB_NAME` bisa ditimpa dari luar (`database.DB_NAME = "test_study.db"`) sebelum function apa pun dipanggil, supaya `study.db` tidak tersentuh. Ini dipakai di `manual_test_targets.py`.
- Semua tabel dibuat dengan `CREATE TABLE IF NOT EXISTS`. **Catatan penting:** perintah ini tidak memperbarui struktur tabel yang sudah ada. Kalau struktur berubah, file `.db` lama harus dihapus dulu.
- Urutan pembuatan tabel: `subjects` dulu, baru tabel yang menunjuk ke sana (konvensi yang benar walau SQLite tidak mewajibkan).

### 3.2 Skema

**Tabel `subjects`**

| Kolom | Tipe | Constraint | Keterangan |
|---|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | nomor unik mapel |
| name | TEXT | NOT NULL UNIQUE | nama mapel (disimpan dalam format `.strip().title()`) |

**Tabel `study_sessions`**

| Kolom | Tipe | Constraint | Keterangan |
|---|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | nomor unik sesi |
| focus_scale | INTEGER | NOT NULL | skor fokus, skala 1-10 |
| duration | INTEGER | NOT NULL | durasi belajar dalam **menit** |
| right_answers | INTEGER | boleh NULL | jumlah soal benar |
| total_questions | INTEGER | boleh NULL | jumlah soal. NULL bersama `right_answers` jika sesi tanpa soal |
| date | TEXT | NOT NULL | format `YYYY-MM-DD` |
| subject_id | INTEGER | NOT NULL, FOREIGN KEY → `subjects(id)` | mapel yang dipelajari |

**Tabel `study_target_weekly`**

| Kolom | Tipe | Constraint | Keterangan |
|---|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | nomor unik target |
| subject_id | INTEGER | NOT NULL, FOREIGN KEY → `subjects(id)` | target untuk mapel mana (target per mapel, bukan total) |
| week_start_date | TEXT | NOT NULL | tanggal **Senin** awal minggu, format `YYYY-MM-DD` |
| target_duration | INTEGER | NOT NULL | target belajar dalam **menit** |
| (aturan tabel) | | UNIQUE(subject_id, week_start_date) | satu mapel hanya boleh punya satu target per minggu |

- **Relasi:** `study_sessions.subject_id` → `subjects.id` dan `study_target_weekly.subject_id` → `subjects.id`.
- **Index:** tidak ada yang dibuat manual (selain index otomatis dari PRIMARY KEY dan UNIQUE).
- **Aturan desain data:** nilai kosong (NULL) artinya "tidak ada data", bukan 0. Nilai nilai latihan **tidak disimpan** sebagai kolom, karena bisa dihitung dari `right_answers / total_questions`.
- **Catatan nomor id:** `id` itu penanda unik, bukan nomor urut. Di hasil uji target, Kimia mendapat id 3 padahal hanya ada dua target, kemungkinan karena upsert memakai nomor id saat mencoba INSERT lalu beralih ke UPDATE. Kode tidak boleh mengandalkan id berurutan.

### 3.3 Data yang diberikan user

- **Gambaran project dan UI:** user mengirim deskripsi project (bagian 1) dan gambar desain dashboard gelap bernama "SelfStudy". Isi desain: sidebar (Profile, Dashboard, Schedule, Courses, Achievements, Settings, Help, Log out), kartu Learning Days (Days in a Roll, Days This Month, Total Days dengan persentase perubahan), grafik batang bertumpuk Productivity per hari, grafik area Progress per minggu, daftar Task hari ini dengan checklist, donut Skills, dan Current Courses berupa cincin progres (mis. 3/15). Ada pemilih mode terang/gelap. Pemetaan ke fitur ada di bagian 5.
- **Data uji awal (dibuat oleh AI agent VS Code, disimpan di `study.db`):** 18 sesi belajar, tanggal 21 September sampai 11 Oktober 2026, 6 mapel (Coding, Mtk Advanced, Biologi, Kimia, Fisika, Mtk), masing-masing 3 sesi. Beberapa sesi tanpa soal (NULL). Ada 3 hari bolong: 22, 24, dan 26 September.
  - Angka acuan: total 1027 menit (17,12 jam), rata-rata durasi sesi 57,06 menit, 18 hari aktif, longest streak 15 hari (27 Sep - 11 Okt), sesi terakhir 11 Oktober.
  - Per mapel: Mtk Advanced 255 menit / 62 benar dari 69 soal (89,9%); Mtk 167 menit / 31 dari 35 (88,6%); Kimia 160 menit / 29 dari 35 (82,9%); Coding 160 menit / 33 dari 40 (82,5%); Fisika 158 menit / 28 dari 33 (84,8%); Biologi 127 menit / 14 dari 16 (87,5%).
  - Per minggu (awal Senin): 21 Sep = 185 menit, 4 sesi, fokus 4,75, 4 hari aktif; 28 Sep = 435 menit, 7 sesi, fokus 7,0, 7 hari aktif; 5 Okt = 407 menit, 7 sesi, fokus 6,43, 7 hari aktif.
  - Menit Fisika per minggu: 35 (21 Sep), 65 (28 Sep), 58 (5 Okt). Coding minggu 5 Okt: 100 menit.
  - Catatan: data ini **buatan agent untuk uji coba**, bukan kebiasaan belajar user yang sesungguhnya. Pola di dalamnya tidak boleh dianggap bermakna.
  - Ada "Mtk" dan "Mtk Advanced" yang dihitung sebagai dua mapel berbeda. User membiarkannya (keputusan desain, bukan bug).
- **Data mini buatan sendiri untuk pengujian** (ditulis di blok `__main__` analysis.py dan charts.py): `sample_df` berisi sesi Fisika dan Sejarah tanggal 1-4 Oktober (total 200 menit, 5 sesi, 4 hari aktif di minggu 28 Sep), ditambah beberapa sesi 3 menit (variasi: minggu semua hari di bawah 5 menit, dua sesi kembar di satu hari, minggu yang hilang di tengah). Versinya di analysis.py dan charts.py **tidak identik**, karena dipakai untuk uji yang berbeda. `empty_df` adalah DataFrame kosong dengan kolom `SESSIONS_COLUMNS`.
- **Database uji target:** `test_study.db`, dibuat ulang tiap skrip `manual_test_targets.py` dijalankan, berisi mapel Fisika (id 1) dan Kimia (id 2).

## 4. Roadmap & langkah pembuatan

| Phase | Isi | Status |
|---|---|---|
| 0 | Persiapan: environment dan desain data | ✅ selesai |
| 1 | Database dan Logger (tabel, simpan/baca sesi, input divalidasi) | ✅ selesai (level function; belum ada input interaktif/CLI) |
| 2 | Statistics (total jam, rata-rata durasi, konsistensi: streak, hari aktif) | ✅ selesai |
| 3 | Subject Analysis (perbandingan antar mapel, Pandas groupby) | ✅ selesai |
| 4 | Trend Analysis (perubahan mingguan + grafik Matplotlib) | ✅ selesai |
| 5 | Goal Tracker (target mingguan dan persentase pencapaian) | 🚧 bagian database ✅; bagian analisis (`goal_progress`) ⏳ belum ditulis |
| 6 | Testing (pytest untuk fungsi hitungan) | ⏳ |
| 7 | UI dan polish (README, dashboard) | ⏳ |

**Pendekatan tiap fase (ringkas):**

- **Phase 0:** desain tiga tabel di atas kertas dulu (kolom, tipe, boleh kosong atau tidak) sebelum menulis kode.
- **Phase 1:** buat tabel dengan `CREATE TABLE IF NOT EXISTS`; tiap function tulis memakai placeholder `?` (anti SQL injection), validasi dulu **sebelum** membuka koneksi, `try/except/finally` untuk menutup koneksi, dan mengembalikan `(True/False, pesan)`.
- **Phase 2:** ubah hasil `get_sessions()` jadi DataFrame bernama kolom; hitung statistik dengan `.sum()`, `.mean()`; konsistensi diukur sebagai streak (current dan longest) dari daftar "tanggal aktif".
- **Phase 3:** `groupby("subject_name").agg(...)` untuk beberapa hasil sekaligus; akurasi dihitung **di luar** `.agg()` dari total benar dibagi total soal.
- **Phase 4:** kelompokkan per minggu dengan `to_period("W").dt.start_time` (Senin); hari aktif dihitung dua tahap (total menit per hari, saring ≥ ambang, hitung per minggu, tempel ke tabel mingguan lewat penyelarasan index); perubahan dengan `.diff()` dan `.pct_change()`; grafik lewat function yang menerima tabel mingguan dan mengembalikan `fig`.
- **Phase 5:** tulis target dengan upsert (`INSERT ... ON CONFLICT ... DO UPDATE`); lalu gabungkan target dengan menit nyata memakai `merge`.

## 5. Fitur

### ✅ Sudah jadi

**Study Session Logger (`database.py`)**
- `create_table()`: membuat tiga tabel.
- `add_subject(name)`: validasi (harus string, tidak kosong setelah strip), simpan dalam format `.strip().title()`, tangani nama dobel. Mengembalikan `(True/False, pesan)`.
- `add_session(focus_scale, duration, session_date, subject_id, right_answers=None, total_questions=None)`: validasi fokus 1-10, durasi > 0, pasangan benar/soal (keduanya diisi bersama atau kosong bersama, benar tidak boleh melebihi soal, soal > 0), tanggal `YYYY-MM-DD` (disimpan sebagai teks `.date().isoformat()`), subject_id wajib; menangkap `IntegrityError` (mis. mapel tidak ada). Mengembalikan `(True/False, pesan)`.
- `get_subjects()`: daftar `(id, name)` diurutkan menurut nama.
- `get_sessions()`: semua sesi dengan **nama mapel** (JOIN), urut tanggal terbaru lalu id terbaru. Kolom hasil berurutan: id, focus_scale, duration, right_answers, total_questions, date, nama mapel.
- `calculate_duration_minutes(start, end)`: function murni; menerima dua `datetime`, mengembalikan menit bulat (`// 60`); `raise TypeError` jika bukan datetime, `raise ValueError` jika end sebelum start. (Memakai `raise`, bukan tuple, karena ini function internal, bukan input pengguna.)

**Statistics Dashboard (`analysis.py`)**
- `get_sessions_dataframe()`: membungkus `get_sessions()` jadi DataFrame dengan kolom `SESSIONS_COLUMNS`.
- `total_study_hours(df)`: total menit dibagi 60, dibulatkan 2 desimal (dipilih daripada `// 60` karena pembagian bulat memotong sisa).
- `average_session_duration(df)`: rata-rata durasi; DataFrame kosong mengembalikan 0.
- `get_active_dates(df)`: daftar tanggal (objek `date`, terurut naik, tanpa duplikat) dengan total menit per hari ≥ `MIN_DAILY_MINUTES` (5). Bekerja pada salinan `df`.
- `calculate_longest_streak(dates)`: rekor hari berturut-turut; daftar kosong = 0; mengasumsikan `dates` terurut naik tanpa duplikat (ditulis di komentar).
- `calculate_current_streak(dates, today)`: streak yang sedang berjalan; `today` jadi parameter agar bisa diuji. Mengembalikan 0 jika sesi terakhir lebih dari 1 hari sebelum `today`.

**Subject Analysis**
- `subject_summary(df)`: satu baris per mapel, kolom `SUMMARY_COLUMNS` (total_minute, total_sessions, average_duration_every_sessions, average_focus_scale, right_answers, total_questions, accuracy), diurutkan dari total menit terbanyak. Mapel tanpa soal menghasilkan `NaN` pada accuracy. DataFrame kosong mengembalikan tabel kosong dengan kolom ringkasan.

**Trend Analysis**
- `weekly_summary(df)`: satu baris per minggu (index `week_start_date`, hari Senin), kolom `WEEKLY_COLUMNS` (total_minute, total_sessions, average_focus_scale, total_active_days). `total_active_days` memakai aturan hari aktif ≥ 5 menit, minggu tanpa hari aktif = 0 (int).
- `weekly_changes(df)` (sebelumnya bernama `add_weekly_changes`): perubahan dibanding minggu sebelumnya, kolom `WEEKLY_CHANGE_COLUMNS` (minute_change, minute_change_pct, session_change, active_days_change). Baris pertama `NaN`. Menerima sesi mentah (memanggil `weekly_summary` di dalamnya). Hanya mengembalikan kolom perubahan, kolom asli dibuang. Celah minggu dihitung apa adanya (dibanding minggu aktif sebelumnya), dicatat di komentar kode. Versi final kode ini tidak ditempel di chat `[belum jelas isinya persis]`; user hanya melaporkan perbandingan kolom data kosong vs berisi bernilai `True` dan komentar celah sudah ditulis.
- `charts.py`: `plot_minute_per_week(weekly)` (garis menit per minggu, label sumbu x di tiap Senin, sumbu y mulai dari 0, satuan menit), `plot_weekly_overview(weekly)` (dua panel: batang menit belajar di atas, garis hari aktif di bawah, batas atas sumbu hari aktif 8, `sharex=True`, `constrained_layout=True`), `_empty_figure()` (tulisan "Belum Ada Data" untuk tabel kosong). Semua mengembalikan `fig` dan tidak memanggil `plt.show()` di dalamnya.

**Goal Tracker bagian database (`database.py`)**
- `set_weekly_targets(subject_id, week_start_date, target_duration)`: validasi (subject_id wajib, target harus int lalu harus > 0, tanggal valid), **tanggal otomatis disesuaikan ke Senin minggu itu** (`weekday()` dan `timedelta`), upsert (target lama ditimpa), tangani `IntegrityError` (mis. mapel tidak ada). Pesan sukses: "Target weekly changed successfully and started in Monday".
- `get_weekly_targets()`: semua target dengan nama mapel (JOIN), kolom hasil berurutan: id, week_start_date, target_duration, nama mapel; urut id terbaru.
- Lolos semua uji di `manual_test_targets.py` (lihat bagian 6).

### 🚧 Masih dikembangkan

- **Goal Tracker bagian analisis:** `get_targets_dataframe()` dan `goal_progress(sessions_df, targets_df)` di `analysis.py` belum ditulis. Tiga keputusan sudah diambil user (bagian 7, "Keputusan desain yang berlaku"). Konstanta `TARGET_COLUMNS` dan `PROGRESS_COLUMNS` direncanakan.

### ⏳ Belum dimulai / ide

- Pengujian pytest (Phase 6).
- Menu/CLI input interaktif (belum dibuat; rencana awal membangun "otak" sebagai CLI dulu).
- UI (Phase 7). Pemetaan desain ke fitur:

| Bagian UI "SelfStudy" | Fitur kita |
|---|---|
| Learning Days (streak, hari bulan ini, total hari) | Statistics Dashboard (konsistensi) |
| Productivity (batang bertumpuk per hari) | Subject Analysis |
| Progress (area chart per minggu) | Trend Analysis |
| Task hari ini | Study Session Logger |
| Skills / Current Courses (donut, progres) | Goal Tracker |

  Pilihan teknologi UI belum diputuskan: Streamlit (paling cepat) atau CustomTkinter (aplikasi desktop). Pop-up error juga diinginkan user; cara membuatnya tergantung pilihan UI (Tkinter punya `messagebox`, Streamlit punya `st.error`/`st.success`).
- **Ide tombol Start/Stop timer** (dari user): pilih mapel, tekan Start, tekan Stop, lalu isi fokus dan benar/total, lalu simpan. Durasi dari selisih `datetime.now()` (memakai `calculate_duration_minutes`). Tanggal juga otomatis dari waktu mulai (`start.date().isoformat()`). `add_session` tidak berubah, timer hanya cara lain mengisi `duration` dan `session_date`. Input manual dipertahankan untuk sesi yang lupa dicatat. Hal yang belum diputuskan: sesi yang melewati tengah malam (usulan: pakai tanggal waktu mulai), sesi di bawah 1 menit (akan ditolak `add_session`), dan jam mulai belum disimpan di tabel (perlu tambah kolom, berarti database lama harus dibuat ulang).
- Fungsi `fill_missing_weeks` untuk mengisi minggu kosong (ditawarkan, **tidak** dipilih user).
- Student Performance Predictor (proyek lanjutan, setelah ini selesai).

## 6. Yang sudah dikerjakan (riwayat)

**11 Okt: kickoff dan desain data**
- User memberi gambaran project, daftar skill, tech stack, roadmap Phase 0-7, dan gambar desain UI. Disepakati: bangun logika dulu, UI belakangan.
- Aturan desain yang diputuskan user: fokus skala 1-10; durasi dalam menit; jumlah benar boleh kosong (sesi tanpa soal tidak dimasukkan datanya); mapel dipilih dari daftar yang bisa ditambah (tabel terpisah); target mingguan di tabel terpisah.
- Tabel sesi dirancang bertahap sampai final (id, fokus, durasi, jumlah_benar, jumlah_soal, tanggal, mapel_id). Tabel mapel (id, nama). Tabel target mingguan (id, mapel_id, target_menit, minggu_mulai). Kolom diterjemahkan ke bahasa Inggris saat jadi kode.

**12 Okt: `database.py` Phase 1**
- Pembuatan tiga tabel (melalui beberapa revisi, lihat bagian 7). `get_connection()` dengan PRAGMA. `add_subject`, `add_session`, `get_subjects`, `get_sessions`, `calculate_duration_minutes` dibuat dan diuji dengan `print`.
- Data uji 18 sesi dibuat oleh AI agent VS Code.
- Pengenalan Pandas dari nol (contoh buku di `latihan.py`). `get_sessions_dataframe()` dibuat; nama kolom terakhir diperbaiki dari `subject_id` menjadi `subject_name`.

**12-13 Okt: Statistics**
- `total_study_hours`, `average_session_duration`, uji dengan `empty_df`, konstanta `SESSIONS_COLUMNS`.
- Konsistensi didefinisikan sebagai streak, hari dihitung belajar jika total menit hari itu ≥ 5. `get_active_dates`, `calculate_longest_streak`, `calculate_current_streak(dates, today)` dibuat dan diuji dengan tabel harapan (6 kasus longest, 4 kasus `today` untuk current).
- User memutuskan aturan streak: streak tetap hidup selama hari sebelumnya masih belajar; mati jika hari sebelumnya kosong (sama dengan aturan yang kita sepakati; sempat dikira ada kekeliruan, ternyata tidak).

**14 Okt: Subject Analysis**
- `subject_summary` dibuat; konstanta `SUMMARY_COLUMNS`; uji dengan `sample_df` (mapel tanpa soal menghasilkan `NaN`) dan `empty_df`; pemeriksaan kolom data kosong vs berisi bernilai `True`.
- User menjawab pertanyaan interpretasi (mapel terlama dan akurasi tertinggi sama-sama Mtk Advanced; pola fokus; akurasi vs ukuran sampel).

**15-16 Okt: Trend Analysis**
- `weekly_summary` dibuat bertahap, termasuk hari aktif dua tahap. Uji dengan data tiga minggu (asli), minggu yang semua harinya < 5 menit, dan dua sesi kembar di satu hari.
- `charts.py` dibuat: grafik pertama diperbaiki (label x, satuan, sumbu y mulai 0, nama file), lalu grafik dua panel dan `_empty_figure`. Uji dengan data asli, sample bercelah, dan data kosong (semua figure ditampilkan di layar).
- Interpretasi grafik: lonjakan minggu kedua berasal dari jumlah sesi (4 menjadi 7) **dan** menit per sesi (sekitar 46 menjadi 62); penurunan minggu ketiga dari menit per sesi turun (sesi tetap 7).

**23 Okt: perubahan mingguan**
- `add_weekly_changes` dibuat, diuji dengan data asli (+250 menit / +135,1% / +3 sesi / +3 hari aktif, lalu -28 / -6,4% / 0 / 0) dan sample bercelah (-191 / -95,5% / -2 / -3). Kolom asli dibuang, nama diubah jadi `weekly_changes`, konstanta `WEEKLY_CHANGE_COLUMNS`.

**25 Okt: Goal Tracker bagian database**
- `set_weekly_targets` dan `get_weekly_targets` ditulis dan diperbaiki melalui beberapa putaran (lihat bagian 7).
- `DB_NAME` ditambahkan supaya pengujian memakai database terpisah. Skrip `manual_test_targets.py` dibuat Claude atas permintaan user ("berikan kode untuk aku uji kasus, tinggal run saja").
- Hasil akhir uji: semua PASS dengan alasan benar: target normal tersimpan (120), target kedua menimpa (180, satu baris), tanggal Kamis tersimpan sebagai `2026-10-12`, target 0 dan negatif ditolak, tabel tidak terisi saat ditolak, mapel 999 ditolak dengan "FOREIGN KEY constraint failed", tanggal "besok" ditolak dengan pesan format tanggal, `get_weekly_targets` mengembalikan 2 baris dengan nama mapel.

**26 Okt: keputusan Goal Tracker**
- User menjawab tiga keputusan untuk `goal_progress` (bagian 7).

**28-29 Okt:** user meminta rangkuman chat ini.

## 7. Kesalahan & keputusan desain yang keliru (FOKUS UTAMA)

### 7.1 Keputusan desain dan kesalahan konsep

**1. `get_connection()` menutup koneksi dan mengembalikan cursor**
- Keputusan awal: function membuka koneksi, menyalakan PRAGMA, `commit()`, `close()`, lalu mengembalikan cursor.
- Kenapa keliru: koneksi sudah tertutup sebelum diserahkan, dan cursor tidak bisa hidup tanpa koneksinya.
- Dampak: pemakai akan kena `ProgrammingError` (database tertutup), tidak langsung terlihat sampai ada yang memakainya.
- Perbaikan: function hanya mengembalikan `conn`; cursor dibuat oleh pemakai; pemakai yang menutup. Status: ✅ beres.
- Pelajaran: yang membuka sumber daya harus memikirkan siapa yang menutupnya.

**2. Aturan di desain tidak terbawa ke kode (NOT NULL, tipe tanggal, UNIQUE)**
- Kesalahan: `right_answers` dan `total_questions` ditulis `NOT NULL` padahal desain membolehkan kosong; `date` ditulis `INTEGER` padahal desain `TEXT`; `UNIQUE` pada `subjects.name` tidak ada; ada koma tersisa sebelum kurung tutup tabel (syntax error).
- Dampak: sesi tanpa soal akan ditolak; tanggal terbaca aneh; mapel bisa tersimpan dobel; kode gagal jalan.
- Perbaikan: ketiganya diperbaiki. Status: ✅.
- Pelajaran: baca ulang desain sebelum menulis kode. Aturan koma SQL: tiap baris definisi diakhiri koma kecuali yang terakhir.

**3. Kolom `fokus` tidak konsisten (persentase vs skala 1-10)**
- Keputusan awal user: skala 1-10; di tabel tertulis "persentase". Perbaikan: skala 1-10. Status: ✅.

**4. Kolom `target_menit`/tanggal target mingguan**
- Kesalahan awal: tabel target tidak punya `id` dan `subject_id`; satu kolom `tanggal` diisi "nomor minggu dan tahun" (dua informasi dalam satu kolom). Keputusan dikoreksi: memakai `week_start_date` (tanggal Senin, TEXT), karena konsisten dengan format tanggal sesi dan tidak bermasalah di pergantian tahun. Status: ✅.

**5. Tanggal tersimpan dengan jam**
- Kesalahan: `strptime(...).isoformat()` tanpa `.date()` menyimpan `2026-01-05T00:00:00`. Sempat ada koreksi dua tahap: Claude awalnya hanya menyuruh "kembalikan `.date()`" (kurang lengkap, kesalahan Claude); bentuk yang benar `.date().isoformat()` agar yang tersimpan teks `YYYY-MM-DD`, bukan objek tanggal (objek tanggal memicu `DeprecationWarning` di Python 3.12+).
- Pelajaran: `.isoformat()` mengembalikan teks baru, bukan mengubah objeknya. Format `YYYY-MM-DD` penting karena urutan teksnya sama dengan urutan waktu.

**6. Akurasi dihitung salah jika dirata-rata per sesi**
- Konsep yang disepakati: akurasi = jumlah benar seluruh sesi / jumlah soal seluruh sesi, bukan rata-rata persentase per sesi (sesi 2 soal tidak boleh berbobot sama dengan sesi 100 soal). Dihitung **di luar** `.agg()` karena butuh dua hasil agregat. Status: ✅.

**7. Interpretasi hasil yang kurang tajam**
- Contoh: "lonjakan karena total durasi di tabel" (hanya mengulang pola). Pelajaran: uraikan total menit menjadi jumlah sesi × menit per sesi sebelum menyimpulkan.
- Contoh: "semakin sedikit soal, peluang akurasi tinggi makin besar". Koreksi: sedikit soal membuat akurasi **mudah bergeser ke arah mana pun**, jadi kurang bisa dipercaya (ukuran sampel). Akurasi ditentukan rasio, bukan selisih benar dan soal.
- Pelajaran: korelasi bukan sebab-akibat; data uji buatan agent tidak mewakili kebiasaan nyata.

**8. Keputusan minggu kosong (celah) di tabel mingguan**
- Keputusan user: minggu tanpa sesi **dibiarkan tidak muncul** (tidak diisi); grafik langsung menyambung ke minggu aktif berikutnya; `weekly_changes` menghitung terhadap minggu aktif sebelumnya.
- Risiko yang sudah didiskusikan: garis grafik tampak seperti penurunan bertahap, padahal ada minggu kosong; perubahan -95,5% bisa menyesatkan pembaca yang tidak tahu ada celah. Menit/sesi/hari aktif di minggu kosong sebenarnya 0, rata-rata fokus `NaN`. Opsi yang ditawarkan dan tidak diambil: `fill_missing_weeks` memakai `pd.date_range(freq="W-MON")` dan `reindex`.
- Status: keputusan disengaja, dicatat di komentar kode. Bisa ditinjau ulang saat membuat dashboard.

**9. Keputusan Goal Tracker (berlaku sekarang)**
- Target **per mapel**, bukan total.
- Target baru untuk mapel dan minggu yang sama **menimpa** target lama (bukan ditolak).
- Tanggal non-Senin **disesuaikan otomatis ke Senin minggu itu** (bukan ditolak).
- Mapel punya target tapi belum ada sesi minggu itu: pencapaian **0** (fakta, bukan "tidak ada data").
- Mapel punya sesi tapi tanpa target: **tetap ditampilkan** (artinya merge `outer`). Persentasenya seharusnya `NaN` ("tidak ada target"), bukan 0% dan bukan 100% (saran Claude, belum dikonfirmasi eksplisit oleh user).
- Pencapaian di atas 100%: **dibatasi 100%** (user memilih ini). Saran Claude: simpan persentase mentah dulu lalu batasi di langkah terakhir (`clip(upper=100)`), supaya keputusan bisa dibalik; atau satu kolom yang dibatasi saja. **Belum diputuskan: satu atau dua kolom.**
- Kekhawatiran yang disampaikan Claude: dengan merge `outer` dan data asli yang belum punya target, semua baris sesi (16 kombinasi minggu-mapel) akan tampil tanpa target. Belum diputuskan apakah itu yang diinginkan untuk dashboard.

**10. Desain function: terima data mentah vs tabel mingguan**
- `weekly_changes` menerima sesi mentah (memanggil `weekly_summary` di dalamnya). Claude menyarankan menerima tabel mingguan agar mudah diuji dengan data mini, tapi menyatakan pendekatan user sah. Status: dibiarkan, asal nama parameternya jujur.

### 7.2 Bug / error lain (ringkas)

**`database.py`**

| Bug | Penyebab | Solusi | Status |
|---|---|---|---|
| `add_subject`: nilai kembalian tidak konsisten, koneksi tidak selalu ditutup | return `True` vs `(False, pesan)`; return di tengah `try/except` | semua jalur mengembalikan tuple; validasi sebelum koneksi; `finally` untuk `close()` | ✅ |
| `add_subject`: nama berisi spasi saja lolos | pengecekan kosong dilakukan sebelum `.strip()` | bersihkan dulu, baru periksa; tangkap `AttributeError` untuk non-string | ✅ |
| `add_session`: crash saat sesi tanpa soal | `total_questions <= 0` dibandingkan saat nilainya `None` | pengecekan `is not None` lebih dulu | ✅ |
| `add_session`: crash saat mapel tidak ada | `IntegrityError` tidak ditangkap | `try/except IntegrityError/finally` | ✅ |
| `add_session`: aturan tidak cocok desain | fokus menerima 0; durasi menerima 0; pasangan benar/soal bolong | fokus 1-10, durasi > 0, aturan pasangan dipecah jadi beberapa `if` | ✅ |
| `add_session`: nama parameter `date` menutupi `date` hasil import | nama bentrok | parameter jadi `session_date`, variabel jadi `iso_date` | ✅ |
| `get_sessions`: `ambiguous column name: id` | setelah JOIN dua tabel punya kolom `id` | tulis kolom dengan awalan tabel; ambil nama mapel (bukan `subject_id`) | ✅ |
| `get_sessions`: urutan tidak pasti untuk tanggal sama | hanya ORDER BY tanggal | tambah `study_sessions.id DESC` | ✅ |
| `get_subjects`: belum terurut | tidak ada `ORDER BY` | `ORDER BY name` | ✅ |
| `set_weekly_targets`: `no such column: target_durations` | nama kolom salah ejaan (pakai s), muncul di beberapa tempat | samakan jadi `target_duration` (cari semua kemunculan, termasuk di `DO UPDATE SET`) | ✅ |
| `set_weekly_targets`: tidak tersimpan padahal return `True` | `commit()` hilang (lalu salah tempat di `finally`) | `commit()` di dalam `try` setelah `execute` | ✅ |
| `set_weekly_targets`: semua target valid ditolak | `if target <= 0 or isinstance(target, int)` (negasi hilang) | cek tipe dulu (`not isinstance`), baru nilai, dipecah dua `if` | ✅ |
| `set_weekly_targets`: `TypeError: 'datetime.date' object cannot be interpreted as an integer` | `date(week_start_date)` dipanggil pada objek yang sudah `date` | langsung pakai objek tanggal itu | ✅ |
| `set_weekly_targets`: hasil `isoformat()` dibuang | hasil tidak disimpan ke variabel | `monday = monday.isoformat()` | ✅ |
| `get_weekly_targets`: JOIN berlipat ganda | kondisi `ON ... .subject_id = subject_id` membandingkan kolom dengan dirinya sendiri | bandingkan dengan `subjects.id`; ambil nama mapel | ✅ |
| `get_weekly_targets`: syntax error | koma hilang setelah nama kolom | tambah koma | ✅ |

**`analysis.py`**

| Bug | Penyebab | Solusi | Status |
|---|---|---|---|
| `KeyError: 'duration'` pada `empty_df` | `pd.DataFrame([], columns=[])` tanpa nama kolom | `columns=SESSIONS_COLUMNS`; kolom disimpan di satu konstanta (DRY) | ✅ |
| `pd.DataFrame([], SESSIONS_COLUMNS)` tanpa `columns=` | argumen posisi kedua adalah index, bukan kolom | tulis `columns=...` | ✅ |
| Longest streak hasil `(0, 0)` | input `df['date']` mentah (teks, ada duplikat, urutan terbaru dulu sehingga selisih -1); logika `longest += 1`; reset ke 0; `dates.empty` pada list; `date(...)` dipakai sebagai konstruktor | kirim `get_active_dates(df)`; rekor disamakan dengan streak; reset ke 1; `if not dates`; kurangkan tanggal langsung lalu `.days` | ✅ |
| Output `(14, 15)` tidak cocok dengan kode yang ditempel | file yang dijalankan versi lama | pastikan kode yang dikirim = yang dijalankan | ✅ |
| Current streak: `TypeError date vs datetime` | `today` bertipe `datetime`, elemen daftar bertipe `date` | pakai `date(...)` | ✅ |
| Current streak: logika | arah selisih terbalik, tanpa `.days`, `streak = 0` tanpa `return`, kurung `.days` salah tempat | `(today - dates[-1]).days > 1` lalu `return 0`; `.days` di luar kurung | ✅ |
| Uji longest streak: error saat memanggil | kasus uji (sudah list tanggal) dikirim lewat `get_active_dates`, satu tanggal tanpa kurung siku, argumen salah kurung | kirim list langsung ke function streak | ✅ |
| `subject_summary` mengembalikan `None` | `return` hilang | tambah `return summary` | ✅ |
| `subject_summary`: nama kolom di `.agg()` | `right_answer`, `total_question`, kolom spasi | salin nama dari `SESSIONS_COLUMNS` | ✅ |
| Tabel kosong subject_summary punya kolom sesi, bukan ringkasan | `return df` | `pd.DataFrame([], columns=SUMMARY_COLUMNS)` | ✅ |
| `weekly_summary`: `df.empty()` | `empty` itu properti, bukan method | tanpa kurung | ✅ |
| `weekly_summary`: tidak mengembalikan apa pun | `return` hilang | tambah `return` | ✅ |
| `weekly_summary`: nama `total_minute` vs `total_minutes` di `WEEKLY_COLUMNS` | dua daftar kolom tidak sinkron (ketahuan dari pemeriksaan kolom yang bernilai `False`) | samakan ejaan jadi `total_minute` | ✅ |
| `weekly_summary`: hari aktif | `count` menghitung baris sesi, bukan hari berbeda dengan total ≥ 5 menit; lolos di data asli karena tiap hari cuma satu sesi | dua tahap (total per hari, saring, hitung per minggu, `fillna(0).astype(int)`) | ✅ |
| `weekly_summary`: `AttributeError: Can only use .dt accessor with datetimelike values` | konversi `pd.to_datetime` dilakukan setelah `groupby("date")` | pindahkan persiapan (`copy`, `to_datetime`, `week_start_date`) ke atas | ✅ |
| Fungsi statistik mengubah DataFrame pemanggil | `df['date'] = pd.to_datetime(...)` pada `df` asli | `df = df.copy()` di awal | ✅ |
| `add_weekly_changes`: kode tidak jujur | nama "add" padahal membuang kolom; parameter `weekly` berisi sesi mentah; `weekly.copy()` menganggur; daftar kolom ditulis dua kali | ganti nama jadi `weekly_changes`; parameter `df`; pakai `WEEKLY_CHANGE_COLUMNS` | ✅ |

**`charts.py`**

| Bug | Penyebab | Solusi | Status |
|---|---|---|---|
| Label sumbu x bertumpuk dan menyesatkan | Matplotlib memberi label tiap 2 hari pada sumbu tanggal | `set_xticks` di tiap Senin | ✅ |
| Sumbu y terpotong / tanpa satuan / nama file sisa contoh (`pages.png`) | tidak diatur | `set_ylim(bottom=0)`, label "(menit)", nama file bermakna | ✅ |
| Label x di tengah antar panel; titik hari aktif 7 terpotong | `xlabel` di dua panel; batas atas default | label hanya di panel bawah; `ylim(top=8)` | ✅ |
| `print(weekly.index)` sisa debugging; `SESSIONS_COLUMNS` ditulis ulang; `_empty_figure(weekly)` punya pengecekan ganda | sisa eksperimen | dihapus / diimpor dari `analysis.py` / `_empty_figure()` disederhanakan | ✅ (kecuali `_empty_figure` yang masih memuat parameter dan `if` ganda di versi terakhir yang dilihat `[perlu dicek]`) |

### 7.3 Kesalahan dari sisi Claude (untuk dicatat)

- Menyebut "7 mapel" padahal data asli punya 6 mapel.
- Menyuruh "kembalikan `.date()`" tanpa `.isoformat()` (lihat 7.1 nomor 5).
- Tidak menyebut letak tiga tahap hari aktif di dalam `weekly_summary` (di atas atau di bawah persiapan `to_datetime`), sehingga user kena error urutan baris.
- Memberi acuan 108,3% untuk Fisika minggu 28 Sep, lalu dikoreksi: dengan batas 100% kolom yang tampil 100,0 (versi mentah 108,3).

### 7.4 Pelajaran umum yang berulang

- Jalankan semua kasus uji, termasuk jalur normal dan kasus tepi (kosong, satu elemen, hampir kosong). Hasil benar di data asli belum membuktikan logika benar.
- Baca pesan di balik label `PASS`; penolakan karena alasan yang salah bisa membuat uji lolos.
- Periksa tipe masukan dan keluaran sebelum memanggil function (DataFrame, list, date, datetime).
- Setelah mengubah tipe suatu variabel, telusuri baris di bawahnya yang masih memakai tipe lama.
- Ketika mengganti satu nama kolom, cari semua kemunculannya di function.
- Tulis kode dulu dijalankan, baru dikirim. Pastikan kode yang dikirim sama dengan yang dijalankan.
- Function hanya mengembalikan hasil; `print`, pop-up, dan `plt.show()` urusan lapisan atas.

## 8. Catatan kecil

- **Preferensi dan gaya user:** bahasa Indonesia santai (sering memakai "bro"). Istilah teknis tetap bahasa Inggris. Nama kolom dan function di kode memakai bahasa Inggris. Kalau bingung, user jujur menyebut bagian yang tidak dipahami; sering mengirim kode lengkap beserta output terminal.
- **Cara belajar yang disepakati (skill `coder`):** Claude mengajar dengan urutan Explain, Plan, Try, Review, Improve. Claude tidak langsung memberi solusi lengkap; petunjuk bertahap (hint), dengan pseudocode atau contoh domain lain (mis. data buku) yang bukan jawaban user. Setiap fitur ditutup dengan mini review (What I learned, What I did well, What can improve, Next challenge). Kalau user meminta kode langsung, Claude memberi (contoh: skrip uji manual).
- **Pemecahan masalah untuk bug:** format Error, Cause, Diagnosis, Fix, Lesson.
- **Konvensi nama:** nama tabel `study_sessions`, `subjects`, `study_target_weekly`; konstanta kolom huruf kapital (`SESSIONS_COLUMNS`, `SUMMARY_COLUMNS`, `WEEKLY_COLUMNS`, `WEEKLY_CHANGE_COLUMNS`); `MIN_DAILY_MINUTES = 5`. Satuan ditulis di keterangan (durasi dan target dalam menit).
- **Konvensi return:** function tulis ke database mengembalikan `(True/False, pesan)`; function internal murni boleh `raise`; function analisis menerima DataFrame dan mengembalikan DataFrame/angka tanpa `print`; function grafik mengembalikan `fig`.
- **Nilai kosong:** `NaN`/NULL berarti "tidak ada data"; 0 berarti memang nol. DataFrame kosong selalu dikembalikan **dengan kolom yang benar**, dan diperiksa dengan membandingkan `list(df.columns)` hasil data berisi vs data kosong.
- **Nama file yang dihindari:** jangan menamai file `statistics.py` karena bentrok dengan modul bawaan Python (dipakai `analysis.py`).
- **Pesan panjang di chat** otomatis jadi lampiran (bukan masalah di kode); bungkus kode dengan tiga backtick jika ingin tampil seperti di IDE.
- **Tanggal acuan chat:** 11 Okt 2026 sampai 29 Okt 2026; zona waktu Asia/Jakarta.

## 9. To-do berikutnya

Urutan dari yang paling mendesak. Posisi terakhir di chat: user sudah menjawab tiga keputusan Goal Tracker (26 Okt), Claude memberi urutan langkah dan tugas, lalu user meminta rangkuman. Belum ada kode `goal_progress` yang dikirim.

1. **Jawab dua hal yang masih menggantung:** (a) satu kolom persentase (dibatasi) atau dua kolom (mentah dan dibatasi); (b) persentase untuk mapel tanpa target = `NaN` (disarankan) atau lainnya.
2. **Isi tabel harapan skenario mini sebelum menjalankan kode:** target Fisika 100 menit dan Kimia 60 menit minggu 12 Okt; sesi Fisika 40 + 80 menit (13 dan 14 Okt) dan Sejarah 30 menit (13 Okt, tanpa target). Acuan hitungan berdasarkan keputusan user: Fisika target 100, pencapaian 120, persentase mentah 120% (dibatasi 100); Kimia target 60, pencapaian 0, persentase 0%; Sejarah target `NaN`, pencapaian 30, persentase `NaN`.
3. **Tulis di `analysis.py`:**
   - konstanta `TARGET_COLUMNS` dan `PROGRESS_COLUMNS`;
   - `get_targets_dataframe()` yang membungkus `get_weekly_targets()` jadi DataFrame bernama kolom;
   - `goal_progress(sessions_df, targets_df)`: menit nyata per (minggu, mapel); samakan tipe dan nama kolom kunci (minggu dari teks menjadi tanggal lewat `pd.to_datetime`, `rename`); `merge(..., how="outer", on=[minggu, mapel])`; `fillna(0)` **hanya** pada kolom pencapaian; persentase = pencapaian / target × 100; batasi 100 dengan `clip(upper=100)` (cek perilaku pada `NaN`); tabel kosong tetap mengembalikan kolom yang benar; pemeriksaan kolom data kosong vs berisi.
4. **Uji** dengan data mini, lalu data asli (target ditambahkan ke `test_study.db` lewat `set_weekly_targets`, jangan ke `study.db`). Acuan data asli: Fisika per minggu 35/65/58; target 60 di minggu 28 Sep menghasilkan 108,3% mentah (100,0 setelah dibatasi); target 120 di minggu 5 Okt menghasilkan 48,3%; Coding minggu 5 Okt bernilai 100 menit.
5. **Tambahan kecil yang belum dikerjakan:** kasus uji target bertipe teks (`"abc"`, harus ditolak dengan pesan tipe, bukan crash) di `manual_test_targets.py`; pesan sukses `set_weekly_targets` sebaiknya menyebut tanggal Senin yang dipakai; `add_session` belum punya pengecekan tipe (teks pada angka akan crash); `sample_df` ada di dua file dengan isi berbeda (satukan di Phase 6); `True`/`False` lolos `isinstance(..., int)` (boleh dibiarkan).
6. **Verifikasi:** versi final `weekly_changes` dan `_empty_figure` (tidak ditempel di chat terakhir); jalankan ulang `plot_weekly_overview` untuk data sample bercelah dan data kosong (rencana di review 16 Okt, hasilnya belum dikirim ke chat).
7. **Phase 6 (pytest):** ubah semua kasus uji yang dibuat selama ini jadi test pytest dengan database terpisah (memakai `DB_NAME`) dan data buatan: streak (6 kasus longest, kasus current dengan `today` 11/12/13/16 Okt), `weekly_summary` (hari kembar, hari < 5 menit, minggu semua < 5 menit), `subject_summary` (mapel tanpa soal, data kosong), `set_weekly_targets` (7 kasus), `add_session` (validasi).
8. **Phase 7:** pilih UI (Streamlit atau CustomTkinter), pop-up pesan error, tombol Start/Stop timer (aturan tengah malam, jam mulai belum disimpan), pemilihan mapel dari `get_subjects()`, README, dashboard mengikuti desain "SelfStudy", dan Git.
9. **Setelah proyek ini selesai:** pikirkan Student Performance Predictor.
