from Crypto.Cipher import AES


print("Testing AES-GCM")
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
cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)

cipher.update(associated_data)

ciphertext, tag = cipher.encrypt_and_digest(plaintext)

print("Plaintext: ", plaintext)
print("Ciphertext:", ciphertext.hex())
print("Tag:       ", tag.hex())

# Decrypt
decipher = AES.new(key, AES.MODE_GCM, nonce=nonce)

decipher.update(associated_data)

decrypted = decipher.decrypt_and_verify(ciphertext, tag)

print("Decrypted: ", decrypted)

# Verify
if decrypted == plaintext:
    print()
    print("SUCCESS: AES-GCM encryption/decryption works.")
else:
    print()
    print("ERROR: Decrypted data does not match original plaintext.")
