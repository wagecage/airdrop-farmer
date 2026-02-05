# Deployment Guide

This guide covers deployment options for AirdropFarmer.

## Option 1: Railway (Recommended)

Railway provides easy deployment with built-in cron support.

### Prerequisites
- Railway account (https://railway.app)
- GitHub repository pushed

### Steps

1. **Install Railway CLI** (optional):
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**:
   ```bash
   railway login
   ```

3. **Initialize Railway Project**:
   ```bash
   cd airdrop-farmer
   railway init
   ```

4. **Link to GitHub Repository**:
   - Go to Railway Dashboard
   - Create New Project
   - Select "Deploy from GitHub repo"
   - Choose `airdrop-farmer` repository

5. **Set Environment Variables**:

   In Railway dashboard, add these variables:
   ```
   MASTER_PASSWORD=your_secure_password
   NOTION_API_KEY=secret_xxxxx
   NOTION_DATABASE_ID=xxxxx
   ENABLE_CRON=true
   RUN_INTERVAL_HOURS=24
   ```

6. **Configure Deployment**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python main.py schedule`

7. **Deploy**:
   ```bash
   railway up
   ```

8. **Verify Deployment**:
   ```bash
   railway logs
   ```

### Cost
Railway offers a free tier with 500 hours per month. This is sufficient for a bot running 24/7.

## Option 2: Render

Render is another great option with a generous free tier.

### Steps

1. **Go to Render Dashboard** (https://render.com)

2. **Create New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub account
   - Select `airdrop-farmer` repository

3. **Configure Service**:
   - Name: `airdrop-farmer`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python main.py schedule`

4. **Set Environment Variables**:
   - Add all variables from `.env.example`
   - Set `ENABLE_CRON=true`

5. **Deploy**:
   - Click "Create Web Service"
   - Wait for deployment to complete

6. **Monitor Logs**:
   - View logs in Render dashboard

### Cost
Render's free tier includes 750 hours per month.

## Option 3: Docker + VPS

Deploy using Docker on any VPS (DigitalOcean, AWS, etc.)

### Steps

1. **Build Docker Image**:
   ```bash
   docker build -t airdrop-farmer .
   ```

2. **Create `.env` file** on your VPS with all required variables

3. **Run Container**:
   ```bash
   docker run -d \
     --name airdrop-farmer \
     --env-file .env \
     -v $(pwd)/data:/app/data \
     -v $(pwd)/logs:/app/logs \
     --restart unless-stopped \
     airdrop-farmer
   ```

4. **View Logs**:
   ```bash
   docker logs -f airdrop-farmer
   ```

5. **Stop Container**:
   ```bash
   docker stop airdrop-farmer
   ```

### Using Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  airdrop-farmer:
    build: .
    container_name: airdrop-farmer
    env_file:
      - .env
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
```

Run:
```bash
docker-compose up -d
```

## Option 4: Heroku

Heroku is a classic PaaS option.

### Steps

1. **Install Heroku CLI**:
   ```bash
   npm install -g heroku
   ```

2. **Login**:
   ```bash
   heroku login
   ```

3. **Create App**:
   ```bash
   heroku create airdrop-farmer
   ```

4. **Set Environment Variables**:
   ```bash
   heroku config:set MASTER_PASSWORD="your_password"
   heroku config:set NOTION_API_KEY="your_key"
   heroku config:set NOTION_DATABASE_ID="your_db_id"
   heroku config:set ENABLE_CRON=true
   ```

5. **Deploy**:
   ```bash
   git push heroku main
   ```

6. **Scale Worker**:
   ```bash
   heroku ps:scale worker=1
   ```

7. **View Logs**:
   ```bash
   heroku logs --tail
   ```

### Cost
Heroku discontinued its free tier. Hobby dyno costs $7/month.

## Option 5: Local Development/Testing

Run locally for testing:

1. **Setup Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Once**:
   ```bash
   python main.py run
   ```

4. **Run with Scheduler**:
   ```bash
   python main.py schedule
   ```

## Post-Deployment Checklist

After deploying, verify:

- [ ] Bot starts without errors
- [ ] Wallets are created and encrypted
- [ ] Connections to MegaETH/Lighter/Polymarket work
- [ ] Activities are logged to Notion
- [ ] Database is being updated
- [ ] Scheduler runs at correct intervals
- [ ] Logs are accessible

## Monitoring

### Check Logs Regularly

Look for:
- ✅ Successful activity completions
- ❌ Connection errors
- ⚠️ Configuration warnings

### Notion Dashboard

Your Notion database will show:
- Real-time activity log
- Success/failure rates
- Per-wallet statistics
- Transaction hashes

### Database Queries

Query local database for stats:
```bash
python main.py stats
```

## Troubleshooting

### Bot Not Starting

1. Check environment variables are set
2. Verify MASTER_PASSWORD is configured
3. Check logs for error messages

### No Activities Logged

1. Verify Notion API key and database ID
2. Check database is shared with integration
3. Verify network connectivity

### MegaETH Connection Failed

1. Check RPC URL is accessible
2. Verify network is not rate-limiting
3. Bot will continue with mock data if connection fails

## Updating the Bot

### Railway/Render

Simply push to GitHub:
```bash
git add .
git commit -m "Update configuration"
git push
```

Auto-deployment will handle the rest.

### Docker

Rebuild and restart:
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Security Notes

1. **Never commit `.env` file**
2. **Use strong MASTER_PASSWORD**
3. **Regularly rotate API keys**
4. **Monitor logs for suspicious activity**
5. **Keep dependencies updated**

## Support

If you encounter issues:
1. Check logs first
2. Review this deployment guide
3. Open an issue on GitHub with error details

---

Happy farming! 🚀
