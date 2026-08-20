import csv
import os


# ============================================================
# Configuration
# ============================================================

RESULTS_FILE = os.path.join(
    "results",
    "benchmark_results.csv"
)


# ============================================================
# Helper functions
# ============================================================

def load_results():
    """Load benchmark results from the CSV file."""

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
    Calculate throughput in megabytes per second.

    Args:
        data_size_bytes: Size of the processed data.
        mean_ns: Mean execution time in nanoseconds.

    Returns:
        Throughput in MB/s.
    """

    seconds = mean_ns / 1_000_000_000

    megabytes = data_size_bytes / 1_000_000

    return megabytes / seconds


def analyse_result(result):
    """
    Add calculated throughput to one benchmark result.
    """

    data_size = int(
        result["data_size_bytes"]
    )

    mean_ns = float(
        result["mean_ns"]
    )

    throughput = calculate_throughput_mb_s(
        data_size,
        mean_ns
    )

    return {
        "algorithm": result["algorithm"],
        "data_size_bytes": data_size,
        "operation": result["operation"],
        "mean_ns": mean_ns,
        "median_ns": float(result["median_ns"]),
        "min_ns": int(result["min_ns"]),
        "max_ns": int(result["max_ns"]),
        "stdev_ns": float(result["stdev_ns"]),
        "throughput_mb_s": throughput
    }


# ============================================================
# Main analysis
# ============================================================

def main():

    print("=" * 60)
    print("LightCryptBench Benchmark Analysis")
    print("=" * 60)

    # --------------------------------------------------------
    # Load benchmark results
    # --------------------------------------------------------

    results = load_results()

    print()
    print(
        f"Loaded {len(results)} benchmark results."
    )

    # --------------------------------------------------------
    # Analyse results
    # --------------------------------------------------------

    analysed_results = []

    for result in results:

        analysed_result = analyse_result(
            result
        )

        analysed_results.append(
            analysed_result
        )

    # --------------------------------------------------------
    # Display throughput results
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("Throughput Analysis")
    print("=" * 60)

    current_algorithm = None
    current_size = None

    for result in analysed_results:

        algorithm = result["algorithm"]
        data_size = result["data_size_bytes"]

        if algorithm != current_algorithm:

            print()
            print(
                f"Algorithm: {algorithm}"
            )
            print("-" * 60)

            current_algorithm = algorithm
            current_size = None

        if data_size != current_size:

            print()
            print(
                f"Data size: {data_size:,} bytes"
            )

            current_size = data_size

        print(
            f"  {result['operation'].capitalize():12}"
            f" Mean: {result['mean_ns']:,.0f} ns"
            f" | Throughput: "
            f"{result['throughput_mb_s']:,.2f} MB/s"
        )

    # --------------------------------------------------------
    # Analysis complete
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("Benchmark analysis complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
