import csv
import os
import statistics
import sys


# ============================================================
# Project configuration
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.abspath(__file__)
)

sys.path.insert(
    0,
    PROJECT_ROOT
)

from ascon_algorithm import AsconAEAD128
from aes_gcm_algorithm import AESGCM
from chacha20_poly1305_algorithm import ChaCha20Poly1305


# ============================================================
# Experiment configuration
# ============================================================

DATA_SIZES = [
    1024,        # 1 KB
    4096,        # 4 KB
    16384,       # 16 KB
    65536,       # 64 KB
    262144,      # 256 KB
    1048576      # 1 MB
]

TRIALS_PER_EXPERIMENT = 32

TAG_LENGTH_BYTES = 16
TAG_LENGTH_BITS = TAG_LENGTH_BYTES * 8

RESULTS_DIR = os.path.join(
    PROJECT_ROOT,
    "results"
)

RESULTS_FILE = os.path.join(
    RESULTS_DIR,
    "diffusion_results.csv"
)


# ============================================================
# Test-data configuration
# ============================================================

TEST_DATA_FILES = {
    1024: "test_1kb.bin",
    4096: "test_4kb.bin",
    16384: "test_16kb.bin",
    65536: "test_64kb.bin",
    262144: "test_256kb.bin",
    1048576: "test_1mb.bin"
}


# ============================================================
# Helper functions
# ============================================================

def load_test_data(size):
    """
    Load the deterministic benchmark input file for the
    requested data size.
    """

    if size not in TEST_DATA_FILES:
        raise ValueError(
            f"No test-data file configured for "
            f"{size} bytes."
        )

    filename = os.path.join(
        PROJECT_ROOT,
        "data",
        TEST_DATA_FILES[size]
    )

    if not os.path.exists(filename):
        raise FileNotFoundError(
            f"Test-data file not found: {filename}"
        )

    with open(
        filename,
        "rb"
    ) as file:

        data = file.read()

    if len(data) != size:
        raise ValueError(
            f"Test-data size mismatch. "
            f"Expected {size} bytes but "
            f"loaded {len(data)} bytes."
        )

    return data


def get_nonce(algorithm):
    """
    Return the correct deterministic nonce size
    for the selected algorithm.
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


def split_ciphertext_and_tag(
    encrypted_data
):
    """
    Split an AEAD output into ciphertext body and
    16-byte authentication tag.
    """

    if len(encrypted_data) < TAG_LENGTH_BYTES:
        raise ValueError(
            "Encrypted result is shorter than "
            "the authentication tag."
        )

    ciphertext_body = (
        encrypted_data[:-TAG_LENGTH_BYTES]
    )

    authentication_tag = (
        encrypted_data[-TAG_LENGTH_BYTES:]
    )

    return (
        ciphertext_body,
        authentication_tag
    )


def flip_bit(
    data,
    bit_position
):
    """
    Return a copy of data with exactly one bit flipped.

    Bit positions are numbered from zero.
    """

    total_bits = len(data) * 8

    if bit_position < 0:
        raise ValueError(
            "Bit position cannot be negative."
        )

    if bit_position >= total_bits:
        raise ValueError(
            f"Bit position {bit_position} exceeds "
            f"the available {total_bits} bits."
        )

    modified = bytearray(
        data
    )

    byte_index = (
        bit_position // 8
    )

    bit_index = (
        bit_position % 8
    )

    bit_mask = (
        1 << bit_index
    )

    modified[byte_index] ^= bit_mask

    return bytes(
        modified
    )


def hamming_distance_bytes(
    first,
    second
):
    """
    Calculate the number of different bits between
    two equal-length byte sequences.
    """

    if len(first) != len(second):
        raise ValueError(
            "Hamming-distance inputs must have "
            "the same length."
        )

    changed_bits = 0

    for first_byte, second_byte in zip(
        first,
        second
    ):

        difference = (
            first_byte ^ second_byte
        )

        changed_bits += (
            difference.bit_count()
        )

    return changed_bits


def calculate_change_percent(
    changed_bits,
    total_bits
):
    """
    Calculate the percentage of bits that changed.
    """

    if total_bits <= 0:
        return 0.0

    return (
        changed_bits / total_bits
    ) * 100


def generate_trial_bit_positions(
    total_bits,
    trial_count
):
    """
    Generate deterministic bit positions distributed
    across the available bit range.

    The same experiment can therefore be reproduced.
    """

    if total_bits <= 0:
        raise ValueError(
            "Total number of bits must be positive."
        )

    if trial_count <= 0:
        raise ValueError(
            "Trial count must be positive."
        )

    if trial_count > total_bits:
        raise ValueError(
            f"Cannot select {trial_count} unique "
            f"positions from only {total_bits} bits."
        )

    positions = []

    for trial_index in range(
        trial_count
    ):

        position = int(
            (
                trial_index
                * total_bits
            )
            / trial_count
        )

        positions.append(
            position
        )

    return positions


# ============================================================
# Single comparison
# ============================================================

def compare_outputs(
    baseline_output,
    modified_output
):
    """
    Compare two AEAD outputs.

    Ciphertext body and authentication tag are measured
    independently.

    Returns a dictionary containing Hamming-distance
    measurements and percentage changes.
    """

    (
        baseline_ciphertext,
        baseline_tag
    ) = split_ciphertext_and_tag(
        baseline_output
    )

    (
        modified_ciphertext,
        modified_tag
    ) = split_ciphertext_and_tag(
        modified_output
    )

    if (
        len(baseline_ciphertext)
        != len(modified_ciphertext)
    ):
        raise ValueError(
            "Ciphertext-body lengths do not match."
        )

    if len(baseline_tag) != len(modified_tag):
        raise ValueError(
            "Authentication-tag lengths do not match."
        )

    ciphertext_changed_bits = (
        hamming_distance_bytes(
            baseline_ciphertext,
            modified_ciphertext
        )
    )

    ciphertext_total_bits = (
        len(baseline_ciphertext) * 8
    )

    ciphertext_change_percent = (
        calculate_change_percent(
            ciphertext_changed_bits,
            ciphertext_total_bits
        )
    )

    tag_changed_bits = (
        hamming_distance_bytes(
            baseline_tag,
            modified_tag
        )
    )

    tag_total_bits = (
        len(baseline_tag) * 8
    )

    tag_change_percent = (
        calculate_change_percent(
            tag_changed_bits,
            tag_total_bits
        )
    )

    return {
        "ciphertext_changed_bits":
            ciphertext_changed_bits,

        "ciphertext_total_bits":
            ciphertext_total_bits,

        "ciphertext_change_percent":
            ciphertext_change_percent,

        "tag_changed_bits":
            tag_changed_bits,

        "tag_total_bits":
            tag_total_bits,

        "tag_change_percent":
            tag_change_percent
    }


# ============================================================
# Plaintext-bit experiment
# ============================================================

def run_plaintext_bit_experiment(
    algorithm,
    key,
    nonce,
    plaintext,
    associated_data
):
    """
    Measure the effect of flipping one plaintext bit.

    The key, nonce and associated data remain unchanged.

    This controlled reuse of the nonce is performed only
    for laboratory comparison. It is not intended to
    represent operational nonce-management practice.
    """

    results = []

    baseline_output = algorithm.encrypt(
        key,
        nonce,
        plaintext,
        associated_data
    )

    plaintext_total_bits = (
        len(plaintext) * 8
    )

    trial_positions = (
        generate_trial_bit_positions(
            plaintext_total_bits,
            TRIALS_PER_EXPERIMENT
        )
    )

    for trial_number, bit_position in enumerate(
        trial_positions,
        start=1
    ):

        modified_plaintext = flip_bit(
            plaintext,
            bit_position
        )

        modified_output = algorithm.encrypt(
            key,
            nonce,
            modified_plaintext,
            associated_data
        )

        comparison = compare_outputs(
            baseline_output,
            modified_output
        )

        result = {
            "algorithm":
                algorithm.name,

            "data_size_bytes":
                len(plaintext),

            "experiment_type":
                "plaintext_bit_flip",

            "trial_number":
                trial_number,

            "bit_position":
                bit_position,

            "input_total_bits":
                plaintext_total_bits,

            "ciphertext_changed_bits":
                comparison[
                    "ciphertext_changed_bits"
                ],

            "ciphertext_total_bits":
                comparison[
                    "ciphertext_total_bits"
                ],

            "ciphertext_change_percent":
                comparison[
                    "ciphertext_change_percent"
                ],

            "tag_changed_bits":
                comparison[
                    "tag_changed_bits"
                ],

            "tag_total_bits":
                comparison[
                    "tag_total_bits"
                ],

            "tag_change_percent":
                comparison[
                    "tag_change_percent"
                ]
        }

        results.append(
            result
        )

    return results


# ============================================================
# Key-bit experiment
# ============================================================

def run_key_bit_experiment(
    algorithm,
    key,
    nonce,
    plaintext,
    associated_data
):
    """
    Measure the effect of flipping one key bit.

    Plaintext, nonce and associated data remain fixed.
    """

    results = []

    baseline_output = algorithm.encrypt(
        key,
        nonce,
        plaintext,
        associated_data
    )

    key_total_bits = (
        len(key) * 8
    )

    # Ascon uses a 128-bit key, so at most 32 trials
    # remain comfortably within the available bit range.
    trial_positions = (
        generate_trial_bit_positions(
            key_total_bits,
            TRIALS_PER_EXPERIMENT
        )
    )

    for trial_number, bit_position in enumerate(
        trial_positions,
        start=1
    ):

        modified_key = flip_bit(
            key,
            bit_position
        )

        modified_output = algorithm.encrypt(
            modified_key,
            nonce,
            plaintext,
            associated_data
        )

        comparison = compare_outputs(
            baseline_output,
            modified_output
        )

        result = {
            "algorithm":
                algorithm.name,

            "data_size_bytes":
                len(plaintext),

            "experiment_type":
                "key_bit_flip",

            "trial_number":
                trial_number,

            "bit_position":
                bit_position,

            "input_total_bits":
                key_total_bits,

            "ciphertext_changed_bits":
                comparison[
                    "ciphertext_changed_bits"
                ],

            "ciphertext_total_bits":
                comparison[
                    "ciphertext_total_bits"
                ],

            "ciphertext_change_percent":
                comparison[
                    "ciphertext_change_percent"
                ],

            "tag_changed_bits":
                comparison[
                    "tag_changed_bits"
                ],

            "tag_total_bits":
                comparison[
                    "tag_total_bits"
                ],

            "tag_change_percent":
                comparison[
                    "tag_change_percent"
                ]
        }

        results.append(
            result
        )

    return results


# ============================================================
# CSV export
# ============================================================

def export_results(
    results
):
    """
    Export all raw diffusion observations to CSV.
    """

    os.makedirs(
        RESULTS_DIR,
        exist_ok=True
    )

    fieldnames = [
        "algorithm",
        "data_size_bytes",
        "experiment_type",
        "trial_number",
        "bit_position",
        "input_total_bits",
        "ciphertext_changed_bits",
        "ciphertext_total_bits",
        "ciphertext_change_percent",
        "tag_changed_bits",
        "tag_total_bits",
        "tag_change_percent"
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

            writer.writerow(
                result
            )

    print()
    print(
        f"Diffusion results exported to: "
        f"{RESULTS_FILE}"
    )


# ============================================================
# Summary analysis
# ============================================================

def summarise_group(
    results,
    algorithm_name,
    data_size,
    experiment_type
):
    """
    Calculate summary statistics for one algorithm,
    data size and experiment type.
    """

    matching_results = [
        result
        for result in results
        if (
            result["algorithm"]
            == algorithm_name

            and result["data_size_bytes"]
            == data_size

            and result["experiment_type"]
            == experiment_type
        )
    ]

    if not matching_results:
        raise ValueError(
            f"No results found for "
            f"{algorithm_name}, "
            f"{data_size}, "
            f"{experiment_type}."
        )

    ciphertext_percentages = [
        result[
            "ciphertext_change_percent"
        ]
        for result in matching_results
    ]

    tag_percentages = [
        result[
            "tag_change_percent"
        ]
        for result in matching_results
    ]

    return {
        "ciphertext_mean":
            statistics.mean(
                ciphertext_percentages
            ),

        "ciphertext_median":
            statistics.median(
                ciphertext_percentages
            ),

        "ciphertext_stdev":
            statistics.stdev(
                ciphertext_percentages
            ),

        "tag_mean":
            statistics.mean(
                tag_percentages
            ),

        "tag_median":
            statistics.median(
                tag_percentages
            ),

        "tag_stdev":
            statistics.stdev(
                tag_percentages
            )
    }


def print_summary(
    results,
    algorithms
):
    """
    Display concise diffusion summaries.
    """

    print()
    print("=" * 70)
    print("Diffusion and Avalanche Summary")
    print("=" * 70)

    experiment_names = {
        "plaintext_bit_flip":
            "Plaintext Bit Flip",

        "key_bit_flip":
            "Key Bit Flip"
    }

    for experiment_type in [
        "plaintext_bit_flip",
        "key_bit_flip"
    ]:

        print()
        print("=" * 70)
        print(
            experiment_names[
                experiment_type
            ]
        )
        print("=" * 70)

        for algorithm in algorithms:

            print()
            print(
                f"Algorithm: {algorithm.name}"
            )

            print("-" * 70)

            for size in DATA_SIZES:

                summary = summarise_group(
                    results,
                    algorithm.name,
                    size,
                    experiment_type
                )

                print(
                    f"{size:>10,} bytes | "
                    f"Ciphertext: "
                    f"{summary['ciphertext_mean']:7.3f}% "
                    f"(SD {summary['ciphertext_stdev']:6.3f})"
                    f" | Tag: "
                    f"{summary['tag_mean']:7.3f}% "
                    f"(SD {summary['tag_stdev']:6.3f})"
                )


# ============================================================
# Dataset validation
# ============================================================

def validate_results(
    results
):
    """
    Perform basic internal validation before export.
    """

    expected_result_count = (
        3
        * len(DATA_SIZES)
        * 2
        * TRIALS_PER_EXPERIMENT
    )

    if len(results) != expected_result_count:
        raise ValueError(
            f"Expected {expected_result_count} "
            f"diffusion observations but "
            f"collected {len(results)}."
        )

    for result in results:

        if (
            result["tag_total_bits"]
            != TAG_LENGTH_BITS
        ):
            raise ValueError(
                "Unexpected authentication-tag size."
            )

        if (
            result["ciphertext_total_bits"]
            != result["data_size_bytes"] * 8
        ):
            raise ValueError(
                "Ciphertext-body size does not "
                "match plaintext size."
            )

        if not (
            0.0
            <= result[
                "ciphertext_change_percent"
            ]
            <= 100.0
        ):
            raise ValueError(
                "Invalid ciphertext-change percentage."
            )

        if not (
            0.0
            <= result[
                "tag_change_percent"
            ]
            <= 100.0
        ):
            raise ValueError(
                "Invalid tag-change percentage."
            )

    return True


# ============================================================
# Main experiment
# ============================================================

def main():

    print("=" * 70)
    print("LightCryptBench Diffusion and Avalanche Analysis")
    print("=" * 70)

    print()
    print(
        f"Algorithms:              3"
    )

    print(
        f"Data sizes:              "
        f"{len(DATA_SIZES)}"
    )

    print(
        f"Experiment types:        2"
    )

    print(
        f"Trials per experiment:   "
        f"{TRIALS_PER_EXPERIMENT}"
    )

    expected_total = (
        3
        * len(DATA_SIZES)
        * 2
        * TRIALS_PER_EXPERIMENT
    )

    print(
        f"Expected observations:   "
        f"{expected_total:,}"
    )

    print()
    print(
        "Plaintext-bit experiment:"
    )

    print(
        "  key, nonce and AAD remain fixed."
    )

    print(
        "  nonce reuse is for controlled "
        "laboratory comparison only."
    )

    print()
    print(
        "Key-bit experiment:"
    )

    print(
        "  plaintext, nonce and AAD remain fixed."
    )

    algorithms = [
        AsconAEAD128(),
        AESGCM(),
        ChaCha20Poly1305()
    ]

    associated_data = b""

    all_results = []

    # --------------------------------------------------------
    # Run experiments
    # --------------------------------------------------------

    for algorithm in algorithms:

        print()
        print("=" * 70)
        print(
            f"Algorithm: {algorithm.name}"
        )
        print("=" * 70)

        key = algorithm.generate_key()
        nonce = get_nonce(
            algorithm
        )

        for size in DATA_SIZES:

            print()
            print(
                f"Data size: {size:,} bytes"
            )

            plaintext = load_test_data(
                size
            )

            # ------------------------------------------------
            # Plaintext bit flip
            # ------------------------------------------------

            print(
                f"  Running plaintext-bit "
                f"trials: {TRIALS_PER_EXPERIMENT}"
            )

            plaintext_results = (
                run_plaintext_bit_experiment(
                    algorithm,
                    key,
                    nonce,
                    plaintext,
                    associated_data
                )
            )

            all_results.extend(
                plaintext_results
            )

            # ------------------------------------------------
            # Key bit flip
            # ------------------------------------------------

            print(
                f"  Running key-bit "
                f"trials:       "
                f"{TRIALS_PER_EXPERIMENT}"
            )

            key_results = (
                run_key_bit_experiment(
                    algorithm,
                    key,
                    nonce,
                    plaintext,
                    associated_data
                )
            )

            all_results.extend(
                key_results
            )

    # ========================================================
    # Validate dataset
    # ========================================================

    print()
    print("=" * 70)
    print("Validating diffusion dataset")
    print("=" * 70)

    validate_results(
        all_results
    )

    print()
    print(
        f"PASS: Collected "
        f"{len(all_results):,} observations."
    )

    print(
        "PASS: Ciphertext-body lengths are valid."
    )

    print(
        "PASS: Authentication tags are 128 bits."
    )

    print(
        "PASS: All change percentages are valid."
    )

    # ========================================================
    # Export dataset
    # ========================================================

    export_results(
        all_results
    )

    # ========================================================
    # Print summaries
    # ========================================================

    print_summary(
        all_results,
        algorithms
    )

    # ========================================================
    # Complete
    # ========================================================

    print()
    print("=" * 70)
    print(
        "Diffusion and avalanche analysis complete."
    )
    print("=" * 70)

    print()
    print(
        f"Total observations: "
        f"{len(all_results):,}"
    )

    print(
        f"Results file: "
        f"{RESULTS_FILE}"
    )


# ============================================================
# Program entry point
# ============================================================

if __name__ == "__main__":
    main()
