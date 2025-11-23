"""
Validation Utilities
Input validation for x402 protocol
"""

import re
from typing import Optional


def is_valid_solana_address(address: str) -> bool:
    """
    Validate Solana wallet address

    Args:
        address: Wallet address to validate

    Returns:
        True if valid
    """
    if not address:
        return False

    # Solana addresses are base58 encoded, 32-44 characters
    if len(address) < 32 or len(address) > 44:
        return False

    # Basic base58 character check
    base58_pattern = re.compile(r'^[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]+$')
    return bool(base58_pattern.match(address))


def is_valid_amount(amount_str: str) -> tuple[bool, Optional[str]]:
    """
    Validate payment amount

    Args:
        amount_str: Amount string to validate

    Returns:
        (is_valid, error_message)
    """
    try:
        amount = int(amount_str)
        if amount <= 0:
            return False, "Amount must be positive"
        if amount > 10**18:  # Reasonable upper limit
            return False, "Amount too large"
        return True, None
    except ValueError:
        return False, "Amount must be a valid integer"


def is_valid_timeout(timeout: int) -> tuple[bool, Optional[str]]:
    """
    Validate timeout value

    Args:
        timeout: Timeout in seconds

    Returns:
        (is_valid, error_message)
    """
    if timeout < 1:
        return False, "Timeout must be at least 1 second"
    if timeout > 3600:  # Max 1 hour
        return False, "Timeout cannot exceed 1 hour"
    return True, None


def is_valid_url(url: str) -> bool:
    """
    Validate URL format

    Args:
        url: URL to validate

    Returns:
        True if valid
    """
    if not url:
        return False

    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    return bool(url_pattern.match(url))


def sanitize_string(s: str, max_length: int = 500) -> str:
    """
    Sanitize string input

    Args:
        s: String to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized string
    """
    if not s:
        return ""

    # Trim to max length
    s = s[:max_length]

    # Remove potentially dangerous characters
    # Keep alphanumeric, spaces, and common punctuation
    s = re.sub(r'[^\w\s\-.,!?@#$%&*()+=\[\]{}:;\'\"<>/\\]', '', s)

    return s.strip()
