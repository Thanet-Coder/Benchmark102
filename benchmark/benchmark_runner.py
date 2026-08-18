import os
import sys
import time
import statistics

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


# ============================================================
# Benchmark operations
# ============================================================

def benchmark_encryption(algorithm, key, data, associated_data):
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

    # Prepare a valid ciphertext for decryption
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

    return timings


# ============================================================
# Main benchmark
# ============================================================

def main():

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

            decryption_timings = benchmark_decryption(
                algorithm,
                key,
                data,
                associated_data
            )

            # ------------------------------------------------
            # Calculate statistics
            # ------------------------------------------------

            encryption_stats = calculate_statistics(
                encryption_timings
            )

            decryption_stats = calculate_statistics(
                decryption_timings
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
                f"  Mean:    "
                f"{encryption_stats['mean_ns']:,.0f} ns"
            )

            print(
                f"  Median:  "
                f"{encryption_stats['median_ns']:,.0f} ns"
            )

            print(
                f"  Minimum: "
                f"{encryption_stats['min_ns']:,.0f} ns"
            )

            print(
                f"  Maximum: "
                f"{encryption_stats['max_ns']:,.0f} ns"
            )

            print(
                f"  StdDev:  "
                f"{encryption_stats['stdev_ns']:,.0f} ns"
            )

            # ------------------------------------------------
            # Display decryption statistics
            # ------------------------------------------------

            print()
            print("Decryption statistics:")

            print(
                f"  Mean:    "
                f"{decryption_stats['mean_ns']:,.0f} ns"
            )

            print(
                f"  Median:  "
                f"{decryption_stats['median_ns']:,.0f} ns"
            )

            print(
                f"  Minimum: "
                f"{decryption_stats['min_ns']:,.0f} ns"
            )

            print(
                f"  Maximum: "
                f"{decryption_stats['max_ns']:,.0f} ns"
            )

            print(
                f"  StdDev:  "
                f"{decryption_stats['stdev_ns']:,.0f} ns"
            )

    print()
    print("=" * 60)
    print("Timing benchmark complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()