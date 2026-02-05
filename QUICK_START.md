# Quick Start Guide

Get AirdropFarmer running in 5 minutes!

## Prerequisites

- Python 3.11+
- Notion account
- 5 minutes of your time

## Step 1: Clone Repository

```bash
git clone https://github.com/wagecage/airdrop-farmer.git
cd airdrop-farmer
```

## Step 2: Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Step 3: Setup Notion

1. Go to https://www.notion.so/my-integrations
2. Click "New integration"
3. Name it "AirdropFarmer"
4. Copy the API key (starts with `secret_`)

5. Create a new database in Notion with these columns:
   - **Wallet** (Title)
   - **Platform** (Select)
   - **Activity** (Text)
   - **Status** (Select)
   - **Timestamp** (Date)
   - **TX Hash** (Text)
   - **Details** (Text)

6. Click "..." → "Add connections" → Select your integration
7. Copy the database ID from URL (32-character string)

## Step 4: Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:
```bash
MASTER_PASSWORD=your_strong_password_here
NOTION_API_KEY=secret_your_key_here
NOTION_DATABASE_ID=your_database_id_here
```

## Step 5: Create Wallets

```bash
python main.py setup --wallets 5
```

This creates 5 encrypted wallets.

## Step 6: Run Once (Test)

```bash
python main.py run
```

Check your Notion database - you should see activities logged!

## Step 7: Start Automated Farming

```bash
python main.py schedule
```

The bot will now run every 24 hours automatically.

## What's Happening?

The bot is:
1. ✅ Interacting with MegaETH testnet
2. ✅ Tracking Lighter DEX points
3. ✅ Monitoring Polymarket activity
4. ✅ Logging everything to Notion
5. ✅ Storing state in local database

## View Statistics

```bash
python main.py stats
```

## Next Steps

- Deploy to Railway/Render (see DEPLOYMENT.md)
- Monitor your Notion dashboard
- Check logs in `logs/airdrop_farmer.log`
- Customize intervals in `.env`

## Need Help?

- Read the full README.md
- Check DEPLOYMENT.md for cloud deployment
- Open an issue on GitHub

Happy farming! 🌾
