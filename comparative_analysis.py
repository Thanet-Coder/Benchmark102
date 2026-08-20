import csv
import os
import statistics


# ============================================================
# Configuration
# ============================================================

RESULTS_FILE = os.path.join(
    "results",
    "benchmark_results.csv"
)


EXPECTED_ALGORITHMS = [
    "Ascon-AEAD128",
    "AES-GCM",
    "ChaCha20-Poly1305"
]


EXPECTED_DATA_SIZES = [
    1024,
    4096,
    16384,
    65536,
    262144,
    1048576
]


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
    Calculate throughput in decimal megabytes per second.

    MB = 1,000,000 bytes.
    """

    seconds = mean_ns / 1_000_000_000
    megabytes = data_size_bytes / 1_000_000

    return megabytes / seconds


def calculate_cpu_time_per_byte(
    cpu_time_ns,
    data_size_bytes
):
    """
    Calculate CPU time consumed per byte.

    Returns nanoseconds of CPU time per byte.
    """

    return cpu_time_ns / data_size_bytes


def calculate_coefficient_of_variation(
    mean_ns,
    stdev_ns
):
    """
    Calculate coefficient of variation as a percentage.

    This indicates the relative variability of the
    recorded timing measurements.
    """

    if mean_ns == 0:
        return 0.0

    return (
        stdev_ns / mean_ns
    ) * 100


def convert_result(result):
    """
    Convert CSV values into appropriate Python types
    and calculate derived benchmark metrics.
    """

    measurements = [
        float(value)
        for value in result["measurements"].split(";")
    ]

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

    throughput = calculate_throughput_mb_s(
        data_size,
        mean_ns
    )

    cpu_time_per_byte = calculate_cpu_time_per_byte(
        cpu_time_ns,
        data_size
    )

    coefficient_of_variation = (
        calculate_coefficient_of_variation(
            mean_ns,
            stdev_ns
        )
    )

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

        "throughput_mb_s": throughput,

        "cpu_time_per_byte_ns": (
            cpu_time_per_byte
        ),

        "coefficient_of_variation_percent": (
            coefficient_of_variation
        )
    }


def find_result(
    results,
    algorithm,
    data_size,
    operation
):
    """
    Find one benchmark result.
    """

    for result in results:

        if (
            result["algorithm"] == algorithm
            and result["data_size_bytes"] == data_size
            and result["operation"] == operation
        ):
            return result

    raise ValueError(
        f"Result not found: "
        f"{algorithm}, "
        f"{data_size}, "
        f"{operation}"
    )


def calculate_speedup(
    reference_time,
    comparison_time
):
    """
    Calculate how many times faster the comparison
    algorithm is than the reference algorithm.
    """

    return reference_time / comparison_time


# ============================================================
# Comparative analysis
# ============================================================

def print_throughput_comparison(
    results,
    operation
):
    """
    Display throughput for all algorithms at each
    data size.
    """

    print()
    print("=" * 60)
    print(
        f"{operation.capitalize()} Throughput Comparison"
    )
    print("=" * 60)

    for size in EXPECTED_DATA_SIZES:

        print()
        print(
            f"Data size: {size:,} bytes"
        )
        print("-" * 60)

        for algorithm in EXPECTED_ALGORITHMS:

            result = find_result(
                results,
                algorithm,
                size,
                operation
            )

            print(
                f"{algorithm:20}"
                f" {result['throughput_mb_s']:12.2f} MB/s"
            )


def print_execution_time_comparison(
    results,
    operation
):
    """
    Display mean wall-clock execution time
    for all algorithms.
    """

    print()
    print("=" * 60)
    print(
        f"{operation.capitalize()} Execution Time Comparison"
    )
    print("=" * 60)

    for size in EXPECTED_DATA_SIZES:

        print()
        print(
            f"Data size: {size:,} bytes"
        )
        print("-" * 60)

        for algorithm in EXPECTED_ALGORITHMS:

            result = find_result(
                results,
                algorithm,
                size,
                operation
            )

            print(
                f"{algorithm:20}"
                f" {result['mean_ns']:15,.0f} ns"
            )


def print_cpu_time_comparison(
    results,
    operation
):
    """
    Display CPU time per cryptographic operation.

    CPU time is measured separately using adaptive
    batching in the benchmark runner.
    """

    print()
    print("=" * 60)
    print(
        f"{operation.capitalize()} CPU Time Comparison"
    )
    print("=" * 60)

    for size in EXPECTED_DATA_SIZES:

        print()
        print(
            f"Data size: {size:,} bytes"
        )
        print("-" * 60)

        for algorithm in EXPECTED_ALGORITHMS:

            result = find_result(
                results,
                algorithm,
                size,
                operation
            )

            print(
                f"{algorithm:20}"
                f" {result['cpu_time_ns']:15,.0f} ns"
                f" | batch: "
                f"{result['cpu_batch_runs']:,}"
            )


def print_cpu_efficiency_comparison(
    results,
    operation
):
    """
    Display CPU time consumed per byte processed.
    """

    print()
    print("=" * 60)
    print(
        f"{operation.capitalize()} CPU Time Per Byte"
    )
    print("=" * 60)

    for size in EXPECTED_DATA_SIZES:

        print()
        print(
            f"Data size: {size:,} bytes"
        )
        print("-" * 60)

        for algorithm in EXPECTED_ALGORITHMS:

            result = find_result(
                results,
                algorithm,
                size,
                operation
            )

            print(
                f"{algorithm:20}"
                f" "
                f"{result['cpu_time_per_byte_ns']:12.4f}"
                f" ns/byte"
            )


def print_variability_analysis(
    results,
    operation
):
    """
    Display timing variability using the coefficient
    of variation.

    Lower percentages indicate more consistent timing.
    """

    print()
    print("=" * 60)
    print(
        f"{operation.capitalize()} Timing Variability"
    )
    print("=" * 60)

    for size in EXPECTED_DATA_SIZES:

        print()
        print(
            f"Data size: {size:,} bytes"
        )
        print("-" * 60)

        for algorithm in EXPECTED_ALGORITHMS:

            result = find_result(
                results,
                algorithm,
                size,
                operation
            )

            print(
                f"{algorithm:20}"
                f" "
                f"{result['coefficient_of_variation_percent']:10.2f}%"
            )


def print_memory_comparison(
    results,
    operation
):
    """
    Display average observed memory difference
    for each benchmark result.
    """

    print()
    print("=" * 60)
    print(
        f"{operation.capitalize()} Memory Comparison"
    )
    print("=" * 60)

    for size in EXPECTED_DATA_SIZES:

        print()
        print(
            f"Data size: {size:,} bytes"
        )
        print("-" * 60)

        for algorithm in EXPECTED_ALGORITHMS:

            result = find_result(
                results,
                algorithm,
                size,
                operation
            )

            print(
                f"{algorithm:20}"
                f" "
                f"{result['memory_difference_mb']:10.4f} MB"
            )


def print_speedup_analysis(
    results,
    operation
):
    """
    Compare AES-GCM and ChaCha20-Poly1305 against
    Ascon-AEAD128 using mean wall-clock execution time.
    """

    print()
    print("=" * 60)
    print(
        f"{operation.capitalize()} Speedup "
        f"Relative to Ascon-AEAD128"
    )
    print("=" * 60)

    for size in EXPECTED_DATA_SIZES:

        ascon = find_result(
            results,
            "Ascon-AEAD128",
            size,
            operation
        )

        aes = find_result(
            results,
            "AES-GCM",
            size,
            operation
        )

        chacha = find_result(
            results,
            "ChaCha20-Poly1305",
            size,
            operation
        )

        aes_speedup = calculate_speedup(
            ascon["mean_ns"],
            aes["mean_ns"]
        )

        chacha_speedup = calculate_speedup(
            ascon["mean_ns"],
            chacha["mean_ns"]
        )

        print()
        print(
            f"Data size: {size:,} bytes"
        )

        print(
            f"  AES-GCM:            "
            f"{aes_speedup:,.2f}x faster"
        )

        print(
            f"  ChaCha20-Poly1305:  "
            f"{chacha_speedup:,.2f}x faster"
        )


def print_algorithm_rankings(
    results,
    operation
):
    """
    Rank algorithms by throughput for every data size.

    Higher throughput receives the better ranking.
    """

    print()
    print("=" * 60)
    print(
        f"{operation.capitalize()} Throughput Rankings"
    )
    print("=" * 60)

    for size in EXPECTED_DATA_SIZES:

        size_results = [
            find_result(
                results,
                algorithm,
                size,
                operation
            )
            for algorithm in EXPECTED_ALGORITHMS
        ]

        ranked_results = sorted(
            size_results,
            key=lambda item: item["throughput_mb_s"],
            reverse=True
        )

        print()
        print(
            f"Data size: {size:,} bytes"
        )
        print("-" * 60)

        for position, result in enumerate(
            ranked_results,
            start=1
        ):

            print(
                f"{position}. "
                f"{result['algorithm']:20}"
                f" "
                f"{result['throughput_mb_s']:12.2f} MB/s"
            )


def print_algorithm_summary(
    results
):
    """
    Display final summary statistics for each algorithm.
    """

    print()
    print("=" * 60)
    print("Algorithm Summary")
    print("=" * 60)

    for algorithm in EXPECTED_ALGORITHMS:

        algorithm_results = [
            result
            for result in results
            if result["algorithm"] == algorithm
        ]

        encryption_results = [
            result
            for result in algorithm_results
            if result["operation"] == "encryption"
        ]

        decryption_results = [
            result
            for result in algorithm_results
            if result["operation"] == "decryption"
        ]

        encryption_throughputs = [
            result["throughput_mb_s"]
            for result in encryption_results
        ]

        decryption_throughputs = [
            result["throughput_mb_s"]
            for result in decryption_results
        ]

        encryption_cpu_time_per_byte = [
            result["cpu_time_per_byte_ns"]
            for result in encryption_results
        ]

        decryption_cpu_time_per_byte = [
            result["cpu_time_per_byte_ns"]
            for result in decryption_results
        ]

        encryption_variability = [
            result[
                "coefficient_of_variation_percent"
            ]
            for result in encryption_results
        ]

        decryption_variability = [
            result[
                "coefficient_of_variation_percent"
            ]
            for result in decryption_results
        ]

        encryption_memory = [
            result["memory_difference_mb"]
            for result in encryption_results
        ]

        decryption_memory = [
            result["memory_difference_mb"]
            for result in decryption_results
        ]

        print()
        print(
            f"Algorithm: {algorithm}"
        )
        print("-" * 60)

        print(
            f"Encryption average throughput: "
            f"{statistics.mean(encryption_throughputs):.2f} MB/s"
        )

        print(
            f"Decryption average throughput: "
            f"{statistics.mean(decryption_throughputs):.2f} MB/s"
        )

        print(
            f"Encryption average CPU time/byte: "
            f"{statistics.mean(encryption_cpu_time_per_byte):.4f} ns"
        )

        print(
            f"Decryption average CPU time/byte: "
            f"{statistics.mean(decryption_cpu_time_per_byte):.4f} ns"
        )

        print(
            f"Encryption average timing CV: "
            f"{statistics.mean(encryption_variability):.2f}%"
        )

        print(
            f"Decryption average timing CV: "
            f"{statistics.mean(decryption_variability):.2f}%"
        )

        print(
            f"Encryption average memory difference: "
            f"{statistics.mean(encryption_memory):.4f} MB"
        )

        print(
            f"Decryption average memory difference: "
            f"{statistics.mean(decryption_memory):.4f} MB"
        )


# ============================================================
# Main
# ============================================================

def main():

    print("=" * 60)
    print("LightCryptBench Final Comparative Analysis")
    print("=" * 60)

    print()
    print(
        f"Loading results from: {RESULTS_FILE}"
    )

    raw_results = load_results()

    results = [
        convert_result(result)
        for result in raw_results
    ]

    print(
        f"Loaded {len(results)} benchmark results."
    )

    # --------------------------------------------------------
    # Throughput comparisons
    # --------------------------------------------------------

    print_throughput_comparison(
        results,
        "encryption"
    )

    print_throughput_comparison(
        results,
        "decryption"
    )

    # --------------------------------------------------------
    # Wall-clock execution-time comparisons
    # --------------------------------------------------------

    print_execution_time_comparison(
        results,
        "encryption"
    )

    print_execution_time_comparison(
        results,
        "decryption"
    )

    # --------------------------------------------------------
    # CPU-time comparisons
    # --------------------------------------------------------

    print_cpu_time_comparison(
        results,
        "encryption"
    )

    print_cpu_time_comparison(
        results,
        "decryption"
    )

    # --------------------------------------------------------
    # CPU efficiency comparisons
    # --------------------------------------------------------

    print_cpu_efficiency_comparison(
        results,
        "encryption"
    )

    print_cpu_efficiency_comparison(
        results,
        "decryption"
    )

    # --------------------------------------------------------
    # Timing variability
    # --------------------------------------------------------

    print_variability_analysis(
        results,
        "encryption"
    )

    print_variability_analysis(
        results,
        "decryption"
    )

    # --------------------------------------------------------
    # Memory comparisons
    # --------------------------------------------------------

    print_memory_comparison(
        results,
        "encryption"
    )

    print_memory_comparison(
        results,
        "decryption"
    )

    # --------------------------------------------------------
    # Speedup analysis
    # --------------------------------------------------------

    print_speedup_analysis(
        results,
        "encryption"
    )

    print_speedup_analysis(
        results,
        "decryption"
    )

    # --------------------------------------------------------
    # Throughput rankings
    # --------------------------------------------------------

    print_algorithm_rankings(
        results,
        "encryption"
    )

    print_algorithm_rankings(
        results,
        "decryption"
    )

    # --------------------------------------------------------
    # Algorithm summaries
    # --------------------------------------------------------

    print_algorithm_summary(
        results
    )

    # --------------------------------------------------------
    # Complete
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("Final comparative analysis complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()