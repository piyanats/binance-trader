"""Technical indicators for trading analysis."""

from typing import Tuple
import pandas as pd
import numpy as np


class TechnicalIndicators:
    """Calculate technical indicators for trading signals."""

    @staticmethod
    def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index (RSI).

        Args:
            data: Price data series
            period: RSI period (default: 14)

        Returns:
            RSI values
        """
        # Calculate price changes
        delta = data.diff()

        # Separate gains and losses
        gains = delta.where(delta > 0, 0)
        losses = -delta.where(delta < 0, 0)

        # Calculate average gains and losses
        avg_gains = gains.rolling(window=period, min_periods=period).mean()
        avg_losses = losses.rolling(window=period, min_periods=period).mean()

        # Calculate RS and RSI
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))

        return rsi

    @staticmethod
    def calculate_macd(
        data: pd.Series,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate MACD (Moving Average Convergence Divergence).

        Args:
            data: Price data series
            fast: Fast EMA period (default: 12)
            slow: Slow EMA period (default: 26)
            signal: Signal line period (default: 9)

        Returns:
            Tuple of (MACD line, Signal line, Histogram)
        """
        # Calculate EMAs
        ema_fast = data.ewm(span=fast, adjust=False).mean()
        ema_slow = data.ewm(span=slow, adjust=False).mean()

        # Calculate MACD line
        macd_line = ema_fast - ema_slow

        # Calculate signal line
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()

        # Calculate histogram
        histogram = macd_line - signal_line

        return macd_line, signal_line, histogram

    @staticmethod
    def detect_rsi_signal(
        rsi_current: float,
        rsi_previous: float,
        oversold: float = 30,
        overbought: float = 70
    ) -> str:
        """Detect RSI signal (bullish, bearish, or neutral).

        Args:
            rsi_current: Current RSI value
            rsi_previous: Previous RSI value
            oversold: Oversold threshold (default: 30)
            overbought: Overbought threshold (default: 70)

        Returns:
            Signal: 'bullish', 'bearish', or 'neutral'
        """
        # Check if RSI crossed up from oversold
        if rsi_previous <= oversold < rsi_current:
            return "bullish"

        # Check if RSI crossed down from overbought
        if rsi_previous >= overbought > rsi_current:
            return "bearish"

        return "neutral"

    @staticmethod
    def detect_macd_signal(
        macd_current: float,
        signal_current: float,
        macd_previous: float,
        signal_previous: float
    ) -> str:
        """Detect MACD signal (bullish, bearish, or neutral).

        Args:
            macd_current: Current MACD value
            signal_current: Current signal line value
            macd_previous: Previous MACD value
            signal_previous: Previous signal line value

        Returns:
            Signal: 'bullish', 'bearish', or 'neutral'
        """
        # Check if MACD crossed above signal line
        if macd_previous <= signal_previous < macd_current - signal_current:
            return "bullish"

        # Check if MACD crossed below signal line
        if macd_previous >= signal_previous > macd_current - signal_current:
            return "bearish"

        return "neutral"

    @classmethod
    def analyze_trading_signals(
        cls,
        df: pd.DataFrame,
        rsi_period: int = 14,
        rsi_oversold: float = 30,
        rsi_overbought: float = 70,
        macd_fast: int = 12,
        macd_slow: int = 26,
        macd_signal: int = 9
    ) -> dict:
        """Analyze trading signals based on RSI and MACD.

        Args:
            df: DataFrame with OHLCV data
            rsi_period: RSI period
            rsi_oversold: RSI oversold threshold
            rsi_overbought: RSI overbought threshold
            macd_fast: MACD fast period
            macd_slow: MACD slow period
            macd_signal: MACD signal period

        Returns:
            Dictionary with analysis results
        """
        if len(df) < max(rsi_period, macd_slow) + 2:
            return {
                "signal": "insufficient_data",
                "rsi_signal": "neutral",
                "macd_signal": "neutral",
                "rsi_current": None,
                "macd_current": None,
                "signal_current": None,
                "histogram_current": None
            }

        # Calculate indicators
        df["rsi"] = cls.calculate_rsi(df["close"], rsi_period)
        df["macd"], df["signal_line"], df["histogram"] = cls.calculate_macd(
            df["close"], macd_fast, macd_slow, macd_signal
        )

        # Get current and previous values
        rsi_current = df["rsi"].iloc[-1]
        rsi_previous = df["rsi"].iloc[-2]

        macd_current = df["macd"].iloc[-1]
        signal_current = df["signal_line"].iloc[-1]
        macd_previous = df["macd"].iloc[-2]
        signal_previous = df["signal_line"].iloc[-2]
        histogram_current = df["histogram"].iloc[-1]

        # Detect signals
        rsi_signal = cls.detect_rsi_signal(
            rsi_current, rsi_previous, rsi_oversold, rsi_overbought
        )
        macd_signal = cls.detect_macd_signal(
            macd_current, signal_current, macd_previous, signal_previous
        )

        # Determine overall signal
        overall_signal = "neutral"

        # Buy signal: RSI bullish + MACD bullish
        if rsi_signal == "bullish" and macd_signal == "bullish":
            overall_signal = "buy"

        # Sell signal: RSI bearish + MACD bearish
        elif rsi_signal == "bearish" and macd_signal == "bearish":
            overall_signal = "sell"

        return {
            "signal": overall_signal,
            "rsi_signal": rsi_signal,
            "macd_signal": macd_signal,
            "rsi_current": float(rsi_current) if not pd.isna(rsi_current) else None,
            "rsi_previous": float(rsi_previous) if not pd.isna(rsi_previous) else None,
            "macd_current": float(macd_current) if not pd.isna(macd_current) else None,
            "signal_current": float(signal_current) if not pd.isna(signal_current) else None,
            "histogram_current": float(histogram_current) if not pd.isna(histogram_current) else None,
            "current_price": float(df["close"].iloc[-1])
        }
