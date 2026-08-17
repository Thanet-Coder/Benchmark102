import sys

from algorithm_interface import CryptoAlgorithm

# Allow Python to find the Ascon reference implementation
sys.path.insert(0, "algorithms/pyascon")

import ascon


class AsconAEAD128(CryptoAlgorithm):
    """Ascon-AEAD128 implementation for LightCryptBench."""

    @property
    def name(self):
        return "Ascon-AEAD128"

    def generate_key(self):
        return bytes(16)

    def encrypt(self, key, nonce, plaintext, aad=b""):
        return ascon.ascon_encrypt(
            key,
            nonce,
            aad,
            plaintext,
            variant="Ascon-AEAD128"
        )

    def decrypt(self, key, nonce, ciphertext, aad=b""):
        return ascon.ascon_decrypt(
            key,
            nonce,
            aad,
            ciphertext,
            variant="Ascon-AEAD128"
        )
