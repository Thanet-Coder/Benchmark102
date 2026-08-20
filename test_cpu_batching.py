from benchmark.benchmark_runner import measure_cpu_time_batched


print("=" * 60)
print("LightCryptBench Batched CPU Measurement Test")
print("=" * 60)


# ============================================================
# CPU-bound test operation
# ============================================================

def cpu_test_operation():

    total = 0

    for i in range(10_000):
        total += i * i

    return total


# ============================================================
# Measure CPU time using adaptive batching
# ============================================================

cpu_time_ns, batch_runs = measure_cpu_time_batched(
    cpu_test_operation
)


# ============================================================
# Display results
# ============================================================

print()
print(f"CPU time per operation: {cpu_time_ns:,.0f} ns")
print(f"CPU batch runs:         {batch_runs:,}")

print()
print(
    f"CPU time per operation: "
    f"{cpu_time_ns / 1_000_000:.4f} ms"
)


# ============================================================
# Validation
# ============================================================

assert cpu_time_ns > 0
assert batch_runs > 0

print()
print("PASS: CPU time is positive.")
print("PASS: CPU batch size is positive.")

if batch_runs > 1:
    print("PASS: Adaptive batching was used.")
else:
    print(
        "INFO: One operation was sufficient "
        "to reach the CPU batch target."
    )


# ============================================================
# Complete
# ============================================================

print()
print("=" * 60)
print("Batched CPU measurement test complete.")
print("=" * 60)
