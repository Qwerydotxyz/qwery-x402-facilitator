# Qwery x402 Facilitator

> Production-ready payment facilitator for Solana using the x402 protocol

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Features

- **Multi-Token Support** - Accept SOL, USDC, USDT, and any SPL token
- **Zero User Fees** - Facilitator pays all network fees (~$0.0001)
- **Instant Settlement** - Sub-second transaction confirmation
- **x402 Compatible** - Standard protocol for HTTP payments
- **Token Gateway** - Token-gating and membership tiers
- **Production Ready** - Live on Solana mainnet

## 📦 Quick Start

### Prerequisites

- Python 3.11+
- Solana wallet with SOL for network fees
- Basic knowledge of Solana transactions

### Installation
```bash
# Clone repository
git clone https://github.com/Qwerydotxyz/qwery-x402-facilitator.git
cd qwery-x402-facilitator

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Add your FACILITATOR_PRIVATE_KEY
```

### Configuration

Create a `.env` file with:
```env
FACILITATOR_PRIVATE_KEY=your_base58_private_key
FACILITATOR_SERVICE_FEE=0.00
FACILITATOR_MIN_BALANCE=100000
LOG_LEVEL=INFO
CORS_ORIGINS=*
```

### Run Locally
```bash
# Development
python main.py

# Production
uvicorn main:app --host 0.0.0.0 --port 8000
```

API will be available at: `http://localhost:8000`

Interactive docs: `http://localhost:8000/docs`

## 🌐 Production Deployment

Live API: **https://facilitator.qwery.xyz**

Documentation: **https://facilitator.qwery.xyz/docs**

## 📚 API Reference

### Create Payment
```bash
POST /create-payment

{
  "payer": "wallet_address",
  "amount": 100000,
  "token": "SOL",
  "network": "solana"
}
```

### Settle Payment
```bash
POST /settle

{
  "signed_transaction": "base64_encoded...",
  "network": "solana"
}
```

### Check Wallet Status
```bash
GET /wallet-status?network=solana
```

### Token Gateway
```bash
POST /token-gate/check-access

{
  "wallet_address": "...",
  "required_token": "EPjFWdd...",
  "required_amount": 1000000
}
```

## 🏗️ Architecture
```
├── app/
│   ├── api/          # API endpoints
│   ├── models/       # Data models
│   ├── services/     # Business logic
│   └── utils/        # Utilities
├── main.py           # Application entry
└── requirements.txt  # Dependencies
```

## 🔐 Security

- **Private Key Management** - Stored in environment variables only
- **Partial Signing** - Users always control their funds
- **Rate Limiting** - 100 requests/minute per IP
- **HTTPS Only** - All communications encrypted

## 🧪 Testing
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test wallet status
curl http://localhost:8000/wallet-status?network=solana

# Run full test suite
pytest tests/
```

## 📖 Documentation

- **Full Documentation**: [docs/](./docs/)
- **API Reference**: https://facilitator.qwery.xyz/docs
- **Whitepaper**: [Qwery_x402_Whitepaper.txt](./docs/whitepaper.txt)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Website**: https://qwery.xyz
- **API**: https://facilitator.qwery.xyz
- **GitHub**: https://github.com/Qwerydotxyz
- **Documentation**: https://facilitator.qwery.xyz/docs

## 💬 Support

- **Discord**: [discord.gg/qwery](https://discord.gg/qwery)
- **Email**: support@qwery.xyz
- **Twitter**: [@QweryNetwork](https://twitter.com/QweryNetwork)

## 🙏 Acknowledgments

- Built on [Solana](https://solana.com)
- Compatible with [x402 Protocol](https://x402.org)
- Inspired by the need for frictionless web3 payments

---

**Built with ❤️ for the Solana ecosystem**
