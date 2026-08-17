from aes_gcm_algorithm import AESGCM


print("Testing AES-GCM through common interface")
print("-" * 50)

# Create AES-GCM algorithm object
algorithm = AESGCM()

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
    print("SUCCESS: AES-GCM works through the common interface.")
else:
    print()
    print("ERROR: Decrypted data does not match original plaintext.")
