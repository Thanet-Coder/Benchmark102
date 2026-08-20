# LightCryptBench

LightCryptBench is a Python-based cryptographic benchmarking and analysis framework developed to evaluate the performance and diffusion characteristics of authenticated encryption algorithms.

The project compares three authenticated encryption with associated data (AEAD) algorithms:

- Ascon-AEAD128
- AES-GCM
- ChaCha20-Poly1305

The framework measures execution performance across multiple data sizes and performs controlled diffusion and avalanche experiments to examine how changes to plaintext and cryptographic keys affect ciphertext and authentication tags.

The project was developed as part of an MSc Cyber Security dissertation.

---

## Algorithms

### Ascon-AEAD128

Ascon-AEAD128 is evaluated using the Python reference implementation included in:

```text
algorithms/pyascon
```

The implementation is accessed through the common LightCryptBench algorithm interface.

### AES-GCM

AES-GCM is implemented using PyCryptodome.

The benchmark uses a 256-bit AES key and a 128-bit authentication tag.

### ChaCha20-Poly1305

ChaCha20-Poly1305 is implemented using PyCryptodome.

The algorithm uses a 256-bit key and a 128-bit Poly1305 authentication tag.

---

## Test Data Sizes

Each algorithm is evaluated using the following plaintext sizes:

| Test | Size |
|---|---:|
| 1 KB | 1,024 bytes |
| 4 KB | 4,096 bytes |
| 16 KB | 16,384 bytes |
| 64 KB | 65,536 bytes |
| 256 KB | 262,144 bytes |
| 1 MB | 1,048,576 bytes |

Test data can be generated using:

```powershell
.\env1\Scripts\python.exe generate_test_data.py
```

The generated files are stored in:

```text
data/
```

---

## Benchmark Methodology

The benchmark runner evaluates both encryption and decryption for every algorithm and data size.

The benchmarking methodology includes:

- warm-up executions before recorded measurements;
- repeated timing measurements;
- high-resolution wall-clock timing using Python's performance counter;
- process CPU-time measurement;
- adaptive CPU measurement batching;
- process memory measurement;
- statistical analysis of repeated measurements;
- encryption and decryption throughput calculation.

Warm-up measurements are discarded and are not included in the final timing statistics.

The principal benchmark implementation is:

```text
benchmark/benchmark_runner.py
```

---

## Performance Metrics

For each algorithm, data size and operation, LightCryptBench records:

- mean execution time;
- median execution time;
- minimum execution time;
- maximum execution time;
- standard deviation;
- CPU time;
- CPU batching information;
- memory usage;
- throughput.

Benchmark results are exported to:

```text
results/benchmark_results.csv
```

The dataset contains the raw timing measurements as well as the calculated summary statistics.

---

## Running the Benchmark

From the project root:

```powershell
.\env1\Scripts\python.exe benchmark\benchmark_runner.py
```

The benchmark evaluates:

```text
3 algorithms
x 6 data sizes
x 2 operations
= 36 benchmark result groups
```

Each group contains repeated timing measurements.

---

## Benchmark Dataset Validation

The benchmark dataset can be independently checked using:

```powershell
.\env1\Scripts\python.exe validate_benchmark_results.py
```

The validator checks:

- the expected number of result groups;
- all expected algorithms;
- all expected data sizes;
- encryption and decryption results;
- the expected number of measurements;
- consistency between raw measurements and stored statistics.

---

## Benchmark Analysis

Basic benchmark analysis can be performed using:

```powershell
.\env1\Scripts\python.exe analyse_benchmark_results.py
```

Comparative analysis can be performed using:

```powershell
.\env1\Scripts\python.exe comparative_analysis.py
```

The comparative analysis evaluates algorithm performance across data sizes, including execution time, throughput and relative performance.

---

# Diffusion and Avalanche Analysis

LightCryptBench also performs controlled diffusion and avalanche experiments.

The analysis investigates the effect of changing a single input bit on the resulting ciphertext body and authentication tag.

Two experiment types are performed:

1. plaintext-bit flip;
2. key-bit flip.

For each algorithm and data size, 32 trials are performed for each experiment type.

This produces:

```text
3 algorithms
x 6 data sizes
x 2 experiment types
x 32 trials
= 1,152 observations
```

---

## Plaintext-Bit Experiment

A single plaintext bit is changed while the following remain fixed:

- cryptographic key;
- nonce;
- associated data.

The resulting encrypted output is compared with the baseline encryption.

The experiment separately measures changes in:

- ciphertext body;
- authentication tag.

Nonce reuse in this experiment occurs only as part of a controlled laboratory comparison and is not intended to represent correct operational AEAD usage.

---

## Key-Bit Experiment

A single key bit is changed while the following remain fixed:

- plaintext;
- nonce;
- associated data.

The resulting ciphertext body and authentication tag are compared with the baseline output.

This experiment measures the avalanche behaviour produced by changes to cryptographic key material.

---

## Hamming Distance

Diffusion is quantified using Hamming distance.

For two equal-length bit strings, the Hamming distance represents the number of bit positions at which the values differ.

The percentage of changed bits is calculated as:

```text
Change Percentage =
    (Hamming Distance / Total Number of Bits) x 100
```

Ciphertext-body and authentication-tag changes are analysed separately.

---

## Running the Diffusion Analysis

Run:

```powershell
.\env1\Scripts\python.exe diffusion_analysis.py
```

The complete diffusion dataset is exported to:

```text
results/diffusion_results.csv
```

---

## Diffusion Dataset Validation

Run:

```powershell
.\env1\Scripts\python.exe validate_diffusion_results.py
```

The validator checks the structure and integrity of the diffusion dataset, including the expected algorithms, data sizes, experiment types, trial counts, ciphertext lengths, authentication-tag lengths and change-percentage calculations.

A separate sanity test is available:

```powershell
.\env1\Scripts\python.exe test_diffusion_sanity.py
```

---

# Dissertation Figures

LightCryptBench automatically generates publication-quality figures for analysis and inclusion in the Evaluation and Results section of the dissertation.

## Performance Figures

Run:

```powershell
.\env1\Scripts\python.exe generate_benchmark_graphs.py
```

Figures are stored in:

```text
results/graphs/dissertation/
```

The performance figure set contains:

1. Encryption Throughput
2. Decryption Throughput
3. Encryption Execution Time
4. Decryption Execution Time
5. Encryption CPU Time per Byte
6. Decryption CPU Time per Byte
7. Encryption Timing Variability
8. Decryption Timing Variability
9. Encryption Memory Usage
10. Decryption Memory Usage
11. Encryption Speedup Relative to Ascon-AEAD128
12. Performance Heatmap

---

## Diffusion Figures

Run:

```powershell
.\env1\Scripts\python.exe generate_diffusion_graphs.py
```

Figures are stored in:

```text
results/graphs/diffusion/
```

The diffusion figure set contains:

13. Plaintext-to-Ciphertext Diffusion
14. Plaintext-to-Tag Avalanche
15. Key-to-Ciphertext Avalanche
16. Key-to-Tag Avalanche
17. Diffusion Heatmap
18. Key Avalanche Distribution

All dissertation figures are generated programmatically from the experimental datasets.

---

# Project Structure

```text
Benchmark102/
|
|-- algorithms/
|   `-- pyascon/
|
|-- benchmark/
|   |-- benchmark_runner.py
|   |-- test_aes.py
|   |-- test_ascon.py
|   `-- test_chacha.py
|
|-- data/
|   |-- test_1kb.bin
|   |-- test_4kb.bin
|   |-- test_16kb.bin
|   |-- test_64kb.bin
|   |-- test_256kb.bin
|   `-- test_1mb.bin
|
|-- results/
|   |-- benchmark_results.csv
|   |-- diffusion_results.csv
|   `-- graphs/
|       |-- dissertation/
|       `-- diffusion/
|
|-- algorithm_interface.py
|-- ascon_algorithm.py
|-- aes_gcm_algorithm.py
|-- chacha20_poly1305_algorithm.py
|
|-- analyse_benchmark_results.py
|-- comparative_analysis.py
|-- diffusion_analysis.py
|
|-- generate_test_data.py
|-- generate_benchmark_graphs.py
|-- generate_diffusion_graphs.py
|
|-- validate_benchmark_results.py
|-- validate_diffusion_results.py
|
|-- test_ciphertext_structure.py
|-- test_cpu_batching.py
|-- test_cpu_time_measurement.py
|-- test_diffusion_sanity.py
|-- test_memory_measurement.py
|-- test_throughput_calculation.py
|
|-- requirements.txt
`-- README.md
```

---

# Installation

A Python virtual environment is recommended.

Create a virtual environment:

```powershell
python -m venv env1
```

Install the required dependencies:

```powershell
.\env1\Scripts\python.exe -m pip install -r requirements.txt
```

The principal Python dependencies are:

- Matplotlib
- NumPy
- pandas
- psutil
- PyCryptodome

The Ascon implementation is included locally within the project.

---

# Reproducing the Experiment

A typical experimental workflow is:

```powershell
.\env1\Scripts\python.exe generate_test_data.py

.\env1\Scripts\python.exe benchmark\benchmark_runner.py

.\env1\Scripts\python.exe validate_benchmark_results.py

.\env1\Scripts\python.exe analyse_benchmark_results.py

.\env1\Scripts\python.exe comparative_analysis.py

.\env1\Scripts\python.exe generate_benchmark_graphs.py

.\env1\Scripts\python.exe test_diffusion_sanity.py

.\env1\Scripts\python.exe diffusion_analysis.py

.\env1\Scripts\python.exe validate_diffusion_results.py

.\env1\Scripts\python.exe generate_diffusion_graphs.py
```

This workflow regenerates the test data, benchmark dataset, comparative analysis, diffusion dataset and dissertation figures.

---

# Reproducibility

Cryptographic benchmark results are influenced by the execution environment, including:

- processor architecture;
- processor frequency and scheduling;
- operating system;
- Python version;
- cryptographic library implementation;
- hardware acceleration;
- background system activity.

Consequently, exact timing values may differ when the experiments are repeated on different systems.

The repository retains the experimental datasets used for analysis so that the reported results can be examined independently of subsequent benchmark runs.

---

# Research Scope

LightCryptBench is intended as an experimental research and educational framework.

Performance measurements compare the tested Python-accessible implementations in the experimental environment. They should not be interpreted as universal performance rankings of the underlying cryptographic algorithms across all hardware, software or implementation environments.

In particular, implementation language, optimisation level and hardware acceleration can substantially affect measured performance.

---

# Licence

This repository contains third-party cryptographic implementation code under its respective licence terms. Refer to the relevant source files and third-party directories for applicable licensing information.