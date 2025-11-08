"""Initialize portfolio with sample data."""

import json
import os

# Sample initial portfolio data
SAMPLE_PORTFOLIO = {
    "BTC/THB": {
        "asset": "BTC/THB",
        "number_shares": 0.0,
        "market_value": 0.0,
        "avg_fifo_cost": 0.0,
        "avg_cost": 0.0,
        "total_return_value": 0.0,
        "total_return_percent": 0.0
    },
    "ETH/THB": {
        "asset": "ETH/THB",
        "number_shares": 0.0,
        "market_value": 0.0,
        "avg_fifo_cost": 0.0,
        "avg_cost": 0.0,
        "total_return_value": 0.0,
        "total_return_percent": 0.0
    }
}


def initialize_portfolio():
    """Initialize portfolio with sample data."""
    # Create data directory
    os.makedirs("data", exist_ok=True)

    portfolio_file = "data/portfolio.json"
    history_file = "data/history.json"

    # Initialize portfolio
    if not os.path.exists(portfolio_file):
        with open(portfolio_file, "w") as f:
            json.dump(SAMPLE_PORTFOLIO, f, indent=2)
        print(f"✓ Created {portfolio_file}")
    else:
        print(f"⚠ {portfolio_file} already exists, skipping")

    # Initialize history
    if not os.path.exists(history_file):
        with open(history_file, "w") as f:
            json.dump([], f, indent=2)
        print(f"✓ Created {history_file}")
    else:
        print(f"⚠ {history_file} already exists, skipping")

    print("\n✓ Portfolio initialization complete!")
    print("\nYou can now:")
    print("1. Edit data/portfolio.json to set your initial holdings")
    print("2. Run the trading bot: python trading_bot.py")


if __name__ == "__main__":
    initialize_portfolio()
