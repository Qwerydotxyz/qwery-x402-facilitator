"""
Encoding/Decoding Utilities
Base64 encoding for x402 headers
"""

import base64
import json
from typing import Dict, Any


def encode_x402_header(data: Dict[str, Any]) -> str:
    """
    Encode data for x402 header (base64)

    Args:
        data: Dictionary to encode

    Returns:
        Base64-encoded string
    """
    json_str = json.dumps(data)
    return base64.b64encode(json_str.encode()).decode()


def decode_x402_header(header: str) -> Dict[str, Any]:
    """
    Decode x402 header from base64

    Args:
        header: Base64-encoded header string

    Returns:
        Decoded dictionary
    """
    decoded = base64.b64decode(header.encode()).decode()
    return json.loads(decoded)


def create_payment_response_header(
    success: bool,
    transaction: str = None,
    network: str = None,
    payer: str = None,
    error_reason: str = None
) -> str:
    """
    Create X-PAYMENT-RESPONSE header

    Args:
        success: Whether payment succeeded
        transaction: Transaction hash
        network: Network name
        payer: Payer address
        error_reason: Error reason if failed

    Returns:
        Base64-encoded header value
    """
    response_data = {
        "success": success,
    }

    if transaction:
        response_data["transaction"] = transaction
    if network:
        response_data["network"] = network
    if payer:
        response_data["payer"] = payer
    if error_reason:
        response_data["errorReason"] = error_reason

    return encode_x402_header(response_data)
