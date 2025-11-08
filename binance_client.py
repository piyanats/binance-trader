"""Binance Thailand API client."""

import hashlib
import hmac
import time
from typing import Dict, List, Optional
from urllib.parse import urlencode

import requests
import pandas as pd

from config import Config


class BinanceThailandClient:
    """Client for interacting with Binance Thailand API."""

    def __init__(self, api_key: str = None, api_secret: str = None):
        """Initialize the Binance Thailand client.

        Args:
            api_key: Binance API key
            api_secret: Binance API secret
        """
        self.api_key = api_key or Config.BINANCE_API_KEY
        self.api_secret = api_secret or Config.BINANCE_API_SECRET
        self.base_url = Config.BINANCE_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            "X-MBX-APIKEY": self.api_key
        })

    def _generate_signature(self, params: Dict) -> str:
        """Generate HMAC SHA256 signature.

        Args:
            params: Request parameters

        Returns:
            HMAC signature
        """
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        return signature

    def _request(self, method: str, endpoint: str, signed: bool = False, **kwargs) -> Dict:
        """Make a request to the Binance API.

        Args:
            method: HTTP method
            endpoint: API endpoint
            signed: Whether to sign the request
            **kwargs: Additional request parameters

        Returns:
            API response
        """
        url = f"{self.base_url}{endpoint}"
        params = kwargs.get("params", {})

        if signed:
            params["timestamp"] = int(time.time() * 1000)
            params["signature"] = self._generate_signature(params)

        try:
            response = self.session.request(method, url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request error: {e}")
            raise

    def get_ticker_price(self, symbol: str) -> Optional[Dict]:
        """Get current ticker price for a symbol.

        Args:
            symbol: Trading pair symbol (e.g., 'BTCTHB')

        Returns:
            Ticker price data
        """
        # Convert symbol format from BTC/THB to BTCTHB
        formatted_symbol = symbol.replace("/", "")

        endpoint = "/api/v3/ticker/price"
        response = self.get_all_ticker_prices()

        for ticker in response:
            if ticker.get("symbol") == formatted_symbol:
                return {
                    "symbol": symbol,
                    "price": float(ticker.get("price", 0))
                }
        return None

    def get_all_ticker_prices(self) -> List[Dict]:
        """Get all ticker prices.

        Returns:
            List of ticker prices
        """
        endpoint = "/api/v3/ticker/price"
        return self._request("GET", endpoint)

    def get_klines(self, symbol: str, interval: str = "1h", limit: int = 100) -> pd.DataFrame:
        """Get kline/candlestick data.

        Args:
            symbol: Trading pair symbol (e.g., 'BTCTHB')
            interval: Kline interval (e.g., '1h', '4h', '1d')
            limit: Number of klines to retrieve

        Returns:
            DataFrame with OHLCV data
        """
        # Convert symbol format from BTC/THB to BTCTHB
        formatted_symbol = symbol.replace("/", "")

        endpoint = "/api/v3/klines"
        params = {
            "symbol": formatted_symbol,
            "interval": interval,
            "limit": limit
        }

        data = self._request("GET", endpoint, params=params)

        # Convert to DataFrame
        df = pd.DataFrame(data, columns=[
            "timestamp", "open", "high", "low", "close", "volume",
            "close_time", "quote_volume", "trades", "taker_buy_base",
            "taker_buy_quote", "ignore"
        ])

        # Convert to appropriate types
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = df[col].astype(float)

        return df[["timestamp", "open", "high", "low", "close", "volume"]]

    def get_account_info(self) -> Dict:
        """Get account information.

        Returns:
            Account information
        """
        endpoint = "/api/v3/account"
        return self._request("GET", endpoint, signed=True)

    def get_asset_balance(self, asset: str) -> Optional[Dict]:
        """Get balance for a specific asset.

        Args:
            asset: Asset symbol (e.g., 'BTC', 'ETH')

        Returns:
            Asset balance information
        """
        account_info = self.get_account_info()
        balances = account_info.get("balances", [])

        for balance in balances:
            if balance.get("asset") == asset:
                return {
                    "asset": asset,
                    "free": float(balance.get("free", 0)),
                    "locked": float(balance.get("locked", 0)),
                    "total": float(balance.get("free", 0)) + float(balance.get("locked", 0))
                }
        return None

    def create_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None
    ) -> Dict:
        """Create a new order.

        Args:
            symbol: Trading pair symbol (e.g., 'BTCTHB')
            side: Order side ('BUY' or 'SELL')
            order_type: Order type ('LIMIT' or 'MARKET')
            quantity: Order quantity
            price: Order price (required for LIMIT orders)

        Returns:
            Order response
        """
        # Convert symbol format from BTC/THB to BTCTHB
        formatted_symbol = symbol.replace("/", "")

        endpoint = "/api/v3/order"
        params = {
            "symbol": formatted_symbol,
            "side": side.upper(),
            "type": order_type.upper(),
            "quantity": quantity,
        }

        if order_type.upper() == "LIMIT":
            if price is None:
                raise ValueError("Price is required for LIMIT orders")
            params["price"] = price
            params["timeInForce"] = "GTC"  # Good Till Cancel

        return self._request("POST", endpoint, signed=True, params=params)

    def buy_market(self, symbol: str, quantity: float) -> Dict:
        """Place a market buy order.

        Args:
            symbol: Trading pair symbol (e.g., 'BTC/THB')
            quantity: Quantity to buy

        Returns:
            Order response
        """
        return self.create_order(symbol, "BUY", "MARKET", quantity)

    def sell_market(self, symbol: str, quantity: float) -> Dict:
        """Place a market sell order.

        Args:
            symbol: Trading pair symbol (e.g., 'BTC/THB')
            quantity: Quantity to sell

        Returns:
            Order response
        """
        return self.create_order(symbol, "SELL", "MARKET", quantity)
