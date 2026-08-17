from chacha20_poly1305_algorithm import ChaCha20Poly1305


print("Testing ChaCha20-Poly1305 through common interface")
print("-" * 50)

# Create ChaCha20-Poly1305 algorithm object
algorithm = ChaCha20Poly1305()

print("Algorithm:", algorithm.name)

# Generate key
key = algorithm.generate_key()

# Test nonce
nonce = bytes(12)

# Test plaintext
plaintext = b"Hello from LightCryptBench!"

# No associated data
aad = b""

# Encrypt
ciphertext = algorithm.encrypt(
    key,
    nonce,
    plaintext,
    aad
)

print("Plaintext: ", plaintext)
print("Ciphertext:", ciphertext.hex())

# Decrypt
decrypted = algorithm.decrypt(
    key,
    nonce,
    ciphertext,
    aad
)

print("Decrypted: ", decrypted)

# Verify
if decrypted == plaintext:
    print()
    print("SUCCESS: ChaCha20-Poly1305 works through the common interface.")
else:
    print()
    print("ERROR: Decrypted data does not match original plaintext.")

