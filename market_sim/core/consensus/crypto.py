from dataclasses import dataclass
from typing import Tuple

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization


@dataclass(frozen=True)
class Ed25519KeyPair:
    private_key: Ed25519PrivateKey
    public_key: Ed25519PublicKey

    @staticmethod
    def generate() -> "Ed25519KeyPair":
        priv = Ed25519PrivateKey.generate()
        pub = priv.public_key()
        return Ed25519KeyPair(private_key=priv, public_key=pub)

    def sign(self, message: bytes) -> bytes:
        return self.private_key.sign(message)


def verify_signature(public_key: Ed25519PublicKey, message: bytes, signature: bytes) -> bool:
    try:
        public_key.verify(signature, message)
        return True
    except Exception:
        return False


def serialize_public_key(public_key: Ed25519PublicKey) -> bytes:
    return public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


def deserialize_public_key(data: bytes) -> Ed25519PublicKey:
    return Ed25519PublicKey.from_public_bytes(data) 