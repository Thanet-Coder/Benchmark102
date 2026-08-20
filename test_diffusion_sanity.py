from diffusion_analysis import (
    flip_bit,
    hamming_distance_bytes,
    calculate_change_percent,
    split_ciphertext_and_tag
)

from ascon_algorithm import AsconAEAD128
from aes_gcm_algorithm import AESGCM
from chacha20_poly1305_algorithm import ChaCha20Poly1305


print("=" * 70)
print("LightCryptBench Diffusion Sanity Test")
print("=" * 70)


# ============================================================
# Test 1 - Flip exactly one bit
# ============================================================

original = bytes([0b00000000])

modified = flip_bit(
    original,
    0
)

distance = hamming_distance_bytes(
    original,
    modified
)

print()
print("Test 1: Single-bit flip")
print(f"Original byte: {original[0]:08b}")
print(f"Modified byte: {modified[0]:08b}")
print(f"Hamming distance: {distance}")

assert distance == 1

print("PASS")


# ============================================================
# Test 2 - Flip a different bit
# ============================================================

modified = flip_bit(
    original,
    7
)

distance = hamming_distance_bytes(
    original,
    modified
)

print()
print("Test 2: High-bit flip")
print(f"Original byte: {original[0]:08b}")
print(f"Modified byte: {modified[0]:08b}")
print(f"Hamming distance: {distance}")

assert distance == 1

print("PASS")


# ============================================================
# Test 3 - Known Hamming distance
# ============================================================

first = bytes([
    0b00000000
])

second = bytes([
    0b11111111
])

distance = hamming_distance_bytes(
    first,
    second
)

print()
print("Test 3: Known Hamming distance")
print(f"Expected: 8 bits")
print(f"Actual:   {distance} bits")

assert distance == 8

print("PASS")


# ============================================================
# Test 4 - Percentage calculation
# ============================================================

percentage = calculate_change_percent(
    4,
    8
)

print()
print("Test 4: Change percentage")
print("Expected: 50.00%")
print(f"Actual:   {percentage:.2f}%")

assert abs(
    percentage - 50.0
) < 0.000001

print("PASS")


# ============================================================
# Test 5 - Verify AEAD structure
# ============================================================

algorithms = [
    AsconAEAD128(),
    AESGCM(),
    ChaCha20Poly1305()
]

plaintext = bytes(32)
associated_data = b""


print()
print("=" * 70)
print("AEAD Output Structure Check")
print("=" * 70)


for algorithm in algorithms:

    key = algorithm.generate_key()

    if algorithm.name == "Ascon-AEAD128":
        nonce = bytes(16)
    else:
        nonce = bytes(12)

    encrypted = algorithm.encrypt(
        key,
        nonce,
        plaintext,
        associated_data
    )

    (
        ciphertext,
        tag
    ) = split_ciphertext_and_tag(
        encrypted
    )

    print()
    print(f"Algorithm:         {algorithm.name}")
    print(f"Ciphertext length: {len(ciphertext)} bytes")
    print(f"Tag length:        {len(tag)} bytes")

    assert len(ciphertext) == 32
    assert len(tag) == 16

    print("PASS")


# ============================================================
# Test 6 - Plaintext one-bit sensitivity
# ============================================================

print()
print("=" * 70)
print("Plaintext One-Bit Sensitivity Check")
print("=" * 70)


for algorithm in algorithms:

    key = algorithm.generate_key()

    if algorithm.name == "Ascon-AEAD128":
        nonce = bytes(16)
    else:
        nonce = bytes(12)

    baseline_plaintext = bytes(32)

    modified_plaintext = flip_bit(
        baseline_plaintext,
        0
    )

    baseline_output = algorithm.encrypt(
        key,
        nonce,
        baseline_plaintext,
        associated_data
    )

    modified_output = algorithm.encrypt(
        key,
        nonce,
        modified_plaintext,
        associated_data
    )

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

    ciphertext_difference = (
        hamming_distance_bytes(
            baseline_ciphertext,
            modified_ciphertext
        )
    )

    tag_difference = (
        hamming_distance_bytes(
            baseline_tag,
            modified_tag
        )
    )

    ciphertext_percentage = (
        calculate_change_percent(
            ciphertext_difference,
            len(baseline_ciphertext) * 8
        )
    )

    tag_percentage = (
        calculate_change_percent(
            tag_difference,
            len(baseline_tag) * 8
        )
    )

    print()
    print(f"Algorithm: {algorithm.name}")

    print(
        f"Ciphertext changed bits: "
        f"{ciphertext_difference}"
    )

    print(
        f"Ciphertext change: "
        f"{ciphertext_percentage:.2f}%"
    )

    print(
        f"Tag changed bits: "
        f"{tag_difference}"
    )

    print(
        f"Tag change: "
        f"{tag_percentage:.2f}%"
    )

    assert ciphertext_difference >= 1
    assert tag_difference >= 1

    print("PASS")


# ============================================================
# Complete
# ============================================================

print()
print("=" * 70)
print("Diffusion sanity test complete.")
print("=" * 70)

print()
print("SUCCESS: All diffusion sanity checks passed.")
