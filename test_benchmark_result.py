from benchmark.benchmark_runner import create_benchmark_result
from ascon_algorithm import AsconAEAD128


print("Testing benchmark result structure")
print("=" * 60)


# Create algorithm
algorithm = AsconAEAD128()


# Example timing measurements
timings = [
    100000,
    110000,
    105000,
    98000,
    102000
]


# Create result
result = create_benchmark_result(
    algorithm,
    1024,
    "encryption",
    timings
)


# Display result
print("Algorithm:", result["algorithm"])
print("Data size:", result["data_size_bytes"], "bytes")
print("Operation:", result["operation"])
print("Measurements:", result["measurements"])
print("Mean:", result["mean_ns"], "ns")
print("Median:", result["median_ns"], "ns")
print("Minimum:", result["min_ns"], "ns")
print("Maximum:", result["max_ns"], "ns")
print("StdDev:", result["stdev_ns"], "ns")


print()
print("SUCCESS: Benchmark result structure created.")
