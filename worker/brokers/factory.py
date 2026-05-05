from worker.brokers.base_broker import BrokerClient
from worker.brokers.angel_one_broker import AngelOneBrokerClient
from common.db.models.broker_credentials import BrokerCredentials
from common.utils.logger import init_logger

logger = init_logger("broker-factory")


class BrokerFactory:
    """Factory for creating broker client instances"""

    ANGEL_ONE = "angel_one"
    ZERODHA = "zerodha"
    MOCK = "mock"

    @staticmethod
    def create_broker(broker_type: str, credentials: BrokerCredentials) -> BrokerClient:
        """Create a broker client instance

        Args:
            broker_type: Type of broker ("angel_one", "zerodha", "mock")
            credentials: BrokerCredentials object

        Returns:
            BrokerClient instance
        """
        broker_type = broker_type.lower()

        if broker_type == BrokerFactory.ANGEL_ONE:
            logger.info(f"Creating Angel One broker client for user {credentials.user_id}")
            return AngelOneBrokerClient(credentials)

        elif broker_type == BrokerFactory.ZERODHA:
            # Future implementation
            from worker.brokers.zerodha_broker import ZerodhaKiteClient
            logger.info(f"Creating Zerodha broker client for user {credentials.user_id}")
            return ZerodhaKiteClient(credentials)

        elif broker_type == BrokerFactory.MOCK:
            from worker.brokers.mock_broker import MockBrokerClient
            logger.info(f"Creating Mock broker client for testing")
            return MockBrokerClient(credentials)

        else:
            raise ValueError(f"Unknown broker type: {broker_type}")

    @staticmethod
    def get_supported_brokers() -> list:
        """Get list of supported brokers"""
        return [
            BrokerFactory.ANGEL_ONE,
            BrokerFactory.ZERODHA,
            BrokerFactory.MOCK,
        ]
