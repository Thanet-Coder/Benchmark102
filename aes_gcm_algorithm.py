from Crypto.Cipher import AES

from algorithm_interface import CryptoAlgorithm


class AESGCM(CryptoAlgorithm):
    """AES-GCM implementation for LightCryptBench."""

    TAG_LENGTH = 16

    @property
    def name(self):
        return "AES-GCM"

    def generate_key(self):
        return bytes(32)

    def encrypt(self, key, nonce, plaintext, aad=b""):
        cipher = AES.new(
            key,
            AES.MODE_GCM,
            nonce=nonce
        )

        cipher.update(aad)

        ciphertext, tag = cipher.encrypt_and_digest(plaintext)

        return ciphertext + tag

    def decrypt(self, key, nonce, ciphertext, aad=b""):
        cipher = AES.new(
            key,
            AES.MODE_GCM,
            nonce=nonce
        )

        cipher.update(aad)

        actual_ciphertext = ciphertext[:-self.TAG_LENGTH]
        tag = ciphertext[-self.TAG_LENGTH:]

        return cipher.decrypt_and_verify(
            actual_ciphertext,
            tag
        )
