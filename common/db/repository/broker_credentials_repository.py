from common.db.repository.base_repository import BaseRepository
from common.db.models.broker_credentials import BrokerCredentials
from typing import Optional, List


class BrokerCredentialsRepository(BaseRepository):
    """Repository for BrokerCredentials model"""

    def __init__(self, session):
        super().__init__(session, BrokerCredentials)

    def get_by_user_and_broker(self, user_id: int, broker_type: str) -> Optional[BrokerCredentials]:
        """Get credentials for user and broker type

        Args:
            user_id: User ID
            broker_type: Broker type (e.g., "angel_one")

        Returns:
            BrokerCredentials or None
        """
        return self.session.query(BrokerCredentials).filter(
            BrokerCredentials.user_id == user_id,
            BrokerCredentials.broker_type == broker_type,
            BrokerCredentials.is_active == True
        ).first()

    def get_by_user(self, user_id: int) -> List[BrokerCredentials]:
        """Get all active credentials for a user

        Args:
            user_id: User ID

        Returns:
            List of BrokerCredentials
        """
        return self.session.query(BrokerCredentials).filter(
            BrokerCredentials.user_id == user_id,
            BrokerCredentials.is_active == True
        ).all()

    def get_by_broker_type(self, broker_type: str) -> List[BrokerCredentials]:
        """Get all credentials for a broker type

        Args:
            broker_type: Broker type

        Returns:
            List of BrokerCredentials
        """
        return self.session.query(BrokerCredentials).filter(
            BrokerCredentials.broker_type == broker_type,
            BrokerCredentials.is_active == True
        ).all()

    def deactivate(self, credential_id: int) -> bool:
        """Deactivate credentials

        Args:
            credential_id: Credential ID

        Returns:
            True if successful
        """
        try:
            credential = self.get_by_id(credential_id)
            if credential:
                credential.is_active = False
                self.session.commit()
                return True
        except Exception as e:
            self.session.rollback()
            raise e
        return False
