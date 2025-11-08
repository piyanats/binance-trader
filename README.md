# Binance Thailand Trading Bot

A Python-based automated trading bot for Binance Thailand that uses MACD and RSI technical indicators to generate buy/sell signals and sends notifications via Slack.

## Features

- **Automated Price Monitoring**: Fetches current prices from Binance Thailand API every hour
- **Technical Analysis**:
  - RSI (Relative Strength Index) with configurable length and thresholds
  - MACD (Moving Average Convergence Divergence) for signal confirmation
- **Smart Trading Signals**:
  - **Buy Signal**: RSI crosses up from oversold (30) + MACD crosses up
  - **Sell Signal**: RSI crosses down from overbought (70) + MACD crosses down
- **Slack Notifications**: Real-time alerts for price updates, trading signals, and trade executions
- **Portfolio Tracking**:
  - Automatic calculation of average cost, market value, and returns
  - Transaction history recording
  - FIFO cost basis tracking
- **Flexible Configuration**: Environment-based configuration for easy customization

## Tech Stack

- Python 3.13
- Binance Thailand API
- Slack Webhooks
- pandas & numpy for data analysis

## Installation

### Prerequisites

- Python 3.13 or higher
- Binance Thailand account with API access
- Slack workspace with incoming webhook

### Quick Setup (Recommended)

Use the automated setup script with uv package manager for faster installation:

**Linux/Mac:**
```bash
./setup.sh
```

**Windows:**
```bash
setup.bat
```

The script will:
- Create a virtual environment
- Install uv package manager (if not installed)
- Install all dependencies using uv
- Create `.env` file from template
- Initialize portfolio data files

### Manual Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd binance-trader
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

**Using uv (recommended - faster):**
```bash
pip install uv
uv pip install -r requirements.txt
```

**Using pip:**
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
```

5. Edit `.env` file with your credentials:
```env
# Binance Thailand API Configuration
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
BINANCE_BASE_URL=https://api.binance.th

# Slack Configuration
SLACK_WEBHOOK_URL=your_slack_webhook_url_here

# Trading Configuration
CHECK_INTERVAL_HOURS=1
SYMBOLS=BTC/THB,ETH/THB,BNB/THB

# RSI Configuration
RSI_LENGTH=14
RSI_OVERSOLD=30
RSI_OVERBOUGHT=70

# MACD Configuration
MACD_FAST=12
MACD_SLOW=26
MACD_SIGNAL=9

# Trading Settings
ENABLE_AUTO_TRADE=false  # Set to true to enable automatic trading
```

## Configuration

### Binance API Setup

1. Log in to your Binance Thailand account
2. Navigate to API Management
3. Create a new API key
4. Enable "Enable Trading" permission (if you want auto-trading)
5. Save your API Key and Secret Key securely

### Slack Webhook Setup

1. Go to https://api.slack.com/apps
2. Create a new app or select existing one
3. Enable "Incoming Webhooks"
4. Add a new webhook to your desired channel
5. Copy the webhook URL to your `.env` file

## Usage

### Running the Bot

Start the trading bot:
```bash
python trading_bot.py
```

The bot will:
1. Fetch current prices for all configured symbols
2. Analyze technical indicators (RSI and MACD)
3. Generate trading signals
4. Send notifications to Slack
5. Execute trades (if auto-trading is enabled)
6. Wait for the configured interval before the next cycle

### Manual Testing

You can test individual components:

```python
# Test Binance API connection
from binance_client import BinanceThailandClient
client = BinanceThailandClient()
print(client.get_ticker_price("BTC/THB"))

# Test technical indicators
from indicators import TechnicalIndicators
import pandas as pd
# ... analyze your data

# Test Slack notifications
from notifications import SlackNotifier
notifier = SlackNotifier()
notifier.send_message("Test message from trading bot")
```

## Project Structure

```
binance-trader/
├── binance_client.py      # Binance Thailand API client
├── config.py              # Configuration management
├── indicators.py          # Technical indicators (RSI, MACD)
├── notifications.py       # Slack notification handler
├── portfolio.py           # Portfolio and transaction management
├── trading_bot.py         # Main bot application
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment configuration
├── .env                  # Your environment configuration (not in git)
├── .gitignore           # Git ignore rules
└── data/                # Generated data directory
    ├── portfolio.json   # Portfolio state
    └── history.json     # Transaction history
```

## Trading Strategy

### Signal Generation

The bot uses a combination of RSI and MACD indicators:

1. **RSI (Relative Strength Index)**:
   - Length: 14 periods
   - Oversold threshold: 30
   - Overbought threshold: 70
   - Bullish: RSI crosses up from 30
   - Bearish: RSI crosses down from 70

2. **MACD (Moving Average Convergence Divergence)**:
   - Fast period: 12
   - Slow period: 26
   - Signal period: 9
   - Bullish: MACD line crosses above signal line
   - Bearish: MACD line crosses below signal line

### Trading Signals

- **BUY Signal**: RSI bullish + MACD bullish (both must confirm)
- **SELL Signal**: RSI bearish + MACD bearish (both must confirm)
- **NO Signal**: If indicators don't confirm each other

### Portfolio Management

The bot tracks:
- Number of shares/coins held
- Average purchase cost (FIFO method)
- Current market value
- Total return (value and percentage)
- Complete transaction history

## Safety Features

- **Auto-trading disabled by default**: Set `ENABLE_AUTO_TRADE=true` to enable
- **Error handling**: All API calls are wrapped in try-catch blocks
- **Slack notifications**: Get alerted on errors and important events
- **Data persistence**: Portfolio and history saved to JSON files
- **API rate limiting**: Respects exchange rate limits

## Initial Portfolio Setup

To set up your initial portfolio holdings, you can manually create a `data/portfolio.json` file:

```json
{
  "BTC/THB": {
    "asset": "BTC/THB",
    "number_shares": 0.5,
    "market_value": 0,
    "avg_fifo_cost": 2000000,
    "avg_cost": 2000000,
    "total_return_value": 0,
    "total_return_percent": 0
  }
}
```

Or let the bot create it automatically when trades are executed.

## Monitoring

The bot provides several types of Slack notifications:

1. **Price Updates**: Hourly price updates for all monitored symbols
2. **Trading Signals**: When buy or sell signals are detected
3. **Trade Executions**: Confirmation when trades are executed
4. **Errors**: Any errors or issues during operation

## Important Notes

- **Risk Warning**: Cryptocurrency trading involves substantial risk. Only trade with money you can afford to lose.
- **Testing**: Always test with small amounts first before enabling auto-trading
- **API Security**: Never commit your `.env` file or share your API keys
- **Market Hours**: Binance Thailand operates 24/7, but ensure your bot is running when you want it active
- **Network**: Ensure stable internet connection for continuous operation

## Troubleshooting

### Common Issues

1. **API Authentication Error**:
   - Verify your API key and secret are correct
   - Check if API key has necessary permissions
   - Ensure API key is not expired

2. **Insufficient Data Error**:
   - Bot needs at least 26+ candles for MACD calculation
   - Wait for more historical data to accumulate

3. **Slack Notifications Not Working**:
   - Verify webhook URL is correct
   - Check Slack app permissions
   - Test webhook manually using curl

4. **Trade Execution Failed**:
   - Check account balance
   - Verify trading pair is correct
   - Ensure minimum order size is met

## Development

To contribute or modify:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is provided as-is for educational purposes.

## Disclaimer

This bot is for educational and research purposes only. The authors are not responsible for any financial losses incurred through the use of this software. Always do your own research and trade responsibly.

## Support

For issues, questions, or contributions, please open an issue on GitHub.
