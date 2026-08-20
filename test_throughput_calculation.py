from analyse_benchmark_results import calculate_throughput_mb_s


print("=" * 60)
print("LightCryptBench Throughput Calculation Test")
print("=" * 60)


# ============================================================
# Test 1 - Simple known calculation
# ============================================================

data_size = 1_000_000
mean_ns = 1_000_000

expected = 1000.0

result = calculate_throughput_mb_s(
    data_size,
    mean_ns
)

print()
print("Test 1: Known throughput calculation")
print(f"Data size: {data_size:,} bytes")
print(f"Mean time: {mean_ns:,} ns")
print(f"Expected:  {expected:.2f} MB/s")
print(f"Actual:    {result:.2f} MB/s")

assert abs(result - expected) < 0.000001

print("PASS")


# ============================================================
# Test 2 - Realistic 1 KB benchmark
# ============================================================

data_size = 1024
mean_ns = 2_000_000

expected = 0.512

result = calculate_throughput_mb_s(
    data_size,
    mean_ns
)

print()
print("Test 2: 1 KB benchmark")
print(f"Data size: {data_size:,} bytes")
print(f"Mean time: {mean_ns:,} ns")
print(f"Expected:  {expected:.3f} MB/s")
print(f"Actual:    {result:.3f} MB/s")

assert abs(result - expected) < 0.000001

print("PASS")


# ============================================================
# Test 3 - Realistic 1 MB benchmark
# ============================================================

data_size = 1_048_576
mean_ns = 1_000_000

expected = 1048.576

result = calculate_throughput_mb_s(
    data_size,
    mean_ns
)

print()
print("Test 3: 1 MB benchmark")
print(f"Data size: {data_size:,} bytes")
print(f"Mean time: {mean_ns:,} ns")
print(f"Expected:  {expected:.6f} MB/s")
print(f"Actual:    {result:.6f} MB/s")

assert abs(result - expected) < 0.000001

print("PASS")


# ============================================================
# Test 4 - Positive result
# ============================================================

assert result > 0

print()
print("Test 4: Throughput is positive")
print("PASS")


# ============================================================
# Complete
# ============================================================

print()
print("=" * 60)
print("Throughput calculation test complete.")
print("=" * 60)
print()
print("SUCCESS: All throughput tests passed.")