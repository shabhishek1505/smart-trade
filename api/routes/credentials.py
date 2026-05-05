"""Broker credentials management routes"""

from fastapi import APIRouter, Depends, HTTPException, status
from common.db.session import get_session
from common.db.models.broker_credentials import BrokerCredentials
from common.db.repository.broker_credentials_repository import BrokerCredentialsRepository
from api.dependencies import get_current_user, get_db_session
from pydantic import BaseModel
from common.db.models.user import User
from common.utils.logger import init_logger

logger = init_logger("credentials-routes")
router = APIRouter()


class AddCredentialsRequest(BaseModel):
    broker_type: str
    api_key: str
    api_secret: str
    client_code: str = None
    pin: str = None
    totp_key: str = None


class CredentialsResponse(BaseModel):
    id: int
    broker_type: str
    is_active: bool
    created_at: str

    class Config:
        from_attributes = True


@router.post("/", response_model=CredentialsResponse)
async def add_credentials(
    request: AddCredentialsRequest,
    current_user: User = Depends(get_current_user),
    session = Depends(get_db_session)
):
    """Add broker credentials"""

    credentials = BrokerCredentials(
        user_id=current_user.id,
        broker_type=request.broker_type
    )
    credentials.set_credentials(
        request.api_key,
        request.api_secret,
        request.client_code,
        request.pin,
        request.totp_key
    )
    session.add(credentials)
    session.commit()

    logger.info(f"Credentials added for user {current_user.id}: {request.broker_type}")

    return CredentialsResponse.model_validate(credentials)


@router.get("/")
async def list_credentials(
    current_user: User = Depends(get_current_user),
    session = Depends(get_db_session)
):
    """List user's credentials"""

    repo = BrokerCredentialsRepository(session)
    credentials = repo.get_by_user(current_user.id)

    return {
        "status": "success",
        "data": [c.to_dict() for c in credentials]
    }


@router.post("/{credential_id}/test")
async def test_credentials(
    credential_id: int,
    current_user: User = Depends(get_current_user),
    session = Depends(get_db_session)
):
    """Test broker connection"""

    credentials = session.query(BrokerCredentials).filter(
        BrokerCredentials.id == credential_id,
        BrokerCredentials.user_id == current_user.id
    ).first()

    if not credentials:
        raise HTTPException(status_code=404, detail="Credentials not found")

    try:
        from worker.brokers.factory import BrokerFactory
        broker = BrokerFactory.create_broker(credentials.broker_type, credentials)
        success = broker.authenticate()

        if success:
            capital = broker.get_available_capital()
            broker.disconnect()
            return {
                "status": "success",
                "message": "Connection successful",
                "data": {"available_capital": capital}
            }
        else:
            return {
                "status": "error",
                "message": "Authentication failed"
            }
    except Exception as e:
        logger.error(f"Test connection failed: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }


@router.delete("/{credential_id}")
async def deactivate_credentials(
    credential_id: int,
    current_user: User = Depends(get_current_user),
    session = Depends(get_db_session)
):
    """Deactivate credentials"""

    repo = BrokerCredentialsRepository(session)
    credentials = session.query(BrokerCredentials).filter(
        BrokerCredentials.id == credential_id,
        BrokerCredentials.user_id == current_user.id
    ).first()

    if not credentials:
        raise HTTPException(status_code=404, detail="Credentials not found")

    repo.deactivate(credential_id)
    logger.info(f"Credentials deactivated for user {current_user.id}")

    return {"status": "success", "message": "Credentials deactivated"}
