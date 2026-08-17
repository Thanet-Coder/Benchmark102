from ascon_algorithm import AsconAEAD128


print("Testing Ascon-AEAD128 through common interface")
print("-" * 50)

# Create Ascon algorithm object
algorithm = AsconAEAD128()

print("Algorithm:", algorithm.name)

# Generate key
key = algorithm.generate_key()

# Test nonce
nonce = bytes(16)

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
    print("SUCCESS: Ascon-AEAD128 works through the common interface.")
else:
    print()
    print("ERROR: Decrypted data does not match original plaintext.")
