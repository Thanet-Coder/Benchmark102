import csv
import os
import statistics

import matplotlib.pyplot as plt


# ============================================================
# Configuration
# ============================================================

RESULTS_FILE = os.path.join(
    "results",
    "diffusion_results.csv"
)

GRAPHS_DIR = os.path.join(
    "results",
    "graphs",
    "diffusion"
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


EXPERIMENT_PLAINTEXT = "plaintext_bit_flip"
EXPERIMENT_KEY = "key_bit_flip"


# ============================================================
# Data loading
# ============================================================

def load_results():
    """
    Load the validated diffusion dataset.
    """

    with open(
        RESULTS_FILE,
        "r",
        newline="",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        return list(reader)


def convert_result(result):
    """
    Convert one CSV record to appropriate Python types.
    """

    return {
        "algorithm":
            result["algorithm"],

        "data_size_bytes":
            int(
                result["data_size_bytes"]
            ),

        "experiment_type":
            result["experiment_type"],

        "trial_number":
            int(
                result["trial_number"]
            ),

        "bit_position":
            int(
                result["bit_position"]
            ),

        "input_total_bits":
            int(
                result["input_total_bits"]
            ),

        "ciphertext_changed_bits":
            int(
                result[
                    "ciphertext_changed_bits"
                ]
            ),

        "ciphertext_total_bits":
            int(
                result[
                    "ciphertext_total_bits"
                ]
            ),

        "ciphertext_change_percent":
            float(
                result[
                    "ciphertext_change_percent"
                ]
            ),

        "tag_changed_bits":
            int(
                result[
                    "tag_changed_bits"
                ]
            ),

        "tag_total_bits":
            int(
                result[
                    "tag_total_bits"
                ]
            ),

        "tag_change_percent":
            float(
                result[
                    "tag_change_percent"
                ]
            )
    }


def prepare_results():
    """
    Load and convert every diffusion result.
    """

    raw_results = load_results()

    return [
        convert_result(result)
        for result in raw_results
    ]


# ============================================================
# Filtering and summary helpers
# ============================================================

def filter_results(
    results,
    algorithm=None,
    data_size=None,
    experiment_type=None
):
    """
    Return results matching the supplied conditions.
    """

    filtered = []

    for result in results:

        if (
            algorithm is not None
            and result["algorithm"] != algorithm
        ):
            continue

        if (
            data_size is not None
            and result["data_size_bytes"] != data_size
        ):
            continue

        if (
            experiment_type is not None
            and result["experiment_type"]
            != experiment_type
        ):
            continue

        filtered.append(
            result
        )

    return filtered


def get_metric_values(
    results,
    algorithm,
    data_size,
    experiment_type,
    metric
):
    """
    Retrieve all 32 observations for one condition.
    """

    matching = filter_results(
        results,
        algorithm=algorithm,
        data_size=data_size,
        experiment_type=experiment_type
    )

    if len(matching) != 32:
        raise ValueError(
            f"Expected 32 observations for "
            f"{algorithm}, {data_size}, "
            f"{experiment_type}, but found "
            f"{len(matching)}."
        )

    return [
        result[metric]
        for result in matching
    ]


def get_mean_metric(
    results,
    algorithm,
    data_size,
    experiment_type,
    metric
):
    """
    Calculate the mean value of one diffusion metric.
    """

    values = get_metric_values(
        results,
        algorithm,
        data_size,
        experiment_type,
        metric
    )

    return statistics.mean(
        values
    )


def get_stdev_metric(
    results,
    algorithm,
    data_size,
    experiment_type,
    metric
):
    """
    Calculate standard deviation of one diffusion metric.
    """

    values = get_metric_values(
        results,
        algorithm,
        data_size,
        experiment_type,
        metric
    )

    return statistics.stdev(
        values
    )


# ============================================================
# Figure helpers
# ============================================================

def create_figure(
    width=10,
    height=6
):
    """
    Create a standard dissertation figure.
    """

    plt.figure(
        figsize=(
            width,
            height
        )
    )


def configure_data_size_axis():
    """
    Configure the common payload-size x-axis.
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
    Add restrained grid lines.
    """

    plt.grid(
        True,
        which="major",
        linestyle="--",
        alpha=0.35
    )


def add_fifty_percent_reference():
    """
    Add the classical 50 percent avalanche reference line.
    """

    plt.axhline(
        y=50.0,
        linestyle="--",
        linewidth=1.5,
        label="50% reference"
    )


def save_figure(
    filename
):
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
# Plaintext bit flip - ciphertext body
# ============================================================

def figure_01_plaintext_ciphertext(
    results
):
    """
    Plot mean ciphertext-body change following
    a one-bit plaintext modification.
    """

    create_figure()

    for algorithm in EXPECTED_ALGORITHMS:

        means = [
            get_mean_metric(
                results,
                algorithm,
                size,
                EXPERIMENT_PLAINTEXT,
                "ciphertext_change_percent"
            )
            for size in DATA_SIZES
        ]

        stdevs = [
            get_stdev_metric(
                results,
                algorithm,
                size,
                EXPERIMENT_PLAINTEXT,
                "ciphertext_change_percent"
            )
            for size in DATA_SIZES
        ]

        plt.errorbar(
            DATA_SIZES,
            means,
            yerr=stdevs,
            marker="o",
            linewidth=2,
            capsize=4,
            label=algorithm
        )

    configure_data_size_axis()
    configure_grid()

    plt.ylabel(
        "Ciphertext Bits Changed (%)"
    )

    plt.title(
        "Plaintext Bit Flip: Ciphertext-Body Diffusion"
    )

    plt.legend()

    save_figure(
        "Figure_13_Plaintext_Ciphertext_Diffusion.png"
    )


# ============================================================
# Figure 2
# Plaintext bit flip - authentication tag
# ============================================================

def figure_02_plaintext_tag(
    results
):
    """
    Plot authentication-tag avalanche following
    a one-bit plaintext modification.
    """

    create_figure()

    for algorithm in EXPECTED_ALGORITHMS:

        means = [
            get_mean_metric(
                results,
                algorithm,
                size,
                EXPERIMENT_PLAINTEXT,
                "tag_change_percent"
            )
            for size in DATA_SIZES
        ]

        stdevs = [
            get_stdev_metric(
                results,
                algorithm,
                size,
                EXPERIMENT_PLAINTEXT,
                "tag_change_percent"
            )
            for size in DATA_SIZES
        ]

        plt.errorbar(
            DATA_SIZES,
            means,
            yerr=stdevs,
            marker="o",
            linewidth=2,
            capsize=4,
            label=algorithm
        )

    add_fifty_percent_reference()
    configure_data_size_axis()
    configure_grid()

    plt.ylim(
        30,
        70
    )

    plt.ylabel(
        "Authentication Tag Bits Changed (%)"
    )

    plt.title(
        "Plaintext Bit Flip: Authentication-Tag Avalanche"
    )

    plt.legend()

    save_figure(
        "Figure_14_Plaintext_Tag_Avalanche.png"
    )


# ============================================================
# Figure 3
# Key bit flip - ciphertext body
# ============================================================

def figure_03_key_ciphertext(
    results
):
    """
    Plot ciphertext-body avalanche following
    a one-bit key modification.
    """

    create_figure()

    for algorithm in EXPECTED_ALGORITHMS:

        means = [
            get_mean_metric(
                results,
                algorithm,
                size,
                EXPERIMENT_KEY,
                "ciphertext_change_percent"
            )
            for size in DATA_SIZES
        ]

        stdevs = [
            get_stdev_metric(
                results,
                algorithm,
                size,
                EXPERIMENT_KEY,
                "ciphertext_change_percent"
            )
            for size in DATA_SIZES
        ]

        plt.errorbar(
            DATA_SIZES,
            means,
            yerr=stdevs,
            marker="o",
            linewidth=2,
            capsize=4,
            label=algorithm
        )

    add_fifty_percent_reference()
    configure_data_size_axis()
    configure_grid()

    plt.ylim(
        45,
        55
    )

    plt.ylabel(
        "Ciphertext Bits Changed (%)"
    )

    plt.title(
        "Key Bit Flip: Ciphertext-Body Avalanche"
    )

    plt.legend()

    save_figure(
        "Figure_15_Key_Ciphertext_Avalanche.png"
    )


# ============================================================
# Figure 4
# Key bit flip - authentication tag
# ============================================================

def figure_04_key_tag(
    results
):
    """
    Plot authentication-tag avalanche following
    a one-bit key modification.
    """

    create_figure()

    for algorithm in EXPECTED_ALGORITHMS:

        means = [
            get_mean_metric(
                results,
                algorithm,
                size,
                EXPERIMENT_KEY,
                "tag_change_percent"
            )
            for size in DATA_SIZES
        ]

        stdevs = [
            get_stdev_metric(
                results,
                algorithm,
                size,
                EXPERIMENT_KEY,
                "tag_change_percent"
            )
            for size in DATA_SIZES
        ]

        plt.errorbar(
            DATA_SIZES,
            means,
            yerr=stdevs,
            marker="o",
            linewidth=2,
            capsize=4,
            label=algorithm
        )

    add_fifty_percent_reference()
    configure_data_size_axis()
    configure_grid()

    plt.ylim(
        30,
        70
    )

    plt.ylabel(
        "Authentication Tag Bits Changed (%)"
    )

    plt.title(
        "Key Bit Flip: Authentication-Tag Avalanche"
    )

    plt.legend()

    save_figure(
        "Figure_16_Key_Tag_Avalanche.png"
    )


# ============================================================
# Heatmap helpers
# ============================================================

def normalise_absolute_distance_from_fifty(
    value
):
    """
    Convert distance from the ideal 50 percent avalanche
    point into a score between zero and one.

    1.0 means exactly 50 percent.

    0.0 represents a result 50 percentage points away.
    """

    distance = abs(
        value - 50.0
    )

    score = (
        1.0
        - (
            distance / 50.0
        )
    )

    return max(
        0.0,
        min(
            1.0,
            score
        )
    )


# ============================================================
# Figure 5
# 1 MB diffusion heatmap
# ============================================================

def figure_05_diffusion_heatmap(
    results
):
    """
    Create a summary heatmap for the 1 MB payload.

    The heatmap measures closeness to the classical
    50 percent avalanche point.

    This is intended as a visual summary only.
    Plaintext ciphertext-body behaviour must still be
    interpreted according to the AEAD construction.
    """

    size = 1048576

    metric_labels = [
        "Plaintext -> Ciphertext",
        "Plaintext -> Tag",
        "Key -> Ciphertext",
        "Key -> Tag"
    ]

    raw_values = []

    raw_values.append([
        get_mean_metric(
            results,
            algorithm,
            size,
            EXPERIMENT_PLAINTEXT,
            "ciphertext_change_percent"
        )
        for algorithm in EXPECTED_ALGORITHMS
    ])

    raw_values.append([
        get_mean_metric(
            results,
            algorithm,
            size,
            EXPERIMENT_PLAINTEXT,
            "tag_change_percent"
        )
        for algorithm in EXPECTED_ALGORITHMS
    ])

    raw_values.append([
        get_mean_metric(
            results,
            algorithm,
            size,
            EXPERIMENT_KEY,
            "ciphertext_change_percent"
        )
        for algorithm in EXPECTED_ALGORITHMS
    ])

    raw_values.append([
        get_mean_metric(
            results,
            algorithm,
            size,
            EXPERIMENT_KEY,
            "tag_change_percent"
        )
        for algorithm in EXPECTED_ALGORITHMS
    ])

    scores = [
        [
            normalise_absolute_distance_from_fifty(
                value
            )
            for value in row
        ]
        for row in raw_values
    ]

    plt.figure(
        figsize=(
            9,
            6
        )
    )

    image = plt.imshow(
        scores,
        aspect="auto",
        vmin=0,
        vmax=1,
        cmap="viridis"
    )

    plt.colorbar(
        image,
        label="Closeness to 50% Avalanche"
    )

    plt.xticks(
        range(
            len(EXPECTED_ALGORITHMS)
        ),
        EXPECTED_ALGORITHMS
    )

    plt.yticks(
        range(
            len(metric_labels)
        ),
        metric_labels
    )

    for row_index in range(
        len(scores)
    ):

        for column_index in range(
            len(EXPECTED_ALGORITHMS)
        ):

            score = scores[
                row_index
            ][
                column_index
            ]

            raw_value = raw_values[
                row_index
            ][
                column_index
            ]

            text_value = (
                f"{raw_value:.2f}%"
            )

            plt.text(
                column_index,
                row_index,
                text_value,
                ha="center",
                va="center",
                color=(
                    "white"
                    if score < 0.55
                    else "black"
                )
            )

    plt.xlabel(
        "Algorithm"
    )

    plt.ylabel(
        "Diffusion Metric"
    )

    plt.title(
        "1 MB Diffusion and Avalanche Comparison"
    )

    save_figure(
        "Figure_17_Diffusion_Heatmap.png"
    )


# ============================================================
# Figure 6
# Distribution of 1 MB key-bit avalanche
# ============================================================

def figure_06_key_avalanche_distribution(
    results
):
    """
    Show the distribution of the 32 ciphertext-body
    avalanche observations for the 1 MB key-bit test.
    """

    size = 1048576

    datasets = []

    for algorithm in EXPECTED_ALGORITHMS:

        values = get_metric_values(
            results,
            algorithm,
            size,
            EXPERIMENT_KEY,
            "ciphertext_change_percent"
        )

        datasets.append(
            values
        )

    create_figure(
        width=9,
        height=6
    )

    plt.boxplot(
        datasets,
        tick_labels=EXPECTED_ALGORITHMS,
        showmeans=True
    )

    add_fifty_percent_reference()
    configure_grid()

    plt.ylabel(
        "Ciphertext Bits Changed (%)"
    )

    plt.title(
        "Distribution of 1 MB Key-Bit Avalanche Results"
    )

    plt.legend()

    save_figure(
        "Figure_18_Key_Avalanche_Distribution.png"
    )


# ============================================================
# Dataset check
# ============================================================

def validate_loaded_dataset(
    results
):
    """
    Perform a basic structural check before plotting.

    Full validation remains the responsibility of
    validate_diffusion_results.py.
    """

    expected_count = 1152

    if len(results) != expected_count:
        raise ValueError(
            f"Expected {expected_count} diffusion "
            f"observations but loaded {len(results)}."
        )

    algorithms = {
        result["algorithm"]
        for result in results
    }

    if algorithms != set(
        EXPECTED_ALGORITHMS
    ):
        raise ValueError(
            "Unexpected algorithm set in "
            "diffusion dataset."
        )

    sizes = {
        result["data_size_bytes"]
        for result in results
    }

    if sizes != set(
        DATA_SIZES
    ):
        raise ValueError(
            "Unexpected data-size set in "
            "diffusion dataset."
        )


# ============================================================
# Main
# ============================================================

def main():

    print("=" * 70)
    print(
        "LightCryptBench Diffusion Figure Generation"
    )
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

    validate_loaded_dataset(
        results
    )

    print(
        f"Loaded {len(results):,} "
        f"validated diffusion observations."
    )

    print()
    print(
        "Generating diffusion figures..."
    )
    print()

    figure_01_plaintext_ciphertext(
        results
    )

    figure_02_plaintext_tag(
        results
    )

    figure_03_key_ciphertext(
        results
    )

    figure_04_key_tag(
        results
    )

    figure_05_diffusion_heatmap(
        results
    )

    figure_06_key_avalanche_distribution(
        results
    )

    print()
    print("=" * 70)
    print(
        "Diffusion figure generation complete."
    )
    print("=" * 70)

    print()
    print(
        "Total diffusion figures generated: 6"
    )

    print(
        f"Figures saved to: {GRAPHS_DIR}"
    )


# ============================================================
# Program entry point
# ============================================================

if __name__ == "__main__":
    main()
