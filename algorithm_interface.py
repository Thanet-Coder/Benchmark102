from abc import ABC, abstractmethod


class CryptoAlgorithm(ABC):
    """Common interface for authenticated encryption algorithms."""

    @property
    @abstractmethod
    def name(self):
        """Return the algorithm name."""
        pass

    @abstractmethod
    def generate_key(self):
        """Generate and return a cryptographic key."""
        pass

    @abstractmethod
    def encrypt(self, key, nonce, plaintext, aad=b""):
        """Encrypt plaintext and return ciphertext with authentication tag."""
        pass

    @abstractmethod
    def decrypt(self, key, nonce, ciphertext, aad=b""):
        """Decrypt ciphertext and return plaintext."""
        pass
