<div align="center">
  <img src="https://res.cloudinary.com/dkfwg4ta8/image/upload/v1763975857/faci_un8qfi.png" alt="Qwery x402 Facilitator" width="100%" />
</div>

# Qwery x402 Facilitator

Production-ready payment facilitator for Solana implementing the x402 HTTP payment protocol.

[![Python](https://img.shields.io/badge/python-3.11-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<p align="center">
  <a href="https://qwery.xyz">Website</a> •
  <a href="https://docs.qwery.xyz">Docs</a> •
  <a href="https://twitter.com/qaboratory">Twitter</a> •
  <a href="https://discord.gg/qwery">Discord</a>
</p>

---

## What is x402?

The x402 protocol enables HTTP-native payments where API servers can request payment via HTTP 402 status codes. The **facilitator** acts as the trusted intermediary that:

- **Holds escrowed funds** for payments
- **Signs transactions** on behalf of users
- **Pays network fees** so users don't have to
- **Abstracts blockchain complexity** from both clients and servers

## Features

- **Zero User Fees** - Facilitator covers all Solana network costs
- **Instant Settlement** - Sub-2 second transaction finality
- **Multi-Token Support** - SOL, USDC, USDT on Solana
- **Production Ready** - Built with FastAPI for high performance
- **Devnet & Mainnet** - Full support for both networks

## Quick Start

### Prerequisites

- Python 3.11+
- MongoDB
- Solana CLI (optional)

### Installation
```bash
git clone https://github.com/Qwerydotxyz/qwery-x402-facilitator.git
cd qwery-x402-facilitator
pip install -r requirements.txt
```

### Configuration

Create a `.env` file:
```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=qwery_facilitator
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
FACILITATOR_PRIVATE_KEY=your_base58_private_key
JWT_SECRET=your_jwt_secret
```

### Running the Service
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/payments/create` | POST | Create payment request |
| `/payments/settle` | POST | Settle payment with signed tx |
| `/payments/verify` | POST | Verify payment by signature |
| `/payments/{id}` | GET | Get payment details |

## Architecture
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│ Facilitator │────▶│   Solana    │
│   (SDK)     │◀────│   (x402)    │◀────│  Blockchain │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   MongoDB   │
                    │  (Storage)  │
                    └─────────────┘
```

## SDKs

| Language | Package | Install |
|----------|---------|---------|
| **Rust** | [qwery-sdk](https://crates.io/crates/qwery-sdk) | `cargo add qwery-sdk` |
| **Python** | [qwery-sdk](https://pypi.org/project/qwery-sdk/) | `pip install qwery-sdk` |
| **TypeScript** | Coming Soon | - |

## Security

- All transactions require user signatures
- Facilitator only signs fee-paying portions
- Private keys never leave the facilitator server
- Rate limiting and authentication on all endpoints

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Links

- 🌐 **Website**: [qwery.xyz](https://qwery.xyz)
- 📖 **Documentation**: [docs.qwery.xyz](https://docs.qwery.xyz)
- 🐦 **Twitter**: [@qaboratory](https://twitter.com/qaboratory)
- 💬 **Discord**: [Join Community](https://discord.gg/qwery)
- 📦 **GitHub**: [Qwerydotxyz](https://github.com/Qwerydotxyz)

## License

MIT © Qwery
