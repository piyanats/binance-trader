"""Main trading bot application."""

import time
from typing import Dict, List
from datetime import datetime

from binance_client import BinanceThailandClient
from indicators import TechnicalIndicators
from notifications import SlackNotifier
from portfolio import PortfolioManager
from config import Config


class TradingBot:
    """Binance Thailand trading bot with MACD/RSI signals."""

    def __init__(self):
        """Initialize the trading bot."""
        self.client = BinanceThailandClient()
        self.notifier = SlackNotifier()
        self.portfolio = PortfolioManager()
        self.indicators = TechnicalIndicators()

        print("Trading Bot initialized")
        print(f"Monitoring symbols: {', '.join(Config.SYMBOLS)}")
        print(f"Auto-trading: {'Enabled' if Config.ENABLE_AUTO_TRADE else 'Disabled'}")

    def get_current_prices(self) -> Dict[str, float]:
        """Get current prices for all monitored symbols.

        Returns:
            Dictionary mapping symbols to prices
        """
        prices = {}
        for symbol in Config.SYMBOLS:
            try:
                ticker = self.client.get_ticker_price(symbol)
                if ticker:
                    prices[symbol] = ticker["price"]
                    print(f"{symbol}: ฿{ticker['price']:,.2f}")
            except Exception as e:
                print(f"Error getting price for {symbol}: {e}")
                self.notifier.send_error(
                    "Price Fetch Error",
                    f"Failed to get price for {symbol}: {str(e)}"
                )

        return prices

    def analyze_symbol(self, symbol: str) -> Dict:
        """Analyze a symbol for trading signals.

        Args:
            symbol: Trading pair symbol

        Returns:
            Analysis results
        """
        try:
            # Get historical data
            df = self.client.get_klines(symbol, interval="1h", limit=100)

            # Analyze signals
            analysis = self.indicators.analyze_trading_signals(
                df,
                rsi_period=Config.RSI_LENGTH,
                rsi_oversold=Config.RSI_OVERSOLD,
                rsi_overbought=Config.RSI_OVERBOUGHT,
                macd_fast=Config.MACD_FAST,
                macd_slow=Config.MACD_SLOW,
                macd_signal=Config.MACD_SIGNAL
            )

            return analysis

        except Exception as e:
            print(f"Error analyzing {symbol}: {e}")
            self.notifier.send_error(
                "Analysis Error",
                f"Failed to analyze {symbol}: {str(e)}"
            )
            return {"signal": "error", "error": str(e)}

    def execute_trade(self, symbol: str, signal: str, quantity: float = None) -> bool:
        """Execute a trade based on signal.

        Args:
            symbol: Trading pair symbol
            signal: Trading signal (buy/sell)
            quantity: Optional quantity to trade

        Returns:
            True if successful, False otherwise
        """
        if not Config.ENABLE_AUTO_TRADE:
            print(f"Auto-trading disabled. Would execute {signal.upper()} for {symbol}")
            return False

        try:
            # Get current price
            ticker = self.client.get_ticker_price(symbol)
            if not ticker:
                raise ValueError(f"Could not get price for {symbol}")

            price = ticker["price"]

            # If quantity not specified, use a default or calculate from portfolio
            if quantity is None:
                # Default small quantity for demonstration
                # In production, you'd calculate this based on portfolio allocation
                quantity = 0.001  # Example: 0.001 BTC

            # Execute trade
            if signal == "buy":
                order = self.client.buy_market(symbol, quantity)
                self.portfolio.record_buy(
                    symbol=symbol,
                    quantity=quantity,
                    price=price,
                    order_id=order.get("orderId"),
                    signal_type="macd_rsi_buy"
                )
                action = "BUY"
            elif signal == "sell":
                order = self.client.sell_market(symbol, quantity)
                self.portfolio.record_sell(
                    symbol=symbol,
                    quantity=quantity,
                    price=price,
                    order_id=order.get("orderId"),
                    signal_type="macd_rsi_sell"
                )
                action = "SELL"
            else:
                return False

            # Send notification
            total_value = quantity * price
            self.notifier.send_trade_execution(
                symbol=symbol,
                side=action,
                quantity=quantity,
                price=price,
                total_value=total_value,
                order_id=order.get("orderId")
            )

            print(f"Trade executed: {action} {quantity} {symbol} @ ฿{price:,.2f}")
            return True

        except Exception as e:
            print(f"Error executing trade for {symbol}: {e}")
            self.notifier.send_error(
                "Trade Execution Error",
                f"Failed to execute {signal} for {symbol}: {str(e)}"
            )
            return False

    def process_symbol(self, symbol: str) -> None:
        """Process a single symbol for trading signals.

        Args:
            symbol: Trading pair symbol
        """
        print(f"\nAnalyzing {symbol}...")

        # Get analysis
        analysis = self.analyze_symbol(symbol)

        if analysis.get("signal") == "error":
            return

        signal = analysis.get("signal")
        current_price = analysis.get("current_price")

        # Update portfolio market values
        if symbol in self.portfolio.assets:
            self.portfolio.update_market_values(symbol, current_price)

        # Display analysis
        print(f"  Current Price: ฿{current_price:,.2f}")
        print(f"  RSI: {analysis.get('rsi_current', 0):.2f} ({analysis.get('rsi_signal', 'neutral')})")
        print(f"  MACD: {analysis.get('macd_current', 0):.4f} ({analysis.get('macd_signal', 'neutral')})")
        print(f"  Signal: {signal.upper()}")

        # Send notifications for trading signals
        if signal in ["buy", "sell"]:
            self.notifier.send_trading_signal(symbol, signal, analysis)

            # Execute trade if auto-trading is enabled
            if Config.ENABLE_AUTO_TRADE:
                # Get asset info to determine quantity
                asset = self.portfolio.get_asset(symbol)
                if signal == "buy":
                    # For buy signals, you'd calculate how much to buy
                    # This is a simplified example
                    self.execute_trade(symbol, signal, quantity=0.001)
                elif signal == "sell" and asset and asset.number_shares > 0:
                    # For sell signals, sell a portion or all
                    quantity_to_sell = asset.number_shares * 0.5  # Sell 50%
                    self.execute_trade(symbol, signal, quantity=quantity_to_sell)

    def run_cycle(self) -> None:
        """Run one analysis cycle for all symbols."""
        print(f"\n{'='*60}")
        print(f"Running analysis cycle at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")

        # Get current prices
        prices = self.get_current_prices()

        # Send price update notification
        if prices:
            self.notifier.send_price_update(prices)

        # Analyze each symbol
        for symbol in Config.SYMBOLS:
            self.process_symbol(symbol)

        # Display portfolio summary
        print(f"\n{'='*60}")
        print("Portfolio Summary")
        print(f"{'='*60}")
        summary = self.portfolio.get_portfolio_summary()
        print(f"Total Market Value: ฿{summary['total_market_value']:,.2f}")
        print(f"Total Cost: ฿{summary['total_cost']:,.2f}")
        print(f"Total Return: ฿{summary['total_return_value']:,.2f} ({summary['total_return_percent']:.2f}%)")
        print(f"Total Transactions: {summary['transaction_count']}")

        print(f"\nCycle completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def run(self) -> None:
        """Run the trading bot continuously."""
        print(f"\nStarting Binance Thailand Trading Bot")
        print(f"Check interval: Every {Config.CHECK_INTERVAL_HOURS} hour(s)")
        print(f"Press Ctrl+C to stop\n")

        try:
            while True:
                try:
                    self.run_cycle()
                except Exception as e:
                    print(f"Error in cycle: {e}")
                    self.notifier.send_error("Cycle Error", str(e))

                # Wait for next cycle
                sleep_seconds = Config.CHECK_INTERVAL_HOURS * 3600
                print(f"\nWaiting {Config.CHECK_INTERVAL_HOURS} hour(s) until next cycle...")
                time.sleep(sleep_seconds)

        except KeyboardInterrupt:
            print("\n\nBot stopped by user")
        except Exception as e:
            print(f"\nFatal error: {e}")
            self.notifier.send_error("Fatal Error", str(e))


def main():
    """Main entry point."""
    try:
        # Validate configuration
        Config.validate()

        # Create and run bot
        bot = TradingBot()
        bot.run()

    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please check your .env file and ensure all required values are set.")
    except Exception as e:
        print(f"Error starting bot: {e}")


if __name__ == "__main__":
    main()
