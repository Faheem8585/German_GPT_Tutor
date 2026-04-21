from __future__ import annotations

import re
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings
from app.core.exceptions import AuthenticationError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Prompt injection patterns — detect attempts to override system instructions
_INJECTION_PATTERNS = [
    r"ignore\s+(previous|all|prior)\s+(instructions|prompts|rules)",
    r"you\s+are\s+now\s+a",
    r"pretend\s+(you\s+are|to\s+be)",
    r"act\s+as\s+(if\s+you\s+are|a)",
    r"disregard\s+(your|all)\s+(instructions|guidelines)",
    r"reveal\s+(your|the)\s+(system|hidden)\s+prompt",
    r"jailbreak",
    r"DAN\s+mode",
    r"<\s*script\s*>",
]
_INJECTION_RE = re.compile("|".join(_INJECTION_PATTERNS), re.IGNORECASE)

# PII patterns for masking in logs
_PII_PATTERNS = {
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
    "phone": re.compile(r"\b(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
    "iban": re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}\b"),
}


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(subject: str | int, extra: dict[str, Any] | None = None) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {
        "sub": str(subject),
        "iat": now,
        "exp": expire,
        "jti": str(uuid.uuid4()),
        **(extra or {}),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except JWTError as e:
        raise AuthenticationError(f"Invalid token: {e}") from e


def detect_prompt_injection(text: str) -> bool:
    """Return True if text contains a suspected prompt injection attempt."""
    return bool(_INJECTION_RE.search(text))


def mask_pii(text: str) -> str:
    """Mask PII before logging or storing in analytics."""
    for pii_type, pattern in _PII_PATTERNS.items():
        labels = {"email": "[EMAIL]", "phone": "[PHONE]", "iban": "[IBAN]"}
        text = pattern.sub(labels[pii_type], text)
    return text


def sanitize_user_input(text: str, max_length: int = 4096) -> str:
    """Strip dangerous characters and enforce length limits."""
    # Remove null bytes
    text = text.replace("\x00", "")
    # Limit length
    text = text[:max_length]
    return text.strip()
