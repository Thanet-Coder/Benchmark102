import os
import sys
import time
import statistics
import csv
import psutil

# Allow Python to find the project modules
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, PROJECT_ROOT)

from ascon_algorithm import AsconAEAD128
from aes_gcm_algorithm import AESGCM
from chacha20_poly1305_algorithm import ChaCha20Poly1305


# ============================================================
# Benchmark configuration
# ============================================================

DATA_SIZES = [
    1024,        # 1 KB
    4096,        # 4 KB
    16384,       # 16 KB
    65536,       # 64 KB
    262144,      # 256 KB
    1048576      # 1 MB
]

WARMUP_RUNS = 3
MEASUREMENT_RUNS = 10

# Number of operations used for CPU utilisation measurement.
# A batch is used because individual cryptographic operations
# can be too short for reliable CPU percentage measurement.
CPU_MEASUREMENT_RUNS = 100


# ============================================================
# Helper functions
# ============================================================

def generate_test_data(size):
    """Generate deterministic test data of the requested size."""

    return bytes(
        (i % 256 for i in range(size))
    )


def get_nonce(algorithm):
    """Return a nonce of the correct size for the algorithm."""

    if algorithm.name == "Ascon-AEAD128":
        return bytes(16)

    if algorithm.name == "AES-GCM":
        return bytes(12)

    if algorithm.name == "ChaCha20-Poly1305":
        return bytes(12)

    raise ValueError(f"Unknown algorithm: {algorithm.name}")


def measure_operation(operation):
    """
    Measure the execution time of one cryptographic operation.

    Returns:
        result: Result returned by the operation.
        elapsed_ns: Execution time in nanoseconds.
    """

    start = time.perf_counter_ns()

    result = operation()

    end = time.perf_counter_ns()

    elapsed_ns = end - start

    return result, elapsed_ns


def calculate_statistics(timings):
    """
    Calculate basic statistics for a collection of timing measurements.

    Args:
        timings: List of execution times in nanoseconds.

    Returns:
        Dictionary containing timing statistics.
    """

    return {
        "mean_ns": statistics.mean(timings),
        "median_ns": statistics.median(timings),
        "min_ns": min(timings),
        "max_ns": max(timings),
        "stdev_ns": statistics.stdev(timings)
    }


def create_benchmark_result(
    algorithm,
    data_size_bytes,
    operation,
    timings,
    cpu_percent
):
    """
    Create a structured benchmark result.

    Args:
        algorithm: Cryptographic algorithm object.
        data_size_bytes: Size of the test data in bytes.
        operation: Encryption or decryption.
        timings: List of execution times in nanoseconds.
        cpu_percent: Process CPU utilisation percentage.

    Returns:
        Dictionary containing the benchmark result.
    """

    statistics_result = calculate_statistics(timings)

    return {
        "algorithm": algorithm.name,
        "data_size_bytes": data_size_bytes,
        "operation": operation,
        "measurements": timings,
        "mean_ns": statistics_result["mean_ns"],
        "median_ns": statistics_result["median_ns"],
        "min_ns": statistics_result["min_ns"],
        "max_ns": statistics_result["max_ns"],
        "stdev_ns": statistics_result["stdev_ns"],
        "cpu_percent": cpu_percent
    }


# ============================================================
# CPU measurement
# ============================================================

def measure_cpu_encryption(
    algorithm,
    key,
    data,
    associated_data
):
    """
    Measure process CPU utilisation during repeated encryption.

    A batch of operations is used because an individual encryption
    operation may be too short to produce a meaningful CPU reading.

    Returns:
        Average process CPU utilisation percentage.
    """

    process = psutil.Process()

    # Establish the initial CPU measurement.
    process.cpu_percent(interval=None)

    for _ in range(CPU_MEASUREMENT_RUNS):

        nonce = get_nonce(algorithm)

        algorithm.encrypt(
            key,
            nonce,
            data,
            associated_data
        )

    # Measure CPU utilisation over a short sampling interval.
    cpu_percent = process.cpu_percent(interval=0.1)

    return cpu_percent


def measure_cpu_decryption(
    algorithm,
    key,
    nonce,
    ciphertext,
    associated_data
):
    """
    Measure process CPU utilisation during repeated decryption.

    A batch of operations is used because an individual decryption
    operation may be too short to produce a meaningful CPU reading.

    Returns:
        Average process CPU utilisation percentage.
    """

    process = psutil.Process()

    # Establish the initial CPU measurement.
    process.cpu_percent(interval=None)

    for _ in range(CPU_MEASUREMENT_RUNS):

        algorithm.decrypt(
            key,
            nonce,
            ciphertext,
            associated_data
        )

    # Measure CPU utilisation over a short sampling interval.
    cpu_percent = process.cpu_percent(interval=0.1)

    return cpu_percent


# ============================================================
# Benchmark operations
# ============================================================

def benchmark_encryption(
    algorithm,
    key,
    data,
    associated_data
):
    """Benchmark encryption for one algorithm and data size."""

    timings = []

    # Warm-up runs
    for _ in range(WARMUP_RUNS):

        nonce = get_nonce(algorithm)

        algorithm.encrypt(
            key,
            nonce,
            data,
            associated_data
        )

    # Measured runs
    for _ in range(MEASUREMENT_RUNS):

        nonce = get_nonce(algorithm)

        _, elapsed_ns = measure_operation(
            lambda: algorithm.encrypt(
                key,
                nonce,
                data,
                associated_data
            )
        )

        timings.append(elapsed_ns)

    return timings


def benchmark_decryption(
    algorithm,
    key,
    data,
    associated_data
):
    """Benchmark decryption for one algorithm and data size."""

    timings = []

    # Prepare a valid ciphertext for decryption.
    nonce = get_nonce(algorithm)

    ciphertext = algorithm.encrypt(
        key,
        nonce,
        data,
        associated_data
    )

    # Warm-up runs
    for _ in range(WARMUP_RUNS):

        algorithm.decrypt(
            key,
            nonce,
            ciphertext,
            associated_data
        )

    # Measured runs
    for _ in range(MEASUREMENT_RUNS):

        _, elapsed_ns = measure_operation(
            lambda: algorithm.decrypt(
                key,
                nonce,
                ciphertext,
                associated_data
            )
        )

        timings.append(elapsed_ns)

    return timings, nonce, ciphertext


# ============================================================
# CSV export
# ============================================================

def export_results_to_csv(results):
    """
    Export structured benchmark results to CSV.

    The measurements list is stored as a semicolon-separated
    string so that each benchmark result remains one CSV row.
    """

    results_directory = os.path.join(
        PROJECT_ROOT,
        "results"
    )

    os.makedirs(
        results_directory,
        exist_ok=True
    )

    output_file = os.path.join(
        results_directory,
        "benchmark_results.csv"
    )

    fieldnames = [
        "algorithm",
        "data_size_bytes",
        "operation",
        "measurements",
        "mean_ns",
        "median_ns",
        "min_ns",
        "max_ns",
        "stdev_ns",
        "cpu_percent"
    ]

    with open(
        output_file,
        "w",
        newline="",
        encoding="utf-8"
    ) as csv_file:

        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        for result in results:

            row = {
                "algorithm": result["algorithm"],
                "data_size_bytes": result["data_size_bytes"],
                "operation": result["operation"],
                "measurements": ";".join(
                    str(value)
                    for value in result["measurements"]
                ),
                "mean_ns": result["mean_ns"],
                "median_ns": result["median_ns"],
                "min_ns": result["min_ns"],
                "max_ns": result["max_ns"],
                "stdev_ns": result["stdev_ns"],
                "cpu_percent": result["cpu_percent"]
            }

            writer.writerow(row)

    return output_file


# ============================================================
# Main benchmark
# ============================================================

def main():

    # Master collection for all benchmark results.
    all_results = []

    print("=" * 60)
    print("LightCryptBench Timing Benchmark")
    print("=" * 60)

    algorithms = [
        AsconAEAD128(),
        AESGCM(),
        ChaCha20Poly1305()
    ]

    for algorithm in algorithms:

        print()
        print(f"Algorithm: {algorithm.name}")
        print("=" * 60)

        key = algorithm.generate_key()

        for size in DATA_SIZES:

            print()
            print(f"Data size: {size:,} bytes")

            data = generate_test_data(size)

            associated_data = b""

            # ------------------------------------------------
            # Encryption benchmark
            # ------------------------------------------------

            encryption_timings = benchmark_encryption(
                algorithm,
                key,
                data,
                associated_data
            )

            # ------------------------------------------------
            # Decryption benchmark
            # ------------------------------------------------

            (
                decryption_timings,
                decryption_nonce,
                decryption_ciphertext
            ) = benchmark_decryption(
                algorithm,
                key,
                data,
                associated_data
            )

            # ------------------------------------------------
            # CPU measurement
            # ------------------------------------------------

            encryption_cpu = measure_cpu_encryption(
                algorithm,
                key,
                data,
                associated_data
            )

            decryption_cpu = measure_cpu_decryption(
                algorithm,
                key,
                decryption_nonce,
                decryption_ciphertext,
                associated_data
            )

            # ------------------------------------------------
            # Create structured benchmark results
            # ------------------------------------------------

            encryption_result = create_benchmark_result(
                algorithm,
                size,
                "encryption",
                encryption_timings,
                encryption_cpu
            )

            decryption_result = create_benchmark_result(
                algorithm,
                size,
                "decryption",
                decryption_timings,
                decryption_cpu
            )

            # ------------------------------------------------
            # Add results to master collection
            # ------------------------------------------------

            all_results.append(encryption_result)
            all_results.append(decryption_result)

            # ------------------------------------------------
            # Display measurement counts
            # ------------------------------------------------

            print(
                f"Encryption measurements: "
                f"{len(encryption_timings)}"
            )

            print(
                f"Decryption measurements: "
                f"{len(decryption_timings)}"
            )

            # ------------------------------------------------
            # Display encryption statistics
            # ------------------------------------------------

            print()
            print("Encryption statistics:")

            print(
                f"  Mean:    "
                f"{encryption_result['mean_ns']:,.0f} ns"
            )

            print(
                f"  Median:  "
                f"{encryption_result['median_ns']:,.0f} ns"
            )

            print(
                f"  Minimum: "
                f"{encryption_result['min_ns']:,.0f} ns"
            )

            print(
                f"  Maximum: "
                f"{encryption_result['max_ns']:,.0f} ns"
            )

            print(
                f"  StdDev:  "
                f"{encryption_result['stdev_ns']:,.0f} ns"
            )

            print(
                f"  CPU:     "
                f"{encryption_result['cpu_percent']:.2f}%"
            )

            # ------------------------------------------------
            # Display decryption statistics
            # ------------------------------------------------

            print()
            print("Decryption statistics:")

            print(
                f"  Mean:    "
                f"{decryption_result['mean_ns']:,.0f} ns"
            )

            print(
                f"  Median:  "
                f"{decryption_result['median_ns']:,.0f} ns"
            )

            print(
                f"  Minimum: "
                f"{decryption_result['min_ns']:,.0f} ns"
            )

            print(
                f"  Maximum: "
                f"{decryption_result['max_ns']:,.0f} ns"
            )

            print(
                f"  StdDev:  "
                f"{decryption_result['stdev_ns']:,.0f} ns"
            )

            print(
                f"  CPU:     "
                f"{decryption_result['cpu_percent']:.2f}%"
            )

    # ========================================================
    # Benchmark complete
    # ========================================================

    print()
    print("=" * 60)
    print("Timing benchmark complete.")
    print("=" * 60)

    print()
    print(
        f"Total benchmark results collected: "
        f"{len(all_results)}"
    )

    # --------------------------------------------------------
    # Export structured results
    # --------------------------------------------------------

    output_file = export_results_to_csv(
        all_results
    )

    print()
    print(
        f"Results exported to: {output_file}"
    )


# ============================================================
# Program entry point
# ============================================================

if __name__ == "__main__":
    main()