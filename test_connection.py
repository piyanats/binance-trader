"""Test script to verify API connections and configuration."""

import sys
from config import Config
from binance_client import BinanceThailandClient
from notifications import SlackNotifier


def test_config():
    """Test configuration."""
    print("Testing Configuration...")
    print(f"  Binance Base URL: {Config.BINANCE_BASE_URL}")
    print(f"  API Key set: {'Yes' if Config.BINANCE_API_KEY else 'No'}")
    print(f"  API Secret set: {'Yes' if Config.BINANCE_API_SECRET else 'No'}")
    print(f"  Slack Webhook set: {'Yes' if Config.SLACK_WEBHOOK_URL else 'No'}")
    print(f"  Symbols: {', '.join(Config.SYMBOLS)}")
    print(f"  Check Interval: {Config.CHECK_INTERVAL_HOURS} hour(s)")
    print(f"  Auto-trading: {'Enabled' if Config.ENABLE_AUTO_TRADE else 'Disabled'}")

    try:
        Config.validate()
        print("✓ Configuration valid\n")
        return True
    except ValueError as e:
        print(f"✗ Configuration error: {e}\n")
        return False


def test_binance():
    """Test Binance API connection."""
    print("Testing Binance API Connection...")

    try:
        client = BinanceThailandClient()

        # Test public endpoint (doesn't require auth)
        print("  Testing public endpoint...")
        all_prices = client.get_all_ticker_prices()
        print(f"  ✓ Fetched {len(all_prices)} ticker prices")

        # Test specific symbol
        print("  Testing BTC/THB ticker...")
        ticker = client.get_ticker_price("BTC/THB")
        if ticker:
            print(f"  ✓ BTC/THB Price: ฿{ticker['price']:,.2f}")
        else:
            print("  ✗ Could not fetch BTC/THB price")

        # Test klines
        print("  Testing historical data...")
        df = client.get_klines("BTC/THB", interval="1h", limit=10)
        print(f"  ✓ Fetched {len(df)} klines")
        print(f"  Latest close: ฿{df['close'].iloc[-1]:,.2f}")

        print("✓ Binance API connection successful\n")
        return True

    except Exception as e:
        print(f"✗ Binance API error: {e}\n")
        return False


def test_slack():
    """Test Slack notification."""
    print("Testing Slack Integration...")

    try:
        notifier = SlackNotifier()

        if not Config.SLACK_WEBHOOK_URL:
            print("  ⚠ Slack webhook URL not configured, skipping test\n")
            return False

        print("  Sending test message...")
        success = notifier.send_message(
            "🤖 Test message from Binance Thailand Trading Bot"
        )

        if success:
            print("✓ Slack notification sent successfully\n")
            return True
        else:
            print("✗ Failed to send Slack notification\n")
            return False

    except Exception as e:
        print(f"✗ Slack error: {e}\n")
        return False


def test_indicators():
    """Test technical indicators calculation."""
    print("Testing Technical Indicators...")

    try:
        from indicators import TechnicalIndicators
        from binance_client import BinanceThailandClient

        client = BinanceThailandClient()
        df = client.get_klines("BTC/THB", interval="1h", limit=100)

        analysis = TechnicalIndicators.analyze_trading_signals(df)

        print(f"  Signal: {analysis['signal'].upper()}")
        print(f"  RSI: {analysis.get('rsi_current', 0):.2f} ({analysis['rsi_signal']})")
        print(f"  MACD: {analysis.get('macd_current', 0):.4f} ({analysis['macd_signal']})")
        print(f"  Current Price: ฿{analysis.get('current_price', 0):,.2f}")

        print("✓ Technical indicators calculated successfully\n")
        return True

    except Exception as e:
        print(f"✗ Indicators error: {e}\n")
        return False


def main():
    """Run all tests."""
    print("="*60)
    print("Binance Thailand Trading Bot - Connection Test")
    print("="*60)
    print()

    results = {
        "Configuration": test_config(),
        "Binance API": test_binance(),
        "Slack": test_slack(),
        "Indicators": test_indicators()
    }

    print("="*60)
    print("Test Summary")
    print("="*60)

    all_passed = True
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False

    print()

    if all_passed:
        print("✓ All tests passed! You're ready to run the trading bot.")
        print("  Run: python trading_bot.py")
        sys.exit(0)
    else:
        print("⚠ Some tests failed. Please check your configuration.")
        sys.exit(1)


if __name__ == "__main__":
    main()
