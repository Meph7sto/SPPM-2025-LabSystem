from __future__ import annotations

import base64
import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone

import jwt

from .config import settings

_HASH_NAME = "sha256"
_ITERATIONS = 100_000


def hash_password(password: str) -> str:
    """
    使用 PBKDF2 HMAC SHA256 算法对密码进行哈希。
    生成随机盐，并将其与哈希值一起保存。
    """
    salt = os.urandom(16)
    derived = hashlib.pbkdf2_hmac(
        _HASH_NAME,
        password.encode("utf-8"),
        salt,
        _ITERATIONS,
    )
    return "{}${}".format(
        base64.urlsafe_b64encode(salt).decode("ascii"),
        base64.urlsafe_b64encode(derived).decode("ascii"),
    )


def get_password_hash(password: str) -> str:
    """
    获取密码哈希值的辅助函数。
    """
    return hash_password(password)


def verify_password(password: str, stored_hash: str) -> bool:
    """
    验证提供的密码是否与存储的哈希值匹配。
    """
    try:
        salt_b64, digest_b64 = stored_hash.split("$", 1)
    except ValueError:
        return False
    salt = base64.urlsafe_b64decode(salt_b64.encode("ascii"))
    expected = base64.urlsafe_b64decode(digest_b64.encode("ascii"))
    derived = hashlib.pbkdf2_hmac(
        _HASH_NAME,
        password.encode("utf-8"),
        salt,
        _ITERATIONS,
    )
    # 使用常量时间比较以防止时序攻击
    return hmac.compare_digest(derived, expected)


def create_access_token(
    subject: str,
    role: str,
    borrower_type: str | None,
    expires_minutes: int,
) -> str:
    """
    创建 JWT 访问令牌。
    Payload 包含主题(sub)、角色(role)、借阅者类型(borrower_type)、签发时间(iat)和过期时间(exp)。
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "role": role,
        "borrower_type": borrower_type,
        "iat": now,
        "exp": now + timedelta(minutes=expires_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def decode_access_token(token: str) -> dict:
    """
    解码 JWT 访问令牌，验证签名。
    """
    return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
