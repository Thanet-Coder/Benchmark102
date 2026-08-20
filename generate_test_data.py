import os


# ============================================================
# Configuration
# ============================================================

DATA_DIRECTORY = "data"

TEST_SIZES = {
    "1kb": 1_024,
    "4kb": 4_096,
    "16kb": 16_384,
    "64kb": 65_536,
    "256kb": 262_144,
    "1mb": 1_048_576,
}


# ============================================================
# Generate deterministic test data
# ============================================================

def generate_test_data():

    os.makedirs(DATA_DIRECTORY, exist_ok=True)

    print("=" * 60)
    print("LightCryptBench Test Data Generation")
    print("=" * 60)

    for name, size in TEST_SIZES.items():

        filename = os.path.join(
            DATA_DIRECTORY,
            f"test_{name}.bin"
        )

        # Deterministic byte pattern.
        data = bytes(
            value % 256
            for value in range(size)
        )

        with open(filename, "wb") as file:
            file.write(data)

        actual_size = os.path.getsize(filename)

        print(
            f"Created: {filename:<25}"
            f" {actual_size:,} bytes"
        )

    print()
    print("=" * 60)
    print("Test data generation complete.")
    print("=" * 60)


if __name__ == "__main__":
    generate_test_data()
