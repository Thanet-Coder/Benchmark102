from ascon_algorithm import AsconAEAD128
from aes_gcm_algorithm import AESGCM
from chacha20_poly1305_algorithm import ChaCha20Poly1305


print("=" * 60)
print("LightCryptBench Ciphertext Structure Test")
print("=" * 60)


algorithms = [
    AsconAEAD128(),
    AESGCM(),
    ChaCha20Poly1305()
]


plaintext = bytes(32)
associated_data = b""


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

    print()
    print(f"Algorithm:          {algorithm.name}")
    print(f"Plaintext length:   {len(plaintext)} bytes")
    print(f"Encrypted length:   {len(encrypted)} bytes")
    print(
        f"Additional bytes:   "
        f"{len(encrypted) - len(plaintext)} bytes"
    )


print()
print("=" * 60)
print("Ciphertext structure test complete.")
print("=" * 60)
