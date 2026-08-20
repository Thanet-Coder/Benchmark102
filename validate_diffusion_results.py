import csv
import os


# ============================================================
# Configuration
# ============================================================

RESULTS_FILE = os.path.join(
    "results",
    "diffusion_results.csv"
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


EXPECTED_EXPERIMENT_TYPES = [
    "plaintext_bit_flip",
    "key_bit_flip"
]


EXPECTED_TRIALS_PER_CONDITION = 32

EXPECTED_TAG_BITS = 128


# ============================================================
# Helper functions
# ============================================================

def load_results():
    """
    Load diffusion results from the CSV file.
    """

    with open(
        RESULTS_FILE,
        "r",
        newline="",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        return list(reader)


def calculate_percent(
    changed_bits,
    total_bits
):
    """
    Calculate percentage of changed bits.
    """

    if total_bits <= 0:
        raise ValueError(
            "Total bit count must be positive."
        )

    return (
        changed_bits / total_bits
    ) * 100


def validate_expected_count(
    results
):
    """
    Confirm the total number of observations.
    """

    expected_count = (
        len(EXPECTED_ALGORITHMS)
        * len(EXPECTED_DATA_SIZES)
        * len(EXPECTED_EXPERIMENT_TYPES)
        * EXPECTED_TRIALS_PER_CONDITION
    )

    if len(results) != expected_count:
        raise AssertionError(
            f"Expected {expected_count} rows, "
            f"but found {len(results)}."
        )

    print(
        f"PASS: Result count is {expected_count:,}."
    )


def validate_algorithms(
    results
):
    """
    Confirm that all expected algorithms are present.
    """

    algorithms = {
        result["algorithm"]
        for result in results
    }

    if algorithms != set(
        EXPECTED_ALGORITHMS
    ):
        raise AssertionError(
            f"Unexpected algorithm set: "
            f"{algorithms}"
        )

    print(
        "PASS: All three expected algorithms are present."
    )


def validate_data_sizes(
    results
):
    """
    Confirm that all six expected data sizes are present.
    """

    data_sizes = {
        int(
            result["data_size_bytes"]
        )
        for result in results
    }

    if data_sizes != set(
        EXPECTED_DATA_SIZES
    ):
        raise AssertionError(
            f"Unexpected data-size set: "
            f"{data_sizes}"
        )

    print(
        "PASS: All six expected data sizes are present."
    )


def validate_experiment_types(
    results
):
    """
    Confirm that both experiment types are present.
    """

    experiment_types = {
        result["experiment_type"]
        for result in results
    }

    if experiment_types != set(
        EXPECTED_EXPERIMENT_TYPES
    ):
        raise AssertionError(
            f"Unexpected experiment types: "
            f"{experiment_types}"
        )

    print(
        "PASS: Both diffusion experiment types are present."
    )


def validate_trials_per_condition(
    results
):
    """
    Confirm that every algorithm/data-size/experiment
    combination contains exactly 32 trials.
    """

    counts = {}

    for result in results:

        key = (
            result["algorithm"],
            int(
                result["data_size_bytes"]
            ),
            result["experiment_type"]
        )

        counts[key] = (
            counts.get(
                key,
                0
            )
            + 1
        )

    expected_conditions = (
        len(EXPECTED_ALGORITHMS)
        * len(EXPECTED_DATA_SIZES)
        * len(EXPECTED_EXPERIMENT_TYPES)
    )

    if len(counts) != expected_conditions:
        raise AssertionError(
            f"Expected {expected_conditions} "
            f"experimental conditions, "
            f"but found {len(counts)}."
        )

    for key, count in counts.items():

        if count != EXPECTED_TRIALS_PER_CONDITION:
            raise AssertionError(
                f"{key} contains {count} trials "
                f"instead of "
                f"{EXPECTED_TRIALS_PER_CONDITION}."
            )

    print(
        "PASS: Every condition contains "
        "32 diffusion trials."
    )


def validate_trial_numbers(
    results
):
    """
    Confirm that every condition contains trial numbers
    1 through 32 exactly once.
    """

    trial_numbers = {}

    for result in results:

        key = (
            result["algorithm"],
            int(
                result["data_size_bytes"]
            ),
            result["experiment_type"]
        )

        if key not in trial_numbers:
            trial_numbers[key] = []

        trial_numbers[key].append(
            int(
                result["trial_number"]
            )
        )

    expected_trials = list(
        range(
            1,
            EXPECTED_TRIALS_PER_CONDITION + 1
        )
    )

    for key, trials in trial_numbers.items():

        if sorted(trials) != expected_trials:
            raise AssertionError(
                f"Invalid trial-number sequence "
                f"for {key}."
            )

    print(
        "PASS: Trial numbering is complete "
        "for every condition."
    )


def validate_ciphertext_lengths(
    results
):
    """
    Confirm that ciphertext-body bit counts match
    the plaintext data size.
    """

    for result in results:

        data_size = int(
            result["data_size_bytes"]
        )

        expected_bits = (
            data_size * 8
        )

        actual_bits = int(
            result["ciphertext_total_bits"]
        )

        if actual_bits != expected_bits:
            raise AssertionError(
                f"Ciphertext size mismatch for "
                f"{result['algorithm']}, "
                f"{data_size} bytes."
            )

    print(
        "PASS: Ciphertext-body bit counts "
        "match all data sizes."
    )


def validate_tag_lengths(
    results
):
    """
    Confirm that all authentication tags are 128 bits.
    """

    for result in results:

        tag_bits = int(
            result["tag_total_bits"]
        )

        if tag_bits != EXPECTED_TAG_BITS:
            raise AssertionError(
                f"Unexpected tag size: "
                f"{tag_bits} bits."
            )

    print(
        "PASS: All authentication tags are 128 bits."
    )


def validate_changed_bit_ranges(
    results
):
    """
    Confirm changed-bit counts are within valid ranges.
    """

    for result in results:

        ciphertext_changed_bits = int(
            result["ciphertext_changed_bits"]
        )

        ciphertext_total_bits = int(
            result["ciphertext_total_bits"]
        )

        tag_changed_bits = int(
            result["tag_changed_bits"]
        )

        tag_total_bits = int(
            result["tag_total_bits"]
        )

        if not (
            0
            <= ciphertext_changed_bits
            <= ciphertext_total_bits
        ):
            raise AssertionError(
                "Invalid ciphertext changed-bit count."
            )

        if not (
            0
            <= tag_changed_bits
            <= tag_total_bits
        ):
            raise AssertionError(
                "Invalid tag changed-bit count."
            )

    print(
        "PASS: Changed-bit counts are within "
        "valid ranges."
    )


def validate_percentage_ranges(
    results
):
    """
    Confirm all stored percentages lie between
    zero and one hundred.
    """

    for result in results:

        ciphertext_percent = float(
            result[
                "ciphertext_change_percent"
            ]
        )

        tag_percent = float(
            result[
                "tag_change_percent"
            ]
        )

        if not (
            0.0
            <= ciphertext_percent
            <= 100.0
        ):
            raise AssertionError(
                "Invalid ciphertext percentage."
            )

        if not (
            0.0
            <= tag_percent
            <= 100.0
        ):
            raise AssertionError(
                "Invalid tag percentage."
            )

    print(
        "PASS: All stored percentages are "
        "between 0 and 100."
    )


def validate_calculated_percentages(
    results
):
    """
    Recalculate diffusion percentages from raw bit counts
    and confirm they match the values stored in the CSV.
    """

    tolerance = 0.0000001

    for result in results:

        ciphertext_changed_bits = int(
            result["ciphertext_changed_bits"]
        )

        ciphertext_total_bits = int(
            result["ciphertext_total_bits"]
        )

        stored_ciphertext_percent = float(
            result[
                "ciphertext_change_percent"
            ]
        )

        expected_ciphertext_percent = (
            calculate_percent(
                ciphertext_changed_bits,
                ciphertext_total_bits
            )
        )

        if abs(
            stored_ciphertext_percent
            - expected_ciphertext_percent
        ) > tolerance:

            raise AssertionError(
                "Stored ciphertext percentage "
                "does not match raw bit counts."
            )

        tag_changed_bits = int(
            result["tag_changed_bits"]
        )

        tag_total_bits = int(
            result["tag_total_bits"]
        )

        stored_tag_percent = float(
            result[
                "tag_change_percent"
            ]
        )

        expected_tag_percent = (
            calculate_percent(
                tag_changed_bits,
                tag_total_bits
            )
        )

        if abs(
            stored_tag_percent
            - expected_tag_percent
        ) > tolerance:

            raise AssertionError(
                "Stored tag percentage does not "
                "match raw bit counts."
            )

    print(
        "PASS: Stored percentages match "
        "the raw changed-bit counts."
    )


def validate_input_bit_counts(
    results
):
    """
    Validate the input_total_bits field.

    Plaintext-bit experiments should use the payload size.

    Key-bit experiments should contain either a 128-bit
    key for Ascon or a 256-bit key for AES-GCM and
    ChaCha20-Poly1305.
    """

    expected_key_bits = {
        "Ascon-AEAD128": 128,
        "AES-GCM": 256,
        "ChaCha20-Poly1305": 256
    }

    for result in results:

        input_total_bits = int(
            result["input_total_bits"]
        )

        if (
            result["experiment_type"]
            == "plaintext_bit_flip"
        ):

            expected_bits = (
                int(
                    result["data_size_bytes"]
                )
                * 8
            )

        elif (
            result["experiment_type"]
            == "key_bit_flip"
        ):

            expected_bits = expected_key_bits[
                result["algorithm"]
            ]

        else:

            raise AssertionError(
                "Unknown experiment type."
            )

        if input_total_bits != expected_bits:
            raise AssertionError(
                f"Unexpected input bit count for "
                f"{result['algorithm']} "
                f"{result['experiment_type']}."
            )

    print(
        "PASS: Input bit counts match plaintext "
        "and key sizes."
    )


def validate_bit_positions(
    results
):
    """
    Confirm every flipped bit position is valid for
    the corresponding input.
    """

    for result in results:

        bit_position = int(
            result["bit_position"]
        )

        input_total_bits = int(
            result["input_total_bits"]
        )

        if not (
            0
            <= bit_position
            < input_total_bits
        ):
            raise AssertionError(
                f"Invalid bit position "
                f"{bit_position}."
            )

    print(
        "PASS: All flipped bit positions are valid."
    )


# ============================================================
# Main validation
# ============================================================

def main():

    print("=" * 70)
    print(
        "LightCryptBench Diffusion Dataset Validation"
    )
    print("=" * 70)

    print()
    print(
        f"Results file: {RESULTS_FILE}"
    )

    print()

    # --------------------------------------------------------
    # File validation
    # --------------------------------------------------------

    if not os.path.exists(
        RESULTS_FILE
    ):
        raise FileNotFoundError(
            f"Results file not found: "
            f"{RESULTS_FILE}"
        )

    print(
        "PASS: Results file exists."
    )

    # --------------------------------------------------------
    # Load dataset
    # --------------------------------------------------------

    results = load_results()

    print(
        f"PASS: CSV loaded successfully "
        f"({len(results):,} rows)."
    )

    # --------------------------------------------------------
    # Structural validation
    # --------------------------------------------------------

    validate_expected_count(
        results
    )

    validate_algorithms(
        results
    )

    validate_data_sizes(
        results
    )

    validate_experiment_types(
        results
    )

    validate_trials_per_condition(
        results
    )

    validate_trial_numbers(
        results
    )

    # --------------------------------------------------------
    # Cryptographic structure validation
    # --------------------------------------------------------

    validate_ciphertext_lengths(
        results
    )

    validate_tag_lengths(
        results
    )

    validate_input_bit_counts(
        results
    )

    validate_bit_positions(
        results
    )

    # --------------------------------------------------------
    # Numerical validation
    # --------------------------------------------------------

    validate_changed_bit_ranges(
        results
    )

    validate_percentage_ranges(
        results
    )

    validate_calculated_percentages(
        results
    )

    # --------------------------------------------------------
    # Complete
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print(
        "Diffusion dataset validation complete."
    )
    print("=" * 70)

    print()
    print(
        "SUCCESS: All diffusion validation "
        "checks passed."
    )


# ============================================================
# Program entry point
# ============================================================

if __name__ == "__main__":
    main()
