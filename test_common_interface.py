from ascon_algorithm import AsconAEAD128
from aes_gcm_algorithm import AESGCM
from chacha20_poly1305_algorithm import ChaCha20Poly1305


print("Testing common interface")
print("=" * 60)

algorithms = [
    AsconAEAD128(),
    AESGCM(),
    ChaCha20Poly1305()
]

plaintext = b"Hello from LightCryptBench!"
aad = b""

for algorithm in algorithms:

    print()
    print("Algorithm:", algorithm.name)
    print("-" * 60)

    key = algorithm.generate_key()

    # Both Ascon-AEAD128 and the PyCryptodome implementations
    # use a 12- or 16-byte nonce depending on the algorithm.
    if algorithm.name == "Ascon-AEAD128":
        nonce = bytes(16)
    else:
        nonce = bytes(12)

    ciphertext = algorithm.encrypt(
        key,
        nonce,
        plaintext,
        aad
    )

    decrypted = algorithm.decrypt(
        key,
        nonce,
        ciphertext,
        aad
    )

    print("Encryption completed.")
    print("Decryption completed.")

    if decrypted == plaintext:
        print("SUCCESS:", algorithm.name)
    else:
        print("ERROR:", algorithm.name)

print()
print("=" * 60)
print("Common interface test complete.")


