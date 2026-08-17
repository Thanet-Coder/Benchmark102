from Crypto.Cipher import ChaCha20_Poly1305


print("Testing ChaCha20-Poly1305")
print("-" * 30)

# Test key
key = bytes(32)

# Test nonce
nonce = bytes(12)

# Test plaintext
plaintext = b"Hello from LightCryptBench!"

# No associated data for this basic test
associated_data = b""

# Encrypt
cipher = ChaCha20_Poly1305.new(key=key, nonce=nonce)

cipher.update(associated_data)

ciphertext, tag = cipher.encrypt_and_digest(plaintext)

print("Plaintext: ", plaintext)
print("Ciphertext:", ciphertext.hex())
print("Tag:       ", tag.hex())

# Decrypt
decipher = ChaCha20_Poly1305.new(key=key, nonce=nonce)

decipher.update(associated_data)

decrypted = decipher.decrypt_and_verify(ciphertext, tag)

print("Decrypted: ", decrypted)

# Verify
if decrypted == plaintext:
    print()
    print("SUCCESS: ChaCha20-Poly1305 encryption/decryption works.")
else:
    print()
    print("ERROR: Decrypted data does not match original plaintext.")
