"""Make the plots from the result csv files.

    python plot.py            # 1080p plots (from results.csv)
    python plot.py 720        # 720p plots  (from results_720p.csv, files start with 720p_)
    python plot.py compare    # 1080p vs 720p in one picture
"""
import sys

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import ScalarFormatter

COLORS = {"libx264": "tab:orange", "libx265": "tab:green",
          "SVT-AV1": "tab:blue", "vvenc": "tab:red"}
BITRATES = [200, 500, 1000, 3000, 5000]


def style(ax, log_y=False):
    """Axis labels and grid. X is the bitrate on a log scale."""
    ax.set_xscale("log")
    ax.set_xticks(BITRATES)
    ax.xaxis.set_major_formatter(ScalarFormatter())   # show 1000 instead of 10^3
    ax.minorticks_off()
    ax.set_xlabel("bitrate (kbit/s)")
    if log_y:
        ax.set_yscale("log")
    ax.grid(alpha=.3)
    ax.legend()


def plot_resolution(csv_file, prefix):
    """The 5 standard plots for one resolution."""
    data = pd.read_csv(csv_file)

    def plot(columns, ylabel, filename, log_y=False):
        # one small plot per column, side by side, one line per codec
        fig, axes = plt.subplots(1, len(columns), figsize=(5 * len(columns), 4))
        axes = [axes] if len(columns) == 1 else axes
        for ax, column in zip(axes, columns):
            for codec, rows in data.groupby("codec"):
                ax.plot(rows.actual_kbps, rows[column], "o-", color=COLORS[codec], label=codec)
            ax.set_ylabel(column if len(columns) > 1 else ylabel)
            style(ax, log_y)
        plt.tight_layout()
        plt.savefig(prefix + filename, dpi=120)
        plt.close()

    plot(["psnr", "ssim", "vmaf"], "", "1_quality.png")
    plot(["enc_time_s"], "encoding time (s)", "2_encoding_time.png", log_y=True)
    plot(["enc_energy_wh"], "encoding energy (Wh)", "3_encoding_energy.png", log_y=True)
    plot(["dec_time_s"], "decoding time (s)", "4_decoding_time.png", log_y=True)
    plot(["dec_energy_wh"], "decoding energy (Wh)", "5_decoding_energy.png", log_y=True)


def plot_compare():
    """1080p (solid line) vs 720p (dashed line): VMAF, encoding time, encoding energy."""
    results = [("1080p", "-", pd.read_csv("results.csv")),
               ("720p", "--", pd.read_csv("results_720p.csv"))]
    metrics = [("vmaf", "VMAF (higher = better)", False),
               ("enc_time_s", "encoding time (s)", True),
               ("enc_energy_wh", "encoding energy (Wh)", True)]

    fig, axes = plt.subplots(1, 3, figsize=(16, 4.5))
    for ax, (column, label, log_y) in zip(axes, metrics):
        for codec, color in COLORS.items():
            for resolution, line, data in results:
                rows = data[data.codec == codec]
                ax.plot(rows.actual_kbps, rows[column], "o" + line,
                        color=color, label=f"{codec} {resolution}")
        ax.set_ylabel(label)
        style(ax, log_y)
        ax.legend(fontsize=7)
    plt.tight_layout()
    plt.savefig("6_compare_1080p_vs_720p.png", dpi=120)


mode = sys.argv[1] if len(sys.argv) > 1 else "1080"
if mode == "compare":
    plot_compare()
elif mode == "1080":
    plot_resolution("results.csv", prefix="")
else:
    plot_resolution(f"results_{mode}p.csv", prefix=f"{mode}p_")
