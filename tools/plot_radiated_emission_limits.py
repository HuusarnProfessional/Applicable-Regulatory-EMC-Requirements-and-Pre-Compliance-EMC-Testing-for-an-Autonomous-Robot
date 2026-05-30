from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt


LIMIT_BREAKS_MHZ = [30.0, 230.0, 1000.0]
LIMIT_LEVELS_DBUV_M = [40.0, 47.0, 47.0]

CSV_PATH = Path("measurement_data.csv")
OUTPUT_PATH = Path("figures/radiated_emission_reference_limits.png")


def load_measurement_data(csv_path: Path) -> tuple[list[float], list[float]]:
    """Load future measurement data from CSV.

    Expected columns:
    - frequency_mhz
    - level_dbuv_m
    """
    frequencies_mhz: list[float] = []
    levels_dbuv_m: list[float] = []

    with csv_path.open(newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        required_columns = {"frequency_mhz", "level_dbuv_m"}

        if reader.fieldnames is None or not required_columns.issubset(reader.fieldnames):
            raise ValueError(
                "CSV file must contain the columns 'frequency_mhz' and 'level_dbuv_m'."
            )

        for row in reader:
            frequencies_mhz.append(float(row["frequency_mhz"]))
            levels_dbuv_m.append(float(row["level_dbuv_m"]))

    return frequencies_mhz, levels_dbuv_m


def make_plot(csv_path: Path = CSV_PATH, output_path: Path = OUTPUT_PATH) -> None:
    fig, ax = plt.subplots(figsize=(10, 5.5))

    ax.step(
        LIMIT_BREAKS_MHZ,
        LIMIT_LEVELS_DBUV_M,
        where="post",
        color="tab:red",
        linewidth=2.2,
        label="EN 61000-6-3 reference limit",
    )

    if csv_path.exists():
        frequency_mhz, level_dbuv_m = load_measurement_data(csv_path)
        ax.plot(
            frequency_mhz,
            level_dbuv_m,
            color="tab:blue",
            linewidth=1.5,
            label="Measured data",
        )
    else:
        ax.text(
            0.5,
            0.5,
            "No measurement data loaded yet",
            ha="center",
            va="center",
            transform=ax.transAxes,
            fontsize=11,
            color="0.35",
            bbox={"boxstyle": "round,pad=0.4", "facecolor": "white", "edgecolor": "0.7"},
        )

    ax.set_title("Radiated Emission Reference Limits")
    ax.set_xlabel("Frequency (MHz)")
    ax.set_ylabel(r"Field strength (dB$\mu$V/m)")
    ax.set_xlim(30, 1000)
    ax.set_ylim(0, 55)
    ax.grid(True, which="both", linestyle="--", linewidth=0.6, alpha=0.6)
    ax.legend(loc="lower right")
    fig.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    make_plot()
