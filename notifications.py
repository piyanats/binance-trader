"""Notification module for sending alerts."""

import requests
from datetime import datetime
from typing import Dict, Optional

from config import Config


class SlackNotifier:
    """Send notifications to Slack."""

    def __init__(self, webhook_url: str = None):
        """Initialize Slack notifier.

        Args:
            webhook_url: Slack webhook URL
        """
        self.webhook_url = webhook_url or Config.SLACK_WEBHOOK_URL

    def send_message(self, message: str, blocks: Optional[list] = None) -> bool:
        """Send a message to Slack.

        Args:
            message: Message text
            blocks: Optional Slack blocks for rich formatting

        Returns:
            True if successful, False otherwise
        """
        if not self.webhook_url:
            print("Slack webhook URL not configured")
            return False

        payload = {"text": message}
        if blocks:
            payload["blocks"] = blocks

        try:
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Failed to send Slack notification: {e}")
            return False

    def send_trading_signal(self, symbol: str, signal: str, analysis: Dict) -> bool:
        """Send a trading signal notification.

        Args:
            symbol: Trading pair symbol
            signal: Trading signal (buy/sell)
            analysis: Analysis results

        Returns:
            True if successful, False otherwise
        """
        emoji = "🟢" if signal == "buy" else "🔴" if signal == "sell" else "⚪"
        signal_text = signal.upper()

        message = f"{emoji} *{signal_text} SIGNAL for {symbol}*"

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} {signal_text} Signal: {symbol}",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Symbol:*\n{symbol}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Signal:*\n{signal_text}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Price:*\n฿{analysis.get('current_price', 0):,.2f}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Time:*\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    }
                ]
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*RSI:*\n{analysis.get('rsi_current', 0):.2f}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*RSI Signal:*\n{analysis.get('rsi_signal', 'N/A').title()}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*MACD:*\n{analysis.get('macd_current', 0):.4f}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*MACD Signal:*\n{analysis.get('macd_signal', 'N/A').title()}"
                    }
                ]
            },
            {
                "type": "divider"
            }
        ]

        return self.send_message(message, blocks)

    def send_trade_execution(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        total_value: float,
        order_id: Optional[str] = None
    ) -> bool:
        """Send a trade execution notification.

        Args:
            symbol: Trading pair symbol
            side: Trade side (BUY/SELL)
            quantity: Quantity traded
            price: Execution price
            total_value: Total value of trade
            order_id: Optional order ID

        Returns:
            True if successful, False otherwise
        """
        emoji = "✅" if side == "BUY" else "💰"
        action = "Bought" if side == "BUY" else "Sold"

        message = f"{emoji} *Trade Executed: {action} {symbol}*"

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} Trade Executed: {action} {symbol}",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Symbol:*\n{symbol}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Side:*\n{side}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Quantity:*\n{quantity:.8f}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Price:*\n฿{price:,.2f}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Total Value:*\n฿{total_value:,.2f}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Time:*\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    }
                ]
            }
        ]

        if order_id:
            blocks[1]["fields"].append({
                "type": "mrkdwn",
                "text": f"*Order ID:*\n{order_id}"
            })

        blocks.append({"type": "divider"})

        return self.send_message(message, blocks)

    def send_error(self, error_type: str, error_message: str) -> bool:
        """Send an error notification.

        Args:
            error_type: Type of error
            error_message: Error message

        Returns:
            True if successful, False otherwise
        """
        message = f"❌ *Error: {error_type}*\n{error_message}"

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"❌ Error: {error_type}",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"```{error_message}```"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    }
                ]
            }
        ]

        return self.send_message(message, blocks)

    def send_price_update(self, prices: Dict[str, float]) -> bool:
        """Send a price update notification.

        Args:
            prices: Dictionary of symbol to price

        Returns:
            True if successful, False otherwise
        """
        message = "📊 *Price Update*"

        fields = []
        for symbol, price in prices.items():
            fields.append({
                "type": "mrkdwn",
                "text": f"*{symbol}:*\n฿{price:,.2f}"
            })

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📊 Price Update",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": fields
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    }
                ]
            }
        ]

        return self.send_message(message, blocks)
