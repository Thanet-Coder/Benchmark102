import sys

# Allow Python to find the Ascon reference implementation
sys.path.insert(0, "algorithms/pyascon")

import ascon


print("Testing Ascon-AEAD128")
print("-" * 30)

# Test key and nonce
key = bytes(16)
nonce = bytes(16)

# Test plaintext
plaintext = b"Hello from LightCryptBench!"

# No associated data for this basic test
associated_data = b""

# Encrypt
ciphertext = ascon.ascon_encrypt(
    key,
    nonce,
    associated_data,
    plaintext,
    variant="Ascon-AEAD128"
)

print("Plaintext: ", plaintext)
print("Ciphertext:", ciphertext.hex())

# Decrypt
decrypted = ascon.ascon_decrypt(
    key,
    nonce,
    associated_data,
    ciphertext,
    variant="Ascon-AEAD128"
)

print("Decrypted: ", decrypted)

# Verify
if decrypted == plaintext:
    print()
    print("SUCCESS: Ascon-AEAD128 encryption/decryption works.")
else:
    print()
    print("ERROR: Decrypted data does not match original plaintext.")
