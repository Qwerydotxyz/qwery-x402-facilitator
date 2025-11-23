"""
SPL Token Helper Functions
Handles USDC/USDT transfers
"""

from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from solders.system_program import ID as SYSTEM_PROGRAM_ID
import struct

# SPL Token Program ID
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")

# Token Mints
USDC_MINT = Pubkey.from_string("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")
USDT_MINT = Pubkey.from_string("Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB")

TOKEN_DECIMALS = {
    "USDC": 6,
    "USDT": 6,
    "SOL": 9
}


def get_associated_token_address(owner: Pubkey, mint: Pubkey) -> Pubkey:
    """
    Get associated token account address
    Derived deterministically from owner + mint
    """
    ASSOCIATED_TOKEN_PROGRAM_ID = Pubkey.from_string(
        "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL"
    )
    
    seeds = [
        bytes(owner),
        bytes(TOKEN_PROGRAM_ID),
        bytes(mint)
    ]
    
    # Find PDA
    address, _ = Pubkey.find_program_address(seeds, ASSOCIATED_TOKEN_PROGRAM_ID)
    return address


def create_transfer_checked_instruction(
    source: Pubkey,
    mint: Pubkey,
    destination: Pubkey,
    owner: Pubkey,
    amount: int,
    decimals: int
) -> Instruction:
    """
    Create SPL token transfer_checked instruction
    """
    # Instruction data: [12, amount (u64), decimals (u8)]
    data = struct.pack("<BQB", 12, amount, decimals)
    
    keys = [
        AccountMeta(pubkey=source, is_signer=False, is_writable=True),
        AccountMeta(pubkey=mint, is_signer=False, is_writable=False),
        AccountMeta(pubkey=destination, is_signer=False, is_writable=True),
        AccountMeta(pubkey=owner, is_signer=True, is_writable=False),
    ]
    
    return Instruction(
        program_id=TOKEN_PROGRAM_ID,
        accounts=keys,
        data=data
    )


def create_associated_token_account_instruction(
    payer: Pubkey,
    owner: Pubkey,
    mint: Pubkey
) -> Instruction:
    """
    Create associated token account instruction
    """
    ASSOCIATED_TOKEN_PROGRAM_ID = Pubkey.from_string(
        "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL"
    )
    
    associated_token_address = get_associated_token_address(owner, mint)
    
    keys = [
        AccountMeta(pubkey=payer, is_signer=True, is_writable=True),
        AccountMeta(pubkey=associated_token_address, is_signer=False, is_writable=True),
        AccountMeta(pubkey=owner, is_signer=False, is_writable=False),
        AccountMeta(pubkey=mint, is_signer=False, is_writable=False),
        AccountMeta(pubkey=SYSTEM_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    
    return Instruction(
        program_id=ASSOCIATED_TOKEN_PROGRAM_ID,
        accounts=keys,
        data=bytes([])
    )


def get_token_mint(token: str) -> Pubkey:
    """Get token mint address"""
    if token.upper() == "USDC":
        return USDC_MINT
    elif token.upper() == "USDT":
        return USDT_MINT
    else:
        raise ValueError(f"Unsupported token: {token}")
