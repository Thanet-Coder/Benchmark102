import csv
import os
import math
import matplotlib.pyplot as plt


# ============================================================
# Configuration
# ============================================================

RESULTS_FILE = os.path.join(
    "results",
    "benchmark_results.csv"
)

GRAPHS_DIR = os.path.join(
    "results",
    "graphs",
    "dissertation"
)

DPI = 300


EXPECTED_ALGORITHMS = [
    "Ascon-AEAD128",
    "AES-GCM",
    "ChaCha20-Poly1305"
]


DATA_SIZES = [
    1024,
    4096,
    16384,
    65536,
    262144,
    1048576
]


DATA_SIZE_LABELS = {
    1024: "1 KB",
    4096: "4 KB",
    16384: "16 KB",
    65536: "64 KB",
    262144: "256 KB",
    1048576: "1 MB"
}


# Keep algorithm presentation consistent between figures.
ALGORITHM_COLORS = {
    "Ascon-AEAD128": "tab:blue",
    "AES-GCM": "tab:orange",
    "ChaCha20-Poly1305": "tab:green"
}


# ============================================================
# Data loading and preparation
# ============================================================

def load_results():
    """
    Load benchmark results from the final CSV dataset.
    """

    with open(
        RESULTS_FILE,
        "r",
        newline="",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        return list(reader)


def calculate_throughput_mb_s(
    data_size_bytes,
    mean_ns
):
    """
    Calculate throughput using decimal MB/s.

    1 MB = 1,000,000 bytes.
    """

    seconds = mean_ns / 1_000_000_000
    megabytes = data_size_bytes / 1_000_000

    return megabytes / seconds


def calculate_cpu_time_per_byte(
    cpu_time_ns,
    data_size_bytes
):
    """
    Calculate CPU processing time per byte.
    """

    return cpu_time_ns / data_size_bytes


def calculate_coefficient_of_variation(
    mean_ns,
    stdev_ns
):
    """
    Calculate coefficient of variation as a percentage.
    """

    if mean_ns == 0:
        return 0.0

    return (
        stdev_ns / mean_ns
    ) * 100


def convert_result(result):
    """
    Convert one CSV row to appropriate numeric types
    and calculate derived metrics.
    """

    data_size = int(
        result["data_size_bytes"]
    )

    mean_ns = float(
        result["mean_ns"]
    )

    stdev_ns = float(
        result["stdev_ns"]
    )

    cpu_time_ns = float(
        result["cpu_time_ns"]
    )

    measurements = [
        float(value)
        for value in result["measurements"].split(";")
    ]

    return {
        "algorithm": result["algorithm"],
        "data_size_bytes": data_size,
        "operation": result["operation"],

        "measurements": measurements,

        "mean_ns": mean_ns,
        "median_ns": float(result["median_ns"]),
        "min_ns": float(result["min_ns"]),
        "max_ns": float(result["max_ns"]),
        "stdev_ns": stdev_ns,

        "cpu_time_ns": cpu_time_ns,
        "cpu_batch_runs": int(
            result["cpu_batch_runs"]
        ),

        "memory_before_mb": float(
            result["memory_before_mb"]
        ),

        "memory_after_mb": float(
            result["memory_after_mb"]
        ),

        "memory_difference_mb": float(
            result["memory_difference_mb"]
        ),

        "throughput_mb_s": (
            calculate_throughput_mb_s(
                data_size,
                mean_ns
            )
        ),

        "cpu_time_per_byte_ns": (
            calculate_cpu_time_per_byte(
                cpu_time_ns,
                data_size
            )
        ),

        "coefficient_of_variation_percent": (
            calculate_coefficient_of_variation(
                mean_ns,
                stdev_ns
            )
        )
    }


def prepare_results():
    """
    Load and convert every final benchmark result.
    """

    raw_results = load_results()

    return [
        convert_result(result)
        for result in raw_results
    ]


def find_result(
    results,
    algorithm,
    size,
    operation
):
    """
    Locate one benchmark result.
    """

    for result in results:

        if (
            result["algorithm"] == algorithm
            and result["data_size_bytes"] == size
            and result["operation"] == operation
        ):
            return result

    raise ValueError(
        f"Benchmark result not found: "
        f"{algorithm}, {size}, {operation}"
    )


# ============================================================
# Figure helpers
# ============================================================

def create_figure():
    """
    Create a standard dissertation-sized figure.
    """

    return plt.figure(
        figsize=(10, 6)
    )


def configure_data_size_axis():
    """
    Configure the common data-size x-axis.
    """

    plt.xscale(
        "log",
        base=2
    )

    plt.xticks(
        DATA_SIZES,
        [
            DATA_SIZE_LABELS[size]
            for size in DATA_SIZES
        ]
    )

    plt.xlabel(
        "Input Data Size"
    )


def configure_grid():
    """
    Add restrained background grid lines.
    """

    plt.grid(
        True,
        which="major",
        linestyle="--",
        alpha=0.35
    )


def save_figure(filename):
    """
    Save and close the current figure.
    """

    os.makedirs(
        GRAPHS_DIR,
        exist_ok=True
    )

    output_file = os.path.join(
        GRAPHS_DIR,
        filename
    )

    plt.tight_layout()

    plt.savefig(
        output_file,
        dpi=DPI,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"Created: {output_file}"
    )


# ============================================================
# Figure 1
# Encryption throughput
# ============================================================

def figure_01_encryption_throughput(results):

    create_figure()

    for algorithm in EXPECTED_ALGORITHMS:

        values = [
            find_result(
                results,
                algorithm,
                size,
                "encryption"
            )["throughput_mb_s"]
            for size in DATA_SIZES
        ]

        plt.plot(
            DATA_SIZES,
            values,
            marker="o",
            linewidth=2,
            label=algorithm,
            color=ALGORITHM_COLORS[algorithm]
        )

    configure_data_size_axis()
    configure_grid()

    plt.ylabel(
        "Throughput (MB/s)"
    )

    plt.title(
        "Encryption Throughput by Input Data Size"
    )

    plt.legend()

    save_figure(
        "Figure_01_Encryption_Throughput.png"
    )


# ============================================================
# Figure 2
# Decryption throughput
# ============================================================

def figure_02_decryption_throughput(results):

    create_figure()

    for algorithm in EXPECTED_ALGORITHMS:

        values = [
            find_result(
                results,
                algorithm,
                size,
                "decryption"
            )["throughput_mb_s"]
            for size in DATA_SIZES
        ]

        plt.plot(
            DATA_SIZES,
            values,
            marker="o",
            linewidth=2,
            label=algorithm,
            color=ALGORITHM_COLORS[algorithm]
        )

    configure_data_size_axis()
    configure_grid()

    plt.ylabel(
        "Throughput (MB/s)"
    )

    plt.title(
        "Decryption Throughput by Input Data Size"
    )

    plt.legend()

    save_figure(
        "Figure_02_Decryption_Throughput.png"
    )


# ============================================================
# Figure 3
# Encryption execution time
# ============================================================

def figure_03_encryption_execution_time(results):

    create_figure()

    for algorithm in EXPECTED_ALGORITHMS:

        values_ms = [
            find_result(
                results,
                algorithm,
                size,
                "encryption"
            )["mean_ns"] / 1_000_000
            for size in DATA_SIZES
        ]

        plt.plot(
            DATA_SIZES,
            values_ms,
            marker="o",
            linewidth=2,
            label=algorithm,
            color=ALGORITHM_COLORS[algorithm]
        )

    configure_data_size_axis()

    plt.yscale(
        "log"
    )

    configure_grid()

    plt.ylabel(
        "Mean Execution Time (ms, log scale)"
    )

    plt.title(
        "Encryption Execution Time by Input Data Size"
    )

    plt.legend()

    save_figure(
        "Figure_03_Encryption_Execution_Time.png"
    )


# ============================================================
# Figure 4
# Decryption execution time
# ============================================================

def figure_04_decryption_execution_time(results):

    create_figure()

    for algorithm in EXPECTED_ALGORITHMS:

        values_ms = [
            find_result(
                results,
                algorithm,
                size,
                "decryption"
            )["mean_ns"] / 1_000_000
            for size in DATA_SIZES
        ]

        plt.plot(
            DATA_SIZES,
            values_ms,
            marker="o",
            linewidth=2,
            label=algorithm,
            color=ALGORITHM_COLORS[algorithm]
        )

    configure_data_size_axis()

    plt.yscale(
        "log"
    )

    configure_grid()

    plt.ylabel(
        "Mean Execution Time (ms, log scale)"
    )

    plt.title(
        "Decryption Execution Time by Input Data Size"
    )

    plt.legend()

    save_figure(
        "Figure_04_Decryption_Execution_Time.png"
    )


# ============================================================
# Figure 5
# Encryption CPU time per byte
# ============================================================

def figure_05_encryption_cpu_per_byte(results):

    create_figure()

    for algorithm in EXPECTED_ALGORITHMS:

        values = [
            find_result(
                results,
                algorithm,
                size,
                "encryption"
            )["cpu_time_per_byte_ns"]
            for size in DATA_SIZES
        ]

        plt.plot(
            DATA_SIZES,
            values,
            marker="o",
            linewidth=2,
            label=algorithm,
            color=ALGORITHM_COLORS[algorithm]
        )

    configure_data_size_axis()

    plt.yscale(
        "log"
    )

    configure_grid()

    plt.ylabel(
        "CPU Time per Byte (ns, log scale)"
    )

    plt.title(
        "Encryption CPU Processing Cost per Byte"
    )

    plt.legend()

    save_figure(
        "Figure_05_Encryption_CPU_Time_Per_Byte.png"
    )


# ============================================================
# Figure 6
# Decryption CPU time per byte
# ============================================================

def figure_06_decryption_cpu_per_byte(results):

    create_figure()

    for algorithm in EXPECTED_ALGORITHMS:

        values = [
            find_result(
                results,
                algorithm,
                size,
                "decryption"
            )["cpu_time_per_byte_ns"]
            for size in DATA_SIZES
        ]

        plt.plot(
            DATA_SIZES,
            values,
            marker="o",
            linewidth=2,
            label=algorithm,
            color=ALGORITHM_COLORS[algorithm]
        )

    configure_data_size_axis()

    plt.yscale(
        "log"
    )

    configure_grid()

    plt.ylabel(
        "CPU Time per Byte (ns, log scale)"
    )

    plt.title(
        "Decryption CPU Processing Cost per Byte"
    )

    plt.legend()

    save_figure(
        "Figure_06_Decryption_CPU_Time_Per_Byte.png"
    )


# ============================================================
# Grouped-bar helper
# ============================================================

def create_grouped_bars(
    values_by_algorithm,
    ylabel,
    title,
    filename
):
    """
    Create grouped bars for all algorithms and data sizes.
    """

    create_figure()

    positions = list(
        range(len(DATA_SIZES))
    )

    width = 0.25

    offsets = [
        -width,
        0,
        width
    ]

    for algorithm, offset in zip(
        EXPECTED_ALGORITHMS,
        offsets
    ):

        positions_with_offset = [
            position + offset
            for position in positions
        ]

        plt.bar(
            positions_with_offset,
            values_by_algorithm[algorithm],
            width=width,
            label=algorithm,
            color=ALGORITHM_COLORS[algorithm]
        )

    plt.xticks(
        positions,
        [
            DATA_SIZE_LABELS[size]
            for size in DATA_SIZES
        ]
    )

    plt.xlabel(
        "Input Data Size"
    )

    plt.ylabel(
        ylabel
    )

    plt.title(
        title
    )

    configure_grid()

    plt.legend()

    save_figure(
        filename
    )


# ============================================================
# Figure 7
# Encryption variability
# ============================================================

def figure_07_encryption_variability(results):

    values = {}

    for algorithm in EXPECTED_ALGORITHMS:

        values[algorithm] = [
            find_result(
                results,
                algorithm,
                size,
                "encryption"
            )["coefficient_of_variation_percent"]
            for size in DATA_SIZES
        ]

    create_grouped_bars(
        values,
        "Coefficient of Variation (%)",
        "Encryption Timing Variability",
        "Figure_07_Encryption_Timing_Variability.png"
    )


# ============================================================
# Figure 8
# Decryption variability
# ============================================================

def figure_08_decryption_variability(results):

    values = {}

    for algorithm in EXPECTED_ALGORITHMS:

        values[algorithm] = [
            find_result(
                results,
                algorithm,
                size,
                "decryption"
            )["coefficient_of_variation_percent"]
            for size in DATA_SIZES
        ]

    create_grouped_bars(
        values,
        "Coefficient of Variation (%)",
        "Decryption Timing Variability",
        "Figure_08_Decryption_Timing_Variability.png"
    )


# ============================================================
# Figure 9
# Encryption memory
# ============================================================

def figure_09_encryption_memory(results):

    create_figure()

    for algorithm in EXPECTED_ALGORITHMS:

        values = [
            max(
                0.0,
                find_result(
                    results,
                    algorithm,
                    size,
                    "encryption"
                )["memory_difference_mb"]
            )
            for size in DATA_SIZES
        ]

        plt.plot(
            DATA_SIZES,
            values,
            marker="o",
            linewidth=2,
            label=algorithm,
            color=ALGORITHM_COLORS[algorithm]
        )

    configure_data_size_axis()
    configure_grid()

    plt.ylabel(
        "Average RSS Memory Difference (MB)"
    )

    plt.title(
        "Encryption Memory Usage by Input Data Size"
    )

    plt.legend()

    save_figure(
        "Figure_09_Encryption_Memory.png"
    )


# ============================================================
# Figure 10
# Decryption memory
# ============================================================

def figure_10_decryption_memory(results):

    create_figure()

    for algorithm in EXPECTED_ALGORITHMS:

        values = [
            max(
                0.0,
                find_result(
                    results,
                    algorithm,
                    size,
                    "decryption"
                )["memory_difference_mb"]
            )
            for size in DATA_SIZES
        ]

        plt.plot(
            DATA_SIZES,
            values,
            marker="o",
            linewidth=2,
            label=algorithm,
            color=ALGORITHM_COLORS[algorithm]
        )

    configure_data_size_axis()
    configure_grid()

    plt.ylabel(
        "Average RSS Memory Difference (MB)"
    )

    plt.title(
        "Decryption Memory Usage by Input Data Size"
    )

    plt.legend()

    save_figure(
        "Figure_10_Decryption_Memory.png"
    )


# ============================================================
# Figure 11
# Encryption speedup relative to Ascon
# ============================================================

def figure_11_encryption_speedup(results):

    create_figure()

    for algorithm in [
        "AES-GCM",
        "ChaCha20-Poly1305"
    ]:

        speedups = []

        for size in DATA_SIZES:

            ascon = find_result(
                results,
                "Ascon-AEAD128",
                size,
                "encryption"
            )

            comparison = find_result(
                results,
                algorithm,
                size,
                "encryption"
            )

            speedup = (
                ascon["mean_ns"]
                / comparison["mean_ns"]
            )

            speedups.append(
                speedup
            )

        plt.plot(
            DATA_SIZES,
            speedups,
            marker="o",
            linewidth=2,
            label=algorithm,
            color=ALGORITHM_COLORS[algorithm]
        )

    configure_data_size_axis()

    plt.yscale(
        "log"
    )

    configure_grid()

    plt.ylabel(
        "Speedup Relative to Ascon-AEAD128 (x, log scale)"
    )

    plt.title(
        "Encryption Speedup Relative to Ascon-AEAD128"
    )

    plt.legend()

    save_figure(
        "Figure_11_Encryption_Speedup_vs_Ascon.png"
    )


# ============================================================
# Figure 12
# Normalised performance heatmap
# ============================================================

def normalise_higher_is_better(values):
    """
    Scale values between 0 and 1.

    Higher original values receive higher scores.
    """

    minimum = min(values)
    maximum = max(values)

    if maximum == minimum:
        return [
            1.0
            for _ in values
        ]

    return [
        (
            value - minimum
        ) / (
            maximum - minimum
        )
        for value in values
    ]


def normalise_lower_is_better(values):
    """
    Scale values between 0 and 1.

    Lower original values receive higher scores.
    """

    minimum = min(values)
    maximum = max(values)

    if maximum == minimum:
        return [
            1.0
            for _ in values
        ]

    return [
        1.0 - (
            (
                value - minimum
            ) / (
                maximum - minimum
            )
        )
        for value in values
    ]


def figure_12_performance_heatmap(results):
    """
    Create a summary heatmap using 1 MB benchmark results.

    Scores are normalised within each metric.

    1.0 = strongest result for that metric.
    0.0 = weakest result for that metric.

    Higher is better:
        throughput

    Lower is better:
        execution time
        CPU time per byte
        timing variability
        memory difference
    """

    size = 1048576

    metrics = [
        "Encryption Throughput",
        "Decryption Throughput",
        "Encryption Time",
        "Decryption Time",
        "Encryption CPU/Byte",
        "Decryption CPU/Byte",
        "Encryption Variability",
        "Decryption Variability",
        "Encryption Memory",
        "Decryption Memory"
    ]

    raw_rows = []

    # --------------------------------------------------------
    # Throughput
    # --------------------------------------------------------

    raw_rows.append([
        find_result(
            results,
            algorithm,
            size,
            "encryption"
        )["throughput_mb_s"]
        for algorithm in EXPECTED_ALGORITHMS
    ])

    raw_rows.append([
        find_result(
            results,
            algorithm,
            size,
            "decryption"
        )["throughput_mb_s"]
        for algorithm in EXPECTED_ALGORITHMS
    ])

    # --------------------------------------------------------
    # Execution time
    # --------------------------------------------------------

    raw_rows.append([
        find_result(
            results,
            algorithm,
            size,
            "encryption"
        )["mean_ns"]
        for algorithm in EXPECTED_ALGORITHMS
    ])

    raw_rows.append([
        find_result(
            results,
            algorithm,
            size,
            "decryption"
        )["mean_ns"]
        for algorithm in EXPECTED_ALGORITHMS
    ])

    # --------------------------------------------------------
    # CPU per byte
    # --------------------------------------------------------

    raw_rows.append([
        find_result(
            results,
            algorithm,
            size,
            "encryption"
        )["cpu_time_per_byte_ns"]
        for algorithm in EXPECTED_ALGORITHMS
    ])

    raw_rows.append([
        find_result(
            results,
            algorithm,
            size,
            "decryption"
        )["cpu_time_per_byte_ns"]
        for algorithm in EXPECTED_ALGORITHMS
    ])

    # --------------------------------------------------------
    # Variability
    # --------------------------------------------------------

    raw_rows.append([
        find_result(
            results,
            algorithm,
            size,
            "encryption"
        )["coefficient_of_variation_percent"]
        for algorithm in EXPECTED_ALGORITHMS
    ])

    raw_rows.append([
        find_result(
            results,
            algorithm,
            size,
            "decryption"
        )["coefficient_of_variation_percent"]
        for algorithm in EXPECTED_ALGORITHMS
    ])

    # --------------------------------------------------------
    # Memory
    # --------------------------------------------------------

    raw_rows.append([
        max(
            0.0,
            find_result(
                results,
                algorithm,
                size,
                "encryption"
            )["memory_difference_mb"]
        )
        for algorithm in EXPECTED_ALGORITHMS
    ])

    raw_rows.append([
        max(
            0.0,
            find_result(
                results,
                algorithm,
                size,
                "decryption"
            )["memory_difference_mb"]
        )
        for algorithm in EXPECTED_ALGORITHMS
    ])

    # --------------------------------------------------------
    # Normalise rows
    # --------------------------------------------------------

    heatmap_data = []

    for index, row in enumerate(raw_rows):

        if index in [0, 1]:
            normalised = normalise_higher_is_better(
                row
            )
        else:
            normalised = normalise_lower_is_better(
                row
            )

        heatmap_data.append(
            normalised
        )

    # --------------------------------------------------------
    # Create heatmap
    # --------------------------------------------------------

    plt.figure(
        figsize=(9, 8)
    )

    image = plt.imshow(
        heatmap_data,
        aspect="auto",
        vmin=0,
        vmax=1,
        cmap="viridis"
    )

    plt.colorbar(
        image,
        label="Normalised Performance Score"
    )

    plt.xticks(
        range(len(EXPECTED_ALGORITHMS)),
        EXPECTED_ALGORITHMS
    )

    plt.yticks(
        range(len(metrics)),
        metrics
    )

    # Display score within each cell.
    for row_index in range(
        len(heatmap_data)
    ):

        for column_index in range(
            len(EXPECTED_ALGORITHMS)
        ):

            score = heatmap_data[
                row_index
            ][
                column_index
            ]

            plt.text(
                column_index,
                row_index,
                f"{score:.2f}",
                ha="center",
                va="center",
                color=(
                    "white"
                    if score < 0.50
                    else "black"
                )
            )

    plt.title(
        "Normalised 1 MB Performance Comparison"
    )

    plt.xlabel(
        "Algorithm"
    )

    plt.ylabel(
        "Performance Metric"
    )

    save_figure(
        "Figure_12_Performance_Heatmap.png"
    )


# ============================================================
# Main
# ============================================================

def main():

    print("=" * 70)
    print("LightCryptBench Dissertation Figure Generation")
    print("=" * 70)

    print()
    print(
        f"Results file: {RESULTS_FILE}"
    )

    print(
        f"Output directory: {GRAPHS_DIR}"
    )

    print(
        f"Image resolution: {DPI} DPI"
    )

    print()

    results = prepare_results()

    print(
        f"Loaded {len(results)} benchmark results."
    )

    if len(results) != 36:

        raise ValueError(
            f"Expected 36 benchmark results, "
            f"but loaded {len(results)}."
        )

    print()
    print("Generating dissertation figures...")
    print()

    figure_01_encryption_throughput(
        results
    )

    figure_02_decryption_throughput(
        results
    )

    figure_03_encryption_execution_time(
        results
    )

    figure_04_decryption_execution_time(
        results
    )

    figure_05_encryption_cpu_per_byte(
        results
    )

    figure_06_decryption_cpu_per_byte(
        results
    )

    figure_07_encryption_variability(
        results
    )

    figure_08_decryption_variability(
        results
    )

    figure_09_encryption_memory(
        results
    )

    figure_10_decryption_memory(
        results
    )

    figure_11_encryption_speedup(
        results
    )

    figure_12_performance_heatmap(
        results
    )

    print()
    print("=" * 70)
    print("Dissertation figure generation complete.")
    print("=" * 70)

    print()
    print(
        "Total figures generated: 12"
    )

    print(
        f"Figures saved to: {GRAPHS_DIR}"
    )


# ============================================================
# Program entry point
# ============================================================

if __name__ == "__main__":
    main()