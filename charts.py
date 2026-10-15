# charts.py

import matplotlib.pyplot as plt
import pandas as pd
from analysis import get_sessions_dataframe, weekly_summary

SESSIONS_COLUMNS=['id', 'focus_scale', 'duration', 'right_answers', 'total_questions', 'date', 'subject_name']

def plot_minute_per_week(weekly):
    fig, ax = plt.subplots()
    ax.plot(weekly.index, weekly["total_minute"], marker="o")
    print(weekly.index)
    ax.set_title("Total durasi belajar per minggu")
    ax.set_xlabel("Minggu (mulai Senin)")
    ax.set_ylabel("Total durasi (menit)")

    ax.set_xticks(weekly.index.date)
    ax.set_xticklabels(weekly.index.date)
    ax.set_ylim(bottom=0)
    
    return fig


if __name__ == "__main__":
    df = get_sessions_dataframe()
    sample_df = pd.DataFrame(
            [
                (1, 8, 60, 15, 20, "2026-10-01", "Fisika"),
                (2, 6, 40, 9, 10, "2026-10-02", "Fisika"),
                (3, 7, 30, None, None, "2026-10-03", "Fisika"),
                (4, 5, 45, None, None, "2026-10-01", "Sejarah"),
                (5, 9, 25, None, None, "2026-10-04", "Sejarah"),
                (6, 8, 3, None, None, "2026-10-06", "Fisika"),
                (6, 8, 3, None, None, "2026-10-07", "Fisika"),
                (6, 8, 3, None, None, "2026-10-13", "Fisika"),
                (6, 8, 3, None, None, "2026-10-14", "Fisika"),
                (6, 8, 3, None, None, "2026-10-14", "Fisika"),
            ],
            columns=SESSIONS_COLUMNS,
            )

    fig = plot_minute_per_week(weekly_summary(df))
    fig.savefig("weekly_minutes.png")
    fig = plot_minute_per_week(weekly_summary(sample_df))
    fig.savefig("weekly_minutes_sample.png")
    plt.show()