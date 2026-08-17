from Crypto.Cipher import ChaCha20_Poly1305

from algorithm_interface import CryptoAlgorithm


class ChaCha20Poly1305(CryptoAlgorithm):
    """ChaCha20-Poly1305 implementation for LightCryptBench."""

    TAG_LENGTH = 16

    @property
    def name(self):
        return "ChaCha20-Poly1305"

    def generate_key(self):
        return bytes(32)

    def encrypt(self, key, nonce, plaintext, aad=b""):
        cipher = ChaCha20_Poly1305.new(
            key=key,
            nonce=nonce
        )

        cipher.update(aad)

        ciphertext, tag = cipher.encrypt_and_digest(plaintext)

        return ciphertext + tag

    def decrypt(self, key, nonce, ciphertext, aad=b""):
        cipher = ChaCha20_Poly1305.new(
            key=key,
            nonce=nonce
        )

        cipher.update(aad)

        actual_ciphertext = ciphertext[:-self.TAG_LENGTH]
        tag = ciphertext[-self.TAG_LENGTH:]

        return cipher.decrypt_and_verify(
            actual_ciphertext,
            tag
        )
