# Qwery x402 Facilitator

Production-ready payment facilitator for Solana implementing the x402 HTTP payment protocol.

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/) [![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg)](https://fastapi.tiangolo.com) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Contents
- Features
- Quick start
  - Prerequisites
  - Installation
  - Configuration
  - Running the service
- API overview
- Architecture
- Security considerations
- Testing
- Documentation
- Contributing
- License
- Links & support
- Acknowledgments

## Features

- Multi-token support: SOL, USDC, USDT and any SPL token.
- Zero user fees: facilitator covers network fees.
- Fast settlement: sub-second confirmation on Solana.
- x402-compatible: conforms to the x402 HTTP payments standard.
- Token gating: gate access or membership tiers by token holdings.
- Production-grade: deployed and tested on Solana mainnet.

## Quick start

### Prerequisites

- Python 3.11+
- A Solana wallet with SOL for network fees
- Basic familiarity with Solana transactions and SPL tokens

### Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/Qwerydotxyz/qwery-x402-facilitator.git
cd qwery-x402-facilitator

python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

Copy the example environment file and provide your secrets:

```bash
cp .env.example .env
# Edit .env and set FACILITATOR_PRIVATE_KEY and other values
```

### Configuration

Create or update .env with the following variables (examples):

```env
FACILITATOR_PRIVATE_KEY=your_base58_private_key
FACILITATOR_SERVICE_FEE=0.00
FACILITATOR_MIN_BALANCE=100000
LOG_LEVEL=INFO
CORS_ORIGINS=*
```

- FACILITATOR_PRIVATE_KEY must be stored securely. Do not commit to source control.
- FACILITATOR_MIN_BALANCE is in lamports (1 SOL = 1e9 lamports) unless otherwise documented.

### Run locally

Development:

```bash
python main.py
```

Production (example using uvicorn):

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

- API default: http://localhost:8000
- Interactive OpenAPI docs: http://localhost:8000/docs

## API overview

This section provides sample request payloads and endpoints. Consult the running service's OpenAPI docs for full, up-to-date API details.

Create a payment
POST /create-payment

Request example:
```json
{
  "payer": "wallet_address",
  "amount": 100000,
  "token": "SOL",
  "network": "solana"
}
```

Settle a payment
POST /settle

Request example:
```json
{
  "signed_transaction": "base64_encoded...",
  "network": "solana"
}
```

Check wallet status
GET /wallet-status?network=solana

Token gating (membership access)
POST /token-gate/check-access

Request example:
```json
{
  "wallet_address": "...",
  "required_token": "EPjFWdd...",
  "required_amount": 1000000
}
```

## Architecture

Project layout (high level):

```
├── app/
│   ├── api/          # API endpoints
│   ├── models/       # Data models and schemas
│   ├── services/     # Business logic and integrations
│   └── utils/        # Utilities and helpers
├── main.py           # Application entry point
└── requirements.txt  # Python dependencies
```

Key responsibilities:
- API layer: request validation and HTTP surface (FastAPI)
- Services: signing, x402 compliance, token/gateway logic, interactions with Solana RPC
- Utilities: configuration, logging, rate limiting and metrics

## Security considerations

- Private keys: store in environment variables or a secure secret store. Never check private keys into version control.
- Partial signing: users retain custody; the facilitator assists with settlement.
- Transport: use HTTPS in production for all endpoints.
- Rate limiting: recommended to mitigate abuse (e.g., 100 requests/min per IP as an operational guideline).
- Monitoring & alerts: track key metrics (wallet balance, failed settlements, RPC errors).

## Testing

Health and basic checks:

```bash
# Health endpoint
curl http://localhost:8000/health

# Wallet status
curl http://localhost:8000/wallet-status?network=solana
```

Run test suite:

```bash
pytest tests/
```

Ensure you have test keys and a test environment separate from production before running end-to-end tests.

## Documentation

- Local docs directory: ./docs/
- API reference (live): https://facilitator.qwery.xyz/docs
- Whitepaper and design notes: ./docs/whitepaper.txt

## Contributing

Contributions are welcome. Suggested workflow:

1. Fork the repository.
2. Create a feature branch: git checkout -b feature/your-feature.
3. Commit changes with clear messages.
4. Push the branch and open a Pull Request.

Please include tests and update documentation for new behavior or configuration.

## License

This project is licensed under the MIT License. See LICENSE for details.

## Links & support

- Website: https://qwery.xyz
- Live API: https://facilitator.qwery.xyz
- Documentation: https://facilitator.qwery.xyz/docs
- GitHub: https://github.com/Qwerydotxyz
- Support email: support@qwery.xyz
- Community: https://discord.gg/qwery

## Acknowledgments

- Built for the Solana ecosystem: https://solana.com
- Compatible with the x402 protocol: https://x402.org

---

If you would like, I can prepare a PR with this revised README.md and push it to a branch in the repository. Would you like me to proceed with creating the branch and opening a change? 
