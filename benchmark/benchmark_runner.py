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

# CPU batching configuration.
#
# CPU time on Windows can have much coarser resolution than
# wall-clock timing. Very fast operations are therefore
# repeated until the batch lasts for approximately 250 ms.
#
# The CPU time for the completed batch is then divided by the
# number of operations to obtain average CPU time per operation.

CPU_BATCH_TARGET_NS = 250_000_000
CPU_BATCH_MAX_RUNS = 100_000

RESULTS_DIR = os.path.join(
    PROJECT_ROOT,
    "results"
)

RESULTS_FILE = os.path.join(
    RESULTS_DIR,
    "benchmark_results.csv"
)


# ============================================================
# Process information
# ============================================================

PROCESS = psutil.Process(os.getpid())


# ============================================================
# Helper functions
# ============================================================

def load_test_data(size):
    """
    Load deterministic benchmark data from the data directory.

    The test data files are generated separately by
    generate_test_data.py so that the experimental inputs
    remain fixed and reproducible.
    """

    filename_map = {
        1024: "test_1kb.bin",
        4096: "test_4kb.bin",
        16384: "test_16kb.bin",
        65536: "test_64kb.bin",
        262144: "test_256kb.bin",
        1048576: "test_1mb.bin"
    }

    if size not in filename_map:
        raise ValueError(
            f"No test data file configured for {size} bytes."
        )

    filename = os.path.join(
        PROJECT_ROOT,
        "data",
        filename_map[size]
    )

    if not os.path.exists(filename):
        raise FileNotFoundError(
            f"Test data file not found: {filename}"
        )

    with open(filename, "rb") as file:
        data = file.read()

    if len(data) != size:
        raise ValueError(
            f"Test data size mismatch: "
            f"expected {size} bytes, "
            f"got {len(data)} bytes."
        )

    return data


def get_nonce(algorithm):
    """
    Return a nonce of the correct size for the algorithm.
    """

    if algorithm.name == "Ascon-AEAD128":
        return bytes(16)

    if algorithm.name == "AES-GCM":
        return bytes(12)

    if algorithm.name == "ChaCha20-Poly1305":
        return bytes(12)

    raise ValueError(
        f"Unknown algorithm: {algorithm.name}"
    )


def get_memory_usage_mb():
    """
    Return the current process resident memory usage in MB.
    """

    memory_info = PROCESS.memory_info()

    return memory_info.rss / (1024 * 1024)


def measure_operation(operation):
    """
    Measure wall-clock execution time and process memory usage
    for one cryptographic operation.

    CPU time is deliberately measured separately using an
    adaptive batch so that very fast operations can be measured
    reliably despite the coarser process CPU timer.

    Returns:
        result:
            Result returned by the operation.

        elapsed_ns:
            Wall-clock execution time in nanoseconds.

        memory_before_mb:
            Process resident memory before the operation.

        memory_after_mb:
            Process resident memory after the operation.

        memory_difference_mb:
            Difference between memory after and before.
    """

    # --------------------------------------------------------
    # Record memory before operation
    # --------------------------------------------------------

    memory_before_mb = get_memory_usage_mb()

    # --------------------------------------------------------
    # Measure wall-clock execution time
    # --------------------------------------------------------

    start = time.perf_counter_ns()

    result = operation()

    end = time.perf_counter_ns()

    # --------------------------------------------------------
    # Record memory after operation
    # --------------------------------------------------------

    memory_after_mb = get_memory_usage_mb()

    # --------------------------------------------------------
    # Calculate measurements
    # --------------------------------------------------------

    elapsed_ns = end - start

    memory_difference_mb = (
        memory_after_mb - memory_before_mb
    )

    return (
        result,
        elapsed_ns,
        memory_before_mb,
        memory_after_mb,
        memory_difference_mb
    )


def measure_cpu_time_batched(operation):
    """
    Measure average process CPU time for one operation.

    The operation is repeated in increasingly large batches
    until the batch reaches the configured target duration.

    This reduces the effect of coarse CPU timer resolution for
    very fast cryptographic operations.

    Returns:
        average_cpu_time_ns:
            Average process CPU time per operation.

        batch_runs:
            Number of operations used in the final CPU batch.
    """

    batch_runs = 1

    while True:

        wall_start = time.perf_counter_ns()
        cpu_start = time.process_time_ns()

        for _ in range(batch_runs):
            operation()

        cpu_end = time.process_time_ns()
        wall_end = time.perf_counter_ns()

        batch_wall_ns = (
            wall_end - wall_start
        )

        batch_cpu_ns = (
            cpu_end - cpu_start
        )

        if (
            batch_wall_ns >= CPU_BATCH_TARGET_NS
            or batch_runs >= CPU_BATCH_MAX_RUNS
        ):

            average_cpu_time_ns = (
                batch_cpu_ns / batch_runs
            )

            return (
                average_cpu_time_ns,
                batch_runs
            )

        batch_runs *= 2

        if batch_runs > CPU_BATCH_MAX_RUNS:
            batch_runs = CPU_BATCH_MAX_RUNS


def calculate_statistics(timings):
    """
    Calculate basic statistics for timing measurements.
    """

    return {
        "mean_ns": statistics.mean(timings),
        "median_ns": statistics.median(timings),
        "min_ns": min(timings),
        "max_ns": max(timings),
        "stdev_ns": statistics.stdev(timings)
    }


def calculate_average(values):
    """
    Return the arithmetic mean of a collection.
    """

    if not values:
        return 0.0

    return statistics.mean(values)


def create_benchmark_result(
    algorithm,
    data_size_bytes,
    operation,
    timings,
    cpu_time_ns,
    cpu_batch_runs,
    memory_before_measurements,
    memory_after_measurements,
    memory_difference_measurements
):
    """
    Create a structured benchmark result.

    Timing measurements contain the ten recorded wall-clock
    observations.

    CPU time is measured separately using an adaptive batch.

    Memory values are calculated from the recorded timing runs.
    """

    statistics_result = calculate_statistics(
        timings
    )

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

        "cpu_time_ns": cpu_time_ns,
        "cpu_batch_runs": cpu_batch_runs,

        "memory_before_mb": calculate_average(
            memory_before_measurements
        ),

        "memory_after_mb": calculate_average(
            memory_after_measurements
        ),

        "memory_difference_mb": calculate_average(
            memory_difference_measurements
        )
    }


# ============================================================
# Benchmark operations
# ============================================================

def benchmark_encryption(
    algorithm,
    key,
    data,
    associated_data
):
    """
    Benchmark encryption for one algorithm and data size.

    Returns:
        timings
        average CPU time
        CPU batch size
        memory-before measurements
        memory-after measurements
        memory-difference measurements
    """

    timings = []

    memory_before_measurements = []
    memory_after_measurements = []
    memory_difference_measurements = []

    # --------------------------------------------------------
    # Warm-up runs
    # --------------------------------------------------------

    for _ in range(WARMUP_RUNS):

        nonce = get_nonce(
            algorithm
        )

        algorithm.encrypt(
            key,
            nonce,
            data,
            associated_data
        )

    # --------------------------------------------------------
    # Measured timing and memory runs
    # --------------------------------------------------------

    for _ in range(MEASUREMENT_RUNS):

        nonce = get_nonce(
            algorithm
        )

        (
            _,
            elapsed_ns,
            memory_before_mb,
            memory_after_mb,
            memory_difference_mb
        ) = measure_operation(
            lambda: algorithm.encrypt(
                key,
                nonce,
                data,
                associated_data
            )
        )

        timings.append(
            elapsed_ns
        )

        memory_before_measurements.append(
            memory_before_mb
        )

        memory_after_measurements.append(
            memory_after_mb
        )

        memory_difference_measurements.append(
            memory_difference_mb
        )

    # --------------------------------------------------------
    # Batched CPU-time measurement
    # --------------------------------------------------------

    cpu_nonce = get_nonce(
        algorithm
    )

    (
        cpu_time_ns,
        cpu_batch_runs
    ) = measure_cpu_time_batched(
        lambda: algorithm.encrypt(
            key,
            cpu_nonce,
            data,
            associated_data
        )
    )

    return (
        timings,
        cpu_time_ns,
        cpu_batch_runs,
        memory_before_measurements,
        memory_after_measurements,
        memory_difference_measurements
    )


def benchmark_decryption(
    algorithm,
    key,
    data,
    associated_data
):
    """
    Benchmark decryption for one algorithm and data size.

    Returns:
        timings
        average CPU time
        CPU batch size
        memory-before measurements
        memory-after measurements
        memory-difference measurements
    """

    timings = []

    memory_before_measurements = []
    memory_after_measurements = []
    memory_difference_measurements = []

    # --------------------------------------------------------
    # Prepare valid ciphertext
    # --------------------------------------------------------

    nonce = get_nonce(
        algorithm
    )

    ciphertext = algorithm.encrypt(
        key,
        nonce,
        data,
        associated_data
    )

    # --------------------------------------------------------
    # Warm-up runs
    # --------------------------------------------------------

    for _ in range(WARMUP_RUNS):

        algorithm.decrypt(
            key,
            nonce,
            ciphertext,
            associated_data
        )

    # --------------------------------------------------------
    # Measured timing and memory runs
    # --------------------------------------------------------

    for _ in range(MEASUREMENT_RUNS):

        (
            _,
            elapsed_ns,
            memory_before_mb,
            memory_after_mb,
            memory_difference_mb
        ) = measure_operation(
            lambda: algorithm.decrypt(
                key,
                nonce,
                ciphertext,
                associated_data
            )
        )

        timings.append(
            elapsed_ns
        )

        memory_before_measurements.append(
            memory_before_mb
        )

        memory_after_measurements.append(
            memory_after_mb
        )

        memory_difference_measurements.append(
            memory_difference_mb
        )

    # --------------------------------------------------------
    # Batched CPU-time measurement
    # --------------------------------------------------------

    (
        cpu_time_ns,
        cpu_batch_runs
    ) = measure_cpu_time_batched(
        lambda: algorithm.decrypt(
            key,
            nonce,
            ciphertext,
            associated_data
        )
    )

    return (
        timings,
        cpu_time_ns,
        cpu_batch_runs,
        memory_before_measurements,
        memory_after_measurements,
        memory_difference_measurements
    )


# ============================================================
# CSV export
# ============================================================

def export_results(results):
    """
    Export structured benchmark results to CSV.
    """

    os.makedirs(
        RESULTS_DIR,
        exist_ok=True
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
        "cpu_time_ns",
        "cpu_batch_runs",
        "memory_before_mb",
        "memory_after_mb",
        "memory_difference_mb"
    ]

    with open(
        RESULTS_FILE,
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

            row = result.copy()

            row["measurements"] = ";".join(
                str(value)
                for value in result["measurements"]
            )

            writer.writerow(
                row
            )

    print()
    print(
        f"Results exported to: {RESULTS_FILE}"
    )


# ============================================================
# Main benchmark
# ============================================================

def main():

    # Master collection for all benchmark results
    all_results = []

    print("=" * 60)
    print("LightCryptBench Timing Benchmark")
    print("=" * 60)

    print()
    print(
        f"Warm-up runs per test:      "
        f"{WARMUP_RUNS}"
    )

    print(
        f"Recorded runs per test:     "
        f"{MEASUREMENT_RUNS}"
    )

    print(
        "Warm-up results are discarded."
    )

    print(
        "CPU time is measured separately "
        "using adaptive batching."
    )

    print(
        f"CPU batch target:           "
        f"{CPU_BATCH_TARGET_NS / 1_000_000:.0f} ms"
    )

    algorithms = [
        AsconAEAD128(),
        AESGCM(),
        ChaCha20Poly1305()
    ]

    for algorithm in algorithms:

        print()
        print(
            f"Algorithm: {algorithm.name}"
        )

        print("=" * 60)

        key = algorithm.generate_key()

        for size in DATA_SIZES:

            print()
            print(
                f"Data size: {size:,} bytes"
            )

            data = load_test_data(
                size
            )

            associated_data = b""

            # ------------------------------------------------
            # Encryption benchmark
            # ------------------------------------------------

            (
                encryption_timings,
                encryption_cpu_time,
                encryption_cpu_batch_runs,
                encryption_memory_before,
                encryption_memory_after,
                encryption_memory_difference
            ) = benchmark_encryption(
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
                decryption_cpu_time,
                decryption_cpu_batch_runs,
                decryption_memory_before,
                decryption_memory_after,
                decryption_memory_difference
            ) = benchmark_decryption(
                algorithm,
                key,
                data,
                associated_data
            )

            # ------------------------------------------------
            # Create structured results
            # ------------------------------------------------

            encryption_result = create_benchmark_result(
                algorithm,
                size,
                "encryption",
                encryption_timings,
                encryption_cpu_time,
                encryption_cpu_batch_runs,
                encryption_memory_before,
                encryption_memory_after,
                encryption_memory_difference
            )

            decryption_result = create_benchmark_result(
                algorithm,
                size,
                "decryption",
                decryption_timings,
                decryption_cpu_time,
                decryption_cpu_batch_runs,
                decryption_memory_before,
                decryption_memory_after,
                decryption_memory_difference
            )

            # ------------------------------------------------
            # Add results to master collection
            # ------------------------------------------------

            all_results.append(
                encryption_result
            )

            all_results.append(
                decryption_result
            )

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
                f"  Mean:       "
                f"{encryption_result['mean_ns']:,.0f} ns"
            )

            print(
                f"  Median:     "
                f"{encryption_result['median_ns']:,.0f} ns"
            )

            print(
                f"  Minimum:    "
                f"{encryption_result['min_ns']:,.0f} ns"
            )

            print(
                f"  Maximum:    "
                f"{encryption_result['max_ns']:,.0f} ns"
            )

            print(
                f"  StdDev:     "
                f"{encryption_result['stdev_ns']:,.0f} ns"
            )

            print(
                f"  CPU time:   "
                f"{encryption_result['cpu_time_ns']:,.0f} ns"
            )

            print(
                f"  CPU batch:  "
                f"{encryption_result['cpu_batch_runs']:,} runs"
            )

            print(
                f"  Memory:     "
                f"{encryption_result['memory_difference_mb']:.2f} MB"
            )

            # ------------------------------------------------
            # Display decryption statistics
            # ------------------------------------------------

            print()
            print("Decryption statistics:")

            print(
                f"  Mean:       "
                f"{decryption_result['mean_ns']:,.0f} ns"
            )

            print(
                f"  Median:     "
                f"{decryption_result['median_ns']:,.0f} ns"
            )

            print(
                f"  Minimum:    "
                f"{decryption_result['min_ns']:,.0f} ns"
            )

            print(
                f"  Maximum:    "
                f"{decryption_result['max_ns']:,.0f} ns"
            )

            print(
                f"  StdDev:     "
                f"{decryption_result['stdev_ns']:,.0f} ns"
            )

            print(
                f"  CPU time:   "
                f"{decryption_result['cpu_time_ns']:,.0f} ns"
            )

            print(
                f"  CPU batch:  "
                f"{decryption_result['cpu_batch_runs']:,} runs"
            )

            print(
                f"  Memory:     "
                f"{decryption_result['memory_difference_mb']:.2f} MB"
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
    # Export results
    # --------------------------------------------------------

    export_results(
        all_results
    )


# ============================================================
# Program entry point
# ============================================================

if __name__ == "__main__":
    main()