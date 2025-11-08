# Quick Start Guide

## Step 1: Install Dependencies

```bash
# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

## Step 2: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor
```

Required configuration:
- `BINANCE_API_KEY`: Your Binance Thailand API key
- `BINANCE_API_SECRET`: Your Binance Thailand API secret
- `SLACK_WEBHOOK_URL`: Your Slack incoming webhook URL

## Step 3: Initialize Portfolio

```bash
# Create initial portfolio files
python initialize_portfolio.py
```

This creates:
- `data/portfolio.json`: Your portfolio holdings
- `data/history.json`: Transaction history

## Step 4: Test Connection

```bash
# Verify everything is configured correctly
python test_connection.py
```

This will test:
- Configuration validity
- Binance API connection
- Slack notifications
- Technical indicators

## Step 5: Run the Bot

```bash
# Start the trading bot
python trading_bot.py
```

The bot will:
1. Fetch current prices every hour
2. Analyze RSI and MACD indicators
3. Generate buy/sell signals
4. Send notifications to Slack
5. Execute trades (if auto-trading is enabled)

## Important First Steps

### 1. Test Mode First
Keep `ENABLE_AUTO_TRADE=false` in your `.env` file initially. This will:
- Show you what trades would be executed
- Send notifications without actual trading
- Let you verify the bot works correctly

### 2. Monitor Slack
You'll receive notifications for:
- Hourly price updates
- Trading signals (buy/sell)
- Trade executions (if enabled)
- Errors and issues

### 3. Enable Auto-Trading (Optional)

Once you're comfortable, enable auto-trading:

```env
ENABLE_AUTO_TRADE=true
```

**Warning**: Only enable this if you understand the risks and have tested thoroughly!

## Customization

### Change Trading Symbols

Edit `.env`:
```env
SYMBOLS=BTC/THB,ETH/THB,BNB/THB,ADA/THB
```

### Adjust Indicator Settings

```env
# RSI Settings
RSI_LENGTH=14
RSI_OVERSOLD=30
RSI_OVERBOUGHT=70

# MACD Settings
MACD_FAST=12
MACD_SLOW=26
MACD_SIGNAL=9
```

### Change Check Interval

```env
CHECK_INTERVAL_HOURS=2  # Check every 2 hours instead of 1
```

## Monitoring

View your portfolio anytime:
```bash
cat data/portfolio.json
```

View transaction history:
```bash
cat data/history.json
```

## Stopping the Bot

Press `Ctrl+C` in the terminal where the bot is running.

## Running in Background

### Using screen (Linux/Mac):
```bash
screen -S trading-bot
python trading_bot.py
# Press Ctrl+A then D to detach
# Reattach with: screen -r trading-bot
```

### Using nohup:
```bash
nohup python trading_bot.py > bot.log 2>&1 &
```

## Troubleshooting

### Bot not starting?
- Run `python test_connection.py` to diagnose
- Check your `.env` file for correct values
- Verify API keys have necessary permissions

### Not receiving Slack notifications?
- Test your webhook URL manually
- Check Slack app permissions
- Verify webhook URL in `.env`

### Trading signals not appearing?
- Signals require both RSI and MACD confirmation
- Need sufficient historical data (100+ candles)
- Market conditions must meet threshold criteria

## Next Steps

1. **Monitor**: Watch the bot for a few cycles
2. **Analyze**: Review the signals and notifications
3. **Adjust**: Fine-tune indicator parameters if needed
4. **Trade**: Enable auto-trading when ready (be careful!)

## Support

- Check `README.md` for detailed documentation
- Review code comments for implementation details
- Test individual components using the test scripts

## Safety Reminders

- Start with small amounts
- Never trade more than you can afford to lose
- Monitor the bot regularly
- Keep your API keys secure
- Understand the trading strategy before enabling auto-trade
