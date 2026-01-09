from __future__ import annotations

import base64
import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone

import jwt

from .config import settings

# 密码哈希算法配置
_HASH_NAME = "sha256"
_ITERATIONS = 100_000  # PBKDF2 迭代次数，越高越安全但越慢


def hash_password(password: str) -> str:
    """
    对明文密码进行安全哈希。

    使用 PBKDF2 HMAC SHA256 算法。

    Process:
    1. 生成 16 字节的随机盐 (salt)。
    2. 使用盐和密码进行 100,000 次迭代哈希计算。
    3. 将盐和哈希结果分别进行 Base64 编码。
    4. 拼接成 `salt$hash` 格式存储。

    Args:
        password (str): 明文密码。

    Returns:
        str: 存储用的哈希字符串 (格式: salt_b64$hash_b64)。
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
    直接调用 hash_password。
    """
    return hash_password(password)


def verify_password(password: str, stored_hash: str) -> bool:
    """
    验证提供的明文密码是否与存储的哈希值匹配。

    Args:
        password (str): 待验证的明文密码。
        stored_hash (str): 数据库中存储的密码哈希字符串。

    Returns:
        bool: 如果匹配返回 True，否则返回 False。
    """
    try:
        # 分离盐和哈希值
        salt_b64, digest_b64 = stored_hash.split("$", 1)
    except ValueError:
        # 格式不正确，验证失败
        return False

    # 解码 Base64
    salt = base64.urlsafe_b64decode(salt_b64.encode("ascii"))
    expected = base64.urlsafe_b64decode(digest_b64.encode("ascii"))

    # 使用相同的参数重新计算哈希
    derived = hashlib.pbkdf2_hmac(
        _HASH_NAME,
        password.encode("utf-8"),
        salt,
        _ITERATIONS,
    )

    # 使用常量时间比较 (hmac.compare_digest) 以防止时序攻击 (Timing Attacks)
    return hmac.compare_digest(derived, expected)


def create_access_token(
    subject: str,
    role: str,
    borrower_type: str | None,
    expires_minutes: int,
) -> str:
    """
    创建 JWT (JSON Web Token) 访问令牌。

    Args:
        subject (str): 令牌主题，通常是用户 ID。
        role (str): 用户角色。
        borrower_type (str | None): 借阅者类型 (如果由)。
        expires_minutes (int): 令牌有效期（分钟）。

    Returns:
        str: 编码后的 JWT 字符串。
    """
    now = datetime.now(timezone.utc)
    # 构建 Payload
    payload = {
        "sub": subject,          # Subject: 用户 ID
        "role": role,            # Custom claim: 角色
        "borrower_type": borrower_type, # Custom claim: 借阅者类型
        "iat": now,              # Issued At: 签发时间
        "exp": now + timedelta(minutes=expires_minutes), # Expiration Time: 过期时间
    }
    # 使用 HS256 算法和密钥进行签名
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def decode_access_token(token: str) -> dict:
    """
    解码并验证 JWT 访问令牌。

    检查签名是否正确以及令牌是否过期。

    Args:
        token (str): JWT 字符串。

    Returns:
        dict: 解码后的 Payload 字典。

    Raises:
        jwt.InvalidTokenError: 如果令牌无效或过期。
    """
    return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
