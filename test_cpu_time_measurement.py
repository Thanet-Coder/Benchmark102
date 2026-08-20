import time


print("=" * 60)
print("LightCryptBench CPU Time Measurement Test")
print("=" * 60)


# ============================================================
# Test CPU-bound operation
# ============================================================

wall_start = time.perf_counter_ns()
cpu_start = time.process_time_ns()

total = 0

for i in range(5_000_000):
    total += i * i

cpu_end = time.process_time_ns()
wall_end = time.perf_counter_ns()


# ============================================================
# Calculate results
# ============================================================

wall_time_ns = wall_end - wall_start
cpu_time_ns = cpu_end - cpu_start


# ============================================================
# Display results
# ============================================================

print()
print(f"Wall-clock time: {wall_time_ns:,} ns")
print(f"CPU time:        {cpu_time_ns:,} ns")

print()
print(f"Wall-clock time: {wall_time_ns / 1_000_000:.2f} ms")
print(f"CPU time:        {cpu_time_ns / 1_000_000:.2f} ms")


# ============================================================
# Validation
# ============================================================

assert wall_time_ns > 0
assert cpu_time_ns > 0

print()
print("PASS: Wall-clock time is positive.")
print("PASS: CPU time is positive.")

print()
print("=" * 60)
print("CPU time measurement test complete.")
print("=" * 60)
