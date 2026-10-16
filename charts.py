# charts.py

import matplotlib.pyplot as plt
import pandas as pd
from analysis import get_sessions_dataframe, weekly_summary, SESSIONS_COLUMNS

def _empty_figure(weekly):
    if weekly.empty:
        fig, ax = plt.subplots()
        
        ax.text(0.5, 0.5, 'Belum Ada Data', 
            fontsize=16, 
            fontweight='bold',
            color='darkgray', 
            ha='center', 
            va='center', 
            transform=ax.transAxes)
        
        ax.axis('off')
        
        return fig

def plot_minute_per_week(weekly):
    if weekly.empty:
        fig = _empty_figure(weekly)
    
        return fig
        
    fig, ax = plt.subplots()
    ax.plot(weekly.index, weekly["total_minute"], marker="o")
    ax.set_title("Total durasi belajar per minggu")
    ax.set_xlabel("Minggu (mulai Senin)")
    ax.set_ylabel("Total durasi (menit)")

    ax.set_xticks(weekly.index.date)
    ax.set_xticklabels(weekly.index.date)
    ax.set_ylim(bottom=0)
    
    return fig

def plot_weekly_overview(weekly):
    if weekly.empty:
        fig = _empty_figure(weekly)
        
        return fig

    fig, (ax_top, ax_bottom) = plt.subplots(nrows=2, ncols=1, sharex=True, constrained_layout=True)

    ax_top.bar(weekly.index, weekly["total_minute"], width=4)
    ax_bottom.plot(weekly.index, weekly["total_active_days"], marker="o")

    ax_top.set_title("Total durasi belajar per minggu")
    ax_top.set_ylabel("Total durasi (menit)")

    ax_bottom.set_title("Total hari aktif per minggu")
    ax_bottom.set_xlabel("Minggu (mulai Senin)")
    ax_bottom.set_ylabel("Total hari aktif (Hari)")

    ax_bottom.set_xticks(weekly.index.date)
    ax_bottom.set_xticklabels(weekly.index.date)
    ax_bottom.set_ylim(bottom=0, top=8)

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
                (6, 8, 3, None, None, "2026-10-13", "Fisika"),
                (6, 8, 3, None, None, "2026-10-14", "Fisika"),
                (6, 8, 3, None, None, "2026-10-14", "Fisika"),
            ],
            columns=SESSIONS_COLUMNS,
            )

    empty_df = pd.DataFrame([], columns=SESSIONS_COLUMNS)

    fig = plot_minute_per_week(weekly_summary(df))
    fig.savefig("weekly_minutes.png")
    fig = plot_minute_per_week(weekly_summary(sample_df))
    fig.savefig("weekly_minutes_sample.png")
    fig = plot_minute_per_week(weekly_summary(empty_df))
    fig.savefig("weekly_minutes_empty.png")

    fig = plot_weekly_overview(weekly_summary(df))
    fig.savefig("weekly_summary.png")

    plt.show()