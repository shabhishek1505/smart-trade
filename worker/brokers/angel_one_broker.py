from worker.brokers.base_broker import BrokerClient, OrderResponse, OrderStatus, Position, PriceData
from common.db.models.broker_credentials import BrokerCredentials
from common.utils.logger import init_logger
from smartapi import SmartConnect
from smartapi import SmartWebSocketV2
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import threading
import time

logger = init_logger("angel-one-broker")


class AngelOneBrokerClient(BrokerClient):
    """Angel One (SmartAPI) broker client implementation"""

    # Angel One API constants
    EXCHANGE_NSE = "NSE"
    EXCHANGE_BSE = "BSE"
    SEGMENT_EQUITY = "EQUITY"
    PRODUCT_MIS = "MIS"  # Margin Intraday Square off
    PRODUCT_CNC = "CNC"  # Cash and Carry
    PRODUCT_NRML = "NRML"  # Normal
    ORDER_TYPE_MARKET = "MARKET"
    ORDER_TYPE_LIMIT = "LIMIT"
    ORDER_TYPE_STOPLOSS = "STOPLOSS"
    ORDER_TYPE_STOPLOSS_LIMIT = "STOPLOSS_LIMIT"
    DURATION_DAY = "DAY"
    DURATION_IOC = "IOC"

    def __init__(self, credentials: BrokerCredentials):
        """
        Initialize Angel One broker client

        Args:
            credentials: BrokerCredentials object with encrypted API keys
        """
        self.credentials = credentials
        self.user_id = credentials.user_id
        self.api_key = credentials.get_api_key()
        self.api_secret = credentials.get_api_secret()
        self.client_code = credentials.get_client_code()
        self.pin = credentials.get_pin()

        self.smart_connect = None
        self.ws = None
        self.price_cache = {}
        self.is_authenticated = False
        self.position_cache = {}
        self.available_capital = 0.0

    def authenticate(self) -> bool:
        """Authenticate with Angel One"""
        try:
            self.smart_connect = SmartConnect(api_key=self.api_key)

            # Generate session token
            totp_value = self._generate_totp()
            session_data = self.smart_connect.generateSession(
                self.client_code,
                self.pin,
                totp_value
            )

            if session_data["status"] is False:
                logger.error(f"Authentication failed: {session_data['message']}")
                return False

            logger.info(f"Angel One authentication successful for user {self.user_id}")
            self.is_authenticated = True
            self._update_account_info()
            self._start_websocket()
            return True

        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False

    def _generate_totp(self) -> str:
        """Generate TOTP for authentication"""
        try:
            import pyotp
            totp_key = self.credentials.get_totp_key()
            if totp_key:
                totp = pyotp.TOTP(totp_key)
                return totp.now()
            return ""
        except Exception as e:
            logger.warning(f"TOTP generation failed: {str(e)}")
            return ""

    def _update_account_info(self):
        """Update account information (balance, holdings)"""
        try:
            profile = self.smart_connect.getProfile()
            if profile["status"] is True:
                self.available_capital = float(profile["data"]["casBalance"])
                logger.info(f"Account balance updated: {self.available_capital}")
            else:
                logger.warning("Failed to fetch profile")
        except Exception as e:
            logger.error(f"Error updating account info: {str(e)}")

    def _start_websocket(self):
        """Start WebSocket connection for live prices"""
        try:
            auth_token = self.smart_connect.getAuthToken()
            feed_token = self.smart_connect.getFeedToken()

            self.ws = SmartWebSocketV2(
                auth_token=auth_token,
                api_key=self.api_key,
                client_code=self.client_code,
                feed_token=feed_token,
                max_retry_attempt=5,
                retry_delay=5,
            )

            # Set callbacks
            self.ws.on_open = self._on_ws_open
            self.ws.on_data = self._on_ws_data
            self.ws.on_error = self._on_ws_error
            self.ws.on_close = self._on_ws_close

            # Connect in a separate thread
            ws_thread = threading.Thread(target=self.ws.connect)
            ws_thread.daemon = True
            ws_thread.start()

            logger.info("WebSocket connection initiated")
        except Exception as e:
            logger.error(f"WebSocket connection error: {str(e)}")

    def _on_ws_open(self):
        logger.info("WebSocket connected")

    def _on_ws_data(self, msg):
        """Handle WebSocket data"""
        try:
            if "ltp" in msg:
                self.price_cache[msg.get("token")] = {
                    "symbol": msg.get("symbol"),
                    "price": msg.get("ltp"),
                    "bid": msg.get("bid"),
                    "ask": msg.get("ask"),
                    "timestamp": datetime.now(),
                }
        except Exception as e:
            logger.error(f"WebSocket data error: {str(e)}")

    def _on_ws_error(self, msg):
        logger.error(f"WebSocket error: {msg}")

    def _on_ws_close(self, msg):
        logger.warning(f"WebSocket closed: {msg}")

    def place_order(
        self,
        symbol: str,
        action: str,
        quantity: int,
        order_type: str = "MARKET",
        price: Optional[float] = None,
        sl_price: Optional[float] = None,
        target_price: Optional[float] = None,
    ) -> OrderResponse:
        """Place an order on Angel One

        Args:
            symbol: Stock symbol (e.g., "INFY")
            action: "BUY" or "SELL"
            quantity: Number of shares
            order_type: "MARKET", "LIMIT", "STOPLOSS"
            price: Entry price for LIMIT orders
            sl_price: Stop-loss price
            target_price: Take-profit price

        Returns:
            OrderResponse
        """
        if not self.is_authenticated:
            return OrderResponse(
                order_id="",
                symbol=symbol,
                action=action,
                quantity=quantity,
                price=price,
                status="REJECTED",
                message="Not authenticated with broker"
            )

        try:
            # Prepare order parameters
            order_params = {
                "mode": "FULL",
                "exchangeTokens": {
                    self.EXCHANGE_NSE: self._get_exchange_token(symbol),
                },
                "transactionType": action.upper(),
                "quantity": quantity,
                "price": price or 0,
                "productType": self.PRODUCT_MIS,
                "orderType": self._map_order_type(order_type),
                "duration": self.DURATION_DAY,
                "stopPrice": sl_price or 0,
                "disclosedQuantity": 0,
            }

            # Place order via REST API
            response = self.smart_connect.placeOrder(order_params)

            if response["status"] is True:
                order_id = response["data"]["orderId"]
                logger.info(f"Order placed: {order_id} for {symbol}")
                return OrderResponse(
                    order_id=order_id,
                    symbol=symbol,
                    action=action,
                    quantity=quantity,
                    price=price,
                    status="PENDING",
                    message="Order placed successfully"
                )
            else:
                logger.error(f"Order placement failed: {response.get('message', 'Unknown error')}")
                return OrderResponse(
                    order_id="",
                    symbol=symbol,
                    action=action,
                    quantity=quantity,
                    price=price,
                    status="REJECTED",
                    message=response.get("message", "Unknown error")
                )

        except Exception as e:
            logger.error(f"Error placing order: {str(e)}")
            return OrderResponse(
                order_id="",
                symbol=symbol,
                action=action,
                quantity=quantity,
                price=price,
                status="REJECTED",
                message=f"Exception: {str(e)}"
            )

    def _map_order_type(self, order_type: str) -> str:
        """Map order type to Angel One format"""
        mapping = {
            "MARKET": self.ORDER_TYPE_MARKET,
            "LIMIT": self.ORDER_TYPE_LIMIT,
            "STOPLOSS": self.ORDER_TYPE_STOPLOSS,
        }
        return mapping.get(order_type.upper(), self.ORDER_TYPE_MARKET)

    def _get_exchange_token(self, symbol: str) -> str:
        """Get exchange token for symbol (simplified)"""
        # In production, fetch from Angel One instrument list
        # For now, return a placeholder
        return ""

    def get_order_status(self, order_id: str) -> Optional[OrderStatus]:
        """Get order status"""
        try:
            response = self.smart_connect.orderBook()
            if response["status"] is True:
                for order in response["data"]:
                    if order["orderId"] == order_id:
                        return OrderStatus(
                            order_id=order_id,
                            status=order.get("orderStatus", "UNKNOWN"),
                            filled_quantity=int(order.get("filledQuantity", 0)),
                            filled_price=float(order.get("averagePrice", 0.0)),
                            updated_at=datetime.now()
                        )
        except Exception as e:
            logger.error(f"Error fetching order status: {str(e)}")
        return None

    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        try:
            response = self.smart_connect.cancelOrder(
                orderid=order_id,
                mode="FULL"
            )
            if response["status"] is True:
                logger.info(f"Order cancelled: {order_id}")
                return True
            else:
                logger.error(f"Failed to cancel order: {response.get('message')}")
                return False
        except Exception as e:
            logger.error(f"Error cancelling order: {str(e)}")
            return False

    def get_live_price(self, symbol: str) -> Optional[PriceData]:
        """Get current price for a symbol"""
        # Check cache first
        for token, data in self.price_cache.items():
            if data["symbol"] == symbol:
                return PriceData(
                    symbol=symbol,
                    price=data["price"],
                    bid=data.get("bid"),
                    ask=data.get("ask"),
                    timestamp=data.get("timestamp")
                )

        # Fallback to LTP fetch
        try:
            response = self.smart_connect.ltpData(
                mode="LTP",
                exchangeTokens={self.EXCHANGE_NSE: ""},
            )
            if response["status"] is True:
                ltp = response["data"]["ltp"]
                return PriceData(
                    symbol=symbol,
                    price=ltp,
                    timestamp=datetime.now()
                )
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {str(e)}")

        return None

    def get_positions(self) -> List[Position]:
        """Get all current positions"""
        try:
            response = self.smart_connect.position()
            positions = []
            if response["status"] is True:
                for pos in response["data"]:
                    positions.append(Position(
                        symbol=pos.get("symbolname"),
                        quantity=int(pos.get("netquantity", 0)),
                        avg_price=float(pos.get("avgPrice", 0.0)),
                        current_price=float(pos.get("ltp", 0.0)),
                        unrealized_pnl=float(pos.get("unrealizedMTM", 0.0))
                    ))
            return positions
        except Exception as e:
            logger.error(f"Error fetching positions: {str(e)}")
            return []

    def get_available_capital(self) -> float:
        """Get available capital"""
        return self.available_capital

    def get_holdings(self) -> Dict[str, Dict]:
        """Get current holdings"""
        try:
            response = self.smart_connect.holdings()
            holdings = {}
            if response["status"] is True:
                for holding in response["data"]:
                    symbol = holding.get("symbolname")
                    holdings[symbol] = {
                        "quantity": int(holding.get("quantity", 0)),
                        "price": float(holding.get("costPrice", 0.0)),
                        "current_price": float(holding.get("ltp", 0.0)),
                    }
            return holdings
        except Exception as e:
            logger.error(f"Error fetching holdings: {str(e)}")
            return {}

    def disconnect(self):
        """Disconnect from broker"""
        try:
            if self.ws:
                self.ws.close_connection()
            if self.smart_connect:
                self.smart_connect.terminateSession(self.client_code)
            logger.info("Disconnected from Angel One")
        except Exception as e:
            logger.error(f"Error disconnecting: {str(e)}")
