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

EXPECTED_ALGORITHMS = {
    "Ascon-AEAD128",
    "AES-GCM",
    "ChaCha20-Poly1305"
}

EXPECTED_DATA_SIZES = {
    1024,
    4096,
    16384,
    65536,
    262144,
    1048576
}

EXPECTED_OPERATIONS = {
    "encryption",
    "decryption"
}

EXPECTED_MEASUREMENTS = 10
EXPECTED_RESULTS = 36


# ============================================================
# Validation helpers
# ============================================================

def validate_file_exists():
    """Check that the benchmark results file exists."""

    if not os.path.isfile(RESULTS_FILE):
        raise FileNotFoundError(
            f"Benchmark results file not found: {RESULTS_FILE}"
        )


def load_results():
    """Load benchmark results from the CSV file."""

    with open(
        RESULTS_FILE,
        "r",
        newline="",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        results = list(reader)

    return results


def validate_result_count(results):
    """Verify the expected number of benchmark results."""

    if len(results) != EXPECTED_RESULTS:
        raise ValueError(
            f"Expected {EXPECTED_RESULTS} results, "
            f"but found {len(results)}."
        )


def validate_algorithms(results):
    """Verify that all expected algorithms are present."""

    algorithms = {
        result["algorithm"]
        for result in results
    }

    if algorithms != EXPECTED_ALGORITHMS:
        raise ValueError(
            f"Unexpected algorithms found: {algorithms}"
        )


def validate_data_sizes(results):
    """Verify that all expected data sizes are present."""

    data_sizes = {
        int(result["data_size_bytes"])
        for result in results
    }

    if data_sizes != EXPECTED_DATA_SIZES:
        raise ValueError(
            f"Unexpected data sizes found: {data_sizes}"
        )


def validate_operations(results):
    """Verify that encryption and decryption are present."""

    operations = {
        result["operation"]
        for result in results
    }

    if operations != EXPECTED_OPERATIONS:
        raise ValueError(
            f"Unexpected operations found: {operations}"
        )


def validate_measurements(results):
    """Verify measurement count and numerical values."""

    for result in results:

        measurements = [
            int(value)
            for value in result["measurements"].split(";")
        ]

        if len(measurements) != EXPECTED_MEASUREMENTS:
            raise ValueError(
                f"{result['algorithm']} "
                f"{result['data_size_bytes']} "
                f"{result['operation']} has "
                f"{len(measurements)} measurements."
            )

        if any(value <= 0 for value in measurements):
            raise ValueError(
                "Benchmark measurements must be positive."
            )


def validate_statistics(results):
    """
    Recalculate statistics from the raw measurements and
    compare them with the values stored in the CSV.
    """

    for result in results:

        measurements = [
            int(value)
            for value in result["measurements"].split(";")
        ]

        calculated_mean = statistics.mean(measurements)
        calculated_median = statistics.median(measurements)
        calculated_min = min(measurements)
        calculated_max = max(measurements)
        calculated_stdev = statistics.stdev(measurements)

        stored_mean = float(result["mean_ns"])
        stored_median = float(result["median_ns"])
        stored_min = int(result["min_ns"])
        stored_max = int(result["max_ns"])
        stored_stdev = float(result["stdev_ns"])

        if abs(calculated_mean - stored_mean) > 0.01:
            raise ValueError(
                f"Mean mismatch for "
                f"{result['algorithm']} "
                f"{result['data_size_bytes']} "
                f"{result['operation']}"
            )

        if abs(calculated_median - stored_median) > 0.01:
            raise ValueError(
                f"Median mismatch for "
                f"{result['algorithm']} "
                f"{result['data_size_bytes']} "
                f"{result['operation']}"
            )

        if calculated_min != stored_min:
            raise ValueError(
                f"Minimum mismatch for "
                f"{result['algorithm']} "
                f"{result['data_size_bytes']} "
                f"{result['operation']}"
            )

        if calculated_max != stored_max:
            raise ValueError(
                f"Maximum mismatch for "
                f"{result['algorithm']} "
                f"{result['data_size_bytes']} "
                f"{result['operation']}"
            )

        if abs(calculated_stdev - stored_stdev) > 0.01:
            raise ValueError(
                f"Standard deviation mismatch for "
                f"{result['algorithm']} "
                f"{result['data_size_bytes']} "
                f"{result['operation']}"
            )


# ============================================================
# Main validation
# ============================================================

def main():

    print("=" * 60)
    print("LightCryptBench Benchmark Dataset Validation")
    print("=" * 60)

    print()
    print(f"Results file: {RESULTS_FILE}")

    # --------------------------------------------------------
    # File validation
    # --------------------------------------------------------

    validate_file_exists()

    print()
    print("PASS: Results file exists.")

    # --------------------------------------------------------
    # Load results
    # --------------------------------------------------------

    results = load_results()

    print(
        f"PASS: CSV loaded successfully "
        f"({len(results)} rows)."
    )

    # --------------------------------------------------------
    # Validate structure
    # --------------------------------------------------------

    validate_result_count(results)

    print(
        f"PASS: Result count is {EXPECTED_RESULTS}."
    )

    validate_algorithms(results)

    print(
        "PASS: All three expected algorithms are present."
    )

    validate_data_sizes(results)

    print(
        "PASS: All six expected data sizes are present."
    )

    validate_operations(results)

    print(
        "PASS: Encryption and decryption results are present."
    )

    # --------------------------------------------------------
    # Validate measurements
    # --------------------------------------------------------

    validate_measurements(results)

    print(
        f"PASS: Every result contains "
        f"{EXPECTED_MEASUREMENTS} measurements."
    )

    # --------------------------------------------------------
    # Validate statistics
    # --------------------------------------------------------

    validate_statistics(results)

    print(
        "PASS: Stored statistics match the raw measurements."
    )

    # --------------------------------------------------------
    # Validation complete
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("Benchmark dataset validation complete.")
    print("=" * 60)

    print()
    print("SUCCESS: All validation checks passed.")


if __name__ == "__main__":
    main()


