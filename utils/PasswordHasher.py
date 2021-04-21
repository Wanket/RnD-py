from hashlib import sha256


class PasswordHasher:
    @staticmethod
    def get_hash(salt: bytes, password: str) -> bytes:
        return sha256(sha256(password.encode("utf-8")).digest() + salt).digest()
