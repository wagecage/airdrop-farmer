# AirdropFarmer

A comprehensive crypto airdrop farming automation bot that helps you qualify for airdrops across multiple platforms including MegaETH testnet, Lighter DEX, and Polymarket.

## Features

- **Wallet Management**: Secure wallet creation and encrypted storage
- **Multi-Platform Support**:
  - MegaETH testnet interaction automation
  - Lighter DEX points farming and tracking
  - Polymarket interaction tracking
- **Activity Logging**: Comprehensive logging to Notion API
- **State Management**: SQLite database for persistent state
- **Automated Scheduling**: Cron-based daily scheduler for hands-free operation
- **Security**: Encrypted private key storage with password protection

## Architecture

```
airdrop-farmer/
├── src/airdrop_farmer/
│   ├── config.py              # Configuration management
│   ├── wallet_manager.py      # Wallet creation and management
│   ├── database.py            # SQLite state management
│   ├── notion_logger.py       # Notion API integration
│   ├── farmer.py              # Main farming orchestrator
│   ├── scheduler.py           # Cron scheduler
│   ├── modules/
│   │   ├── megaeth.py         # MegaETH testnet interactions
│   │   ├── lighter.py         # Lighter DEX farming
│   │   └── polymarket.py      # Polymarket tracking
│   └── utils/
│       ├── encryption.py      # Encryption utilities
│       └── logger.py          # Logging setup
├── main.py                    # CLI entry point
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## Installation

### Prerequisites

- Python 3.11 or higher
- Git
- A Notion account with API access

### Setup Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/airdrop-farmer.git
   cd airdrop-farmer
   ```

2. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and fill in your credentials:
   - `MASTER_PASSWORD`: Strong password for encrypting wallet private keys
   - `NOTION_API_KEY`: Your Notion integration API key
   - `NOTION_DATABASE_ID`: ID of your Notion database for logging

5. **Setup Notion Database**:

   Create a Notion database with the following properties:
   - **Wallet** (Title)
   - **Platform** (Select: MegaETH, Lighter, Polymarket, System)
   - **Activity** (Text)
   - **Status** (Select: success, failed, pending)
   - **Timestamp** (Date)
   - **TX Hash** (Text)
   - **Details** (Text)

   Get your Notion API key and database ID:
   - Go to https://www.notion.so/my-integrations
   - Create a new integration
   - Copy the API key
   - Share your database with the integration
   - Copy the database ID from the URL

## Usage

### CLI Commands

The bot provides several commands for different operations:

#### 1. Setup Wallets

Create and store wallets securely:

```bash
python main.py setup --wallets 5
```

This creates 5 wallets and stores them encrypted locally.

#### 2. Run Once

Execute farming activities once across all platforms:

```bash
python main.py run
```

#### 3. Start Scheduler

Start automated farming with recurring runs:

```bash
python main.py schedule
```

Options:
- `--interval HOURS`: Set custom interval (default: 24 hours)
- `--no-immediate`: Don't run immediately on start

Example:
```bash
python main.py schedule --interval 12
```

#### 4. View Statistics

Display farming statistics:

```bash
python main.py stats
```

## Configuration

### Environment Variables

Edit `.env` to customize behavior:

```bash
# Required
MASTER_PASSWORD=your_strong_password
NOTION_API_KEY=secret_xxxxx
NOTION_DATABASE_ID=xxxxx

# Optional - Platform Configuration
MEGAETH_RPC_URL=https://rpc.megaeth.testnet
MEGAETH_CHAIN_ID=1234

LIGHTER_API_URL=https://api.lighter.xyz
LIGHTER_API_KEY=your_api_key

POLYMARKET_API_URL=https://api.polymarket.com
POLYMARKET_API_KEY=your_api_key

# Optional - Behavior
NUM_WALLETS=5
RUN_INTERVAL_HOURS=24
ENABLE_CRON=true

# Optional - Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/airdrop_farmer.log
```

## Platform-Specific Details

### MegaETH Testnet

The bot performs the following activities on MegaETH testnet:
- Balance checks
- Self-transfers (common airdrop farming activity)
- Transaction confirmation tracking
- Testnet faucet requests

**Note**: The MegaETH airdrop deadline was February 1, 2026. The bot can still interact with the testnet for practice and future opportunities.

### Lighter DEX

Tracks and farms points on Lighter DEX:
- Points balance tracking
- Trading activity monitoring
- Volume tracking
- Leaderboard position

### Polymarket

Tracks interactions with Polymarket:
- Trade history
- Active positions
- Market participation
- Volume tracking

## Deployment

### Deploy to Railway

1. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**:
   ```bash
   railway login
   ```

3. **Initialize project**:
   ```bash
   railway init
   ```

4. **Set environment variables**:
   ```bash
   railway variables set MASTER_PASSWORD="your_password"
   railway variables set NOTION_API_KEY="your_key"
   railway variables set NOTION_DATABASE_ID="your_db_id"
   ```

5. **Deploy**:
   ```bash
   railway up
   ```

6. **Configure cron job**:

   Add a cron job in Railway dashboard or use the built-in scheduler by setting:
   ```bash
   railway variables set ENABLE_CRON=true
   ```

### Deploy to Render

1. **Create a new Web Service** on Render

2. **Connect your GitHub repository**

3. **Configure build and start commands**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python main.py schedule`

4. **Set environment variables** in Render dashboard

5. **Deploy**

### Alternative: Deploy with Docker

A `Dockerfile` can be created for containerized deployment:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py", "schedule"]
```

Build and run:
```bash
docker build -t airdrop-farmer .
docker run -d --env-file .env airdrop-farmer
```

## Security Best Practices

1. **Never commit secrets**: The `.gitignore` is configured to exclude sensitive files
2. **Use strong master password**: Required for wallet encryption
3. **Secure environment variables**: Use platform-specific secret management
4. **Regular backups**: Backup your encrypted wallet file (`data/wallets.enc`)
5. **Monitor logs**: Check logs regularly for suspicious activity

## Monitoring

### Logs

Application logs are stored in:
- `logs/airdrop_farmer.log` (detailed logs)
- Console output (INFO level)

### Notion Dashboard

All activities are logged to your Notion database in real-time, providing:
- Activity timeline
- Success/failure tracking
- Transaction hashes
- Per-wallet statistics

### Local Database

SQLite database (`data/airdrop_farmer.db`) stores:
- Activity history
- Wallet states
- Platform statistics
- Scheduler run history

Query using any SQLite client or Python:
```python
import sqlite3
conn = sqlite3.connect('data/airdrop_farmer.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM activity_log ORDER BY timestamp DESC LIMIT 10")
print(cursor.fetchall())
```

## Troubleshooting

### Common Issues

1. **"Configuration errors: MASTER_PASSWORD is required"**
   - Solution: Set `MASTER_PASSWORD` in your `.env` file

2. **"Failed to connect to MegaETH testnet"**
   - Solution: Check RPC URL is correct and accessible
   - The bot will continue with mock data for development

3. **"Notion client not initialized"**
   - Solution: Verify `NOTION_API_KEY` and `NOTION_DATABASE_ID` are set
   - Check database is shared with your Notion integration

4. **"No wallets found"**
   - Solution: Run `python main.py setup` to create wallets first

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
python main.py run
```

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Code Structure

- **Modular design**: Each platform has its own module
- **Separation of concerns**: Wallet, database, and logging are independent
- **Extensible**: Easy to add new platforms or features

### Adding a New Platform

1. Create a new module in `src/airdrop_farmer/modules/`
2. Implement interaction methods
3. Add to `farmer.py` orchestrator
4. Update configuration if needed

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Disclaimer

This software is for educational purposes only. Use at your own risk. The authors are not responsible for:
- Lost funds
- Failed airdrop qualifications
- Platform bans or restrictions
- Any other consequences of using this software

Always review platform terms of service before automating interactions.

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check the logs for error details
- Review the documentation

## Roadmap

- [ ] Add more platforms (Arbitrum, Optimism, zkSync)
- [ ] Web dashboard for monitoring
- [ ] Telegram notifications
- [ ] Advanced trading strategies
- [ ] Multi-chain support
- [ ] Gas optimization

---

**Built with Python, Web3.py, and Notion API**

Happy farming!
