"""Portfolio management and tracking."""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

from config import Config


@dataclass
class Asset:
    """Represents a portfolio asset."""
    asset: str  # e.g., "BTC/THB"
    number_shares: float  # Number of shares/coins held
    market_value: float  # Current market value
    avg_fifo_cost: float  # Average cost (FIFO method)
    avg_cost: float  # Average cost
    total_return_value: float  # Total return value
    total_return_percent: float  # Total return percentage

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Asset":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class Transaction:
    """Represents a trading transaction."""
    timestamp: str
    symbol: str
    side: str  # BUY or SELL
    quantity: float
    price: float
    total_value: float
    order_id: Optional[str] = None
    signal_type: Optional[str] = None  # buy/sell signal type

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Transaction":
        """Create from dictionary."""
        return cls(**data)


class PortfolioManager:
    """Manage portfolio assets and trading history."""

    def __init__(self):
        """Initialize portfolio manager."""
        self.portfolio_file = Config.PORTFOLIO_FILE
        self.history_file = Config.HISTORY_FILE
        self.assets: Dict[str, Asset] = {}
        self.history: List[Transaction] = []
        self.load_portfolio()
        self.load_history()

    def load_portfolio(self) -> None:
        """Load portfolio from file."""
        if os.path.exists(self.portfolio_file):
            try:
                with open(self.portfolio_file, "r") as f:
                    data = json.load(f)
                    self.assets = {
                        symbol: Asset.from_dict(asset_data)
                        for symbol, asset_data in data.items()
                    }
            except Exception as e:
                print(f"Error loading portfolio: {e}")
                self.assets = {}
        else:
            self.assets = {}

    def save_portfolio(self) -> None:
        """Save portfolio to file."""
        try:
            with open(self.portfolio_file, "w") as f:
                data = {symbol: asset.to_dict() for symbol, asset in self.assets.items()}
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving portfolio: {e}")

    def load_history(self) -> None:
        """Load transaction history from file."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r") as f:
                    data = json.load(f)
                    self.history = [Transaction.from_dict(tx) for tx in data]
            except Exception as e:
                print(f"Error loading history: {e}")
                self.history = []
        else:
            self.history = []

    def save_history(self) -> None:
        """Save transaction history to file."""
        try:
            with open(self.history_file, "w") as f:
                data = [tx.to_dict() for tx in self.history]
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")

    def get_asset(self, symbol: str) -> Optional[Asset]:
        """Get asset by symbol.

        Args:
            symbol: Asset symbol (e.g., "BTC/THB")

        Returns:
            Asset if exists, None otherwise
        """
        return self.assets.get(symbol)

    def add_asset(
        self,
        symbol: str,
        number_shares: float = 0,
        avg_cost: float = 0
    ) -> Asset:
        """Add or update an asset in the portfolio.

        Args:
            symbol: Asset symbol
            number_shares: Number of shares
            avg_cost: Average cost per share

        Returns:
            Created or updated asset
        """
        if symbol in self.assets:
            asset = self.assets[symbol]
        else:
            asset = Asset(
                asset=symbol,
                number_shares=number_shares,
                market_value=0,
                avg_fifo_cost=avg_cost,
                avg_cost=avg_cost,
                total_return_value=0,
                total_return_percent=0
            )
            self.assets[symbol] = asset

        self.save_portfolio()
        return asset

    def update_market_values(self, symbol: str, current_price: float) -> None:
        """Update market values for an asset.

        Args:
            symbol: Asset symbol
            current_price: Current market price
        """
        if symbol not in self.assets:
            return

        asset = self.assets[symbol]
        asset.market_value = asset.number_shares * current_price

        if asset.avg_cost > 0:
            cost_basis = asset.number_shares * asset.avg_cost
            asset.total_return_value = asset.market_value - cost_basis
            asset.total_return_percent = (
                (asset.total_return_value / cost_basis) * 100
                if cost_basis > 0 else 0
            )
        else:
            asset.total_return_value = 0
            asset.total_return_percent = 0

        self.save_portfolio()

    def record_buy(
        self,
        symbol: str,
        quantity: float,
        price: float,
        order_id: Optional[str] = None,
        signal_type: Optional[str] = None
    ) -> Transaction:
        """Record a buy transaction.

        Args:
            symbol: Asset symbol
            quantity: Quantity bought
            price: Purchase price
            order_id: Optional order ID
            signal_type: Optional signal type

        Returns:
            Transaction record
        """
        total_value = quantity * price

        # Create transaction
        transaction = Transaction(
            timestamp=datetime.now().isoformat(),
            symbol=symbol,
            side="BUY",
            quantity=quantity,
            price=price,
            total_value=total_value,
            order_id=order_id,
            signal_type=signal_type
        )

        # Update portfolio
        if symbol in self.assets:
            asset = self.assets[symbol]
            # Calculate new average cost
            total_cost = (asset.number_shares * asset.avg_cost) + total_value
            asset.number_shares += quantity
            asset.avg_cost = total_cost / asset.number_shares if asset.number_shares > 0 else 0
            asset.avg_fifo_cost = asset.avg_cost  # Simplified FIFO
        else:
            asset = self.add_asset(symbol, quantity, price)

        # Update market value
        self.update_market_values(symbol, price)

        # Save transaction
        self.history.append(transaction)
        self.save_history()
        self.save_portfolio()

        return transaction

    def record_sell(
        self,
        symbol: str,
        quantity: float,
        price: float,
        order_id: Optional[str] = None,
        signal_type: Optional[str] = None
    ) -> Transaction:
        """Record a sell transaction.

        Args:
            symbol: Asset symbol
            quantity: Quantity sold
            price: Sell price
            order_id: Optional order ID
            signal_type: Optional signal type

        Returns:
            Transaction record
        """
        total_value = quantity * price

        # Create transaction
        transaction = Transaction(
            timestamp=datetime.now().isoformat(),
            symbol=symbol,
            side="SELL",
            quantity=quantity,
            price=price,
            total_value=total_value,
            order_id=order_id,
            signal_type=signal_type
        )

        # Update portfolio
        if symbol in self.assets:
            asset = self.assets[symbol]
            asset.number_shares -= quantity
            # Keep average cost the same (realized gain/loss already calculated)
            if asset.number_shares < 0:
                asset.number_shares = 0

            # Update market value
            self.update_market_values(symbol, price)

        # Save transaction
        self.history.append(transaction)
        self.save_history()
        self.save_portfolio()

        return transaction

    def get_portfolio_summary(self) -> Dict:
        """Get portfolio summary.

        Returns:
            Dictionary with portfolio summary
        """
        total_market_value = sum(asset.market_value for asset in self.assets.values())
        total_cost = sum(
            asset.number_shares * asset.avg_cost
            for asset in self.assets.values()
        )
        total_return = total_market_value - total_cost
        total_return_percent = (
            (total_return / total_cost) * 100 if total_cost > 0 else 0
        )

        return {
            "total_market_value": total_market_value,
            "total_cost": total_cost,
            "total_return_value": total_return,
            "total_return_percent": total_return_percent,
            "assets": {symbol: asset.to_dict() for symbol, asset in self.assets.items()},
            "transaction_count": len(self.history)
        }

    def get_recent_transactions(self, limit: int = 10) -> List[Dict]:
        """Get recent transactions.

        Args:
            limit: Number of transactions to return

        Returns:
            List of recent transactions
        """
        return [tx.to_dict() for tx in self.history[-limit:]]
