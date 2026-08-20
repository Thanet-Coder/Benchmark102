import os
import psutil
import time


# ============================================================
# Memory Measurement Test
# ============================================================

def get_memory_usage_mb():
    """
    Return the current process memory usage in megabytes.
    """

    process = psutil.Process(os.getpid())

    memory_bytes = process.memory_info().rss

    return memory_bytes / (1024 * 1024)


def memory_intensive_test():
    """
    Create a temporary memory allocation so that
    memory usage can be measured.
    """

    data = bytearray(50 * 1024 * 1024)

    # Touch the allocated memory so the allocation is actually used.
    for i in range(0, len(data), 4096):
        data[i] = 1

    time.sleep(1)

    return data


def main():

    print("=" * 60)
    print("LightCryptBench Memory Measurement Test")
    print("=" * 60)

    # --------------------------------------------------------
    # Measure memory before test
    # --------------------------------------------------------

    print()
    print("Memory measurement before test:")

    memory_before = get_memory_usage_mb()

    print(
        f"Memory usage before test: "
        f"{memory_before:.2f} MB"
    )

    # --------------------------------------------------------
    # Run memory-intensive test
    # --------------------------------------------------------

    print()
    print("Running memory-intensive test...")

    data = memory_intensive_test()

    # --------------------------------------------------------
    # Measure memory after test
    # --------------------------------------------------------

    memory_after = get_memory_usage_mb()

    print(
        f"Memory usage after test:  "
        f"{memory_after:.2f} MB"
    )

    # --------------------------------------------------------
    # Calculate difference
    # --------------------------------------------------------

    memory_difference = memory_after - memory_before

    print(
        f"Memory difference:        "
        f"{memory_difference:.2f} MB"
    )

    # Prevent the allocation from being optimised away.
    print(
        f"Test allocation size:     "
        f"{len(data) / (1024 * 1024):.2f} MB"
    )

    # --------------------------------------------------------
    # Completion
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("Memory measurement test complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
