import time
import psutil


print("=" * 60)
print("LightCryptBench CPU Measurement Test")
print("=" * 60)

print()
print("CPU measurement before test:")

psutil.cpu_percent(interval=None)

print()
print("Running CPU-intensive test...")

start_cpu = psutil.cpu_percent(interval=None)

start_time = time.perf_counter()

# Perform some CPU-intensive work
total = 0

for i in range(10_000_000):
    total += i * i

elapsed = time.perf_counter() - start_time

end_cpu = psutil.cpu_percent(interval=0.1)

print()
print(f"CPU usage before test: {start_cpu:.2f}%")
print(f"CPU usage after test:  {end_cpu:.2f}%")
print(f"Test execution time:   {elapsed:.4f} seconds")

print()
print("=" * 60)
print("CPU measurement test complete.")
print("=" * 60)


