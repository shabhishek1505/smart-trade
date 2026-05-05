#!/usr/bin/env python
"""Manage broker credentials from command line"""

import sys
import os
import getpass

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.db.session import get_session
from common.db.models.broker_credentials import BrokerCredentials
from common.db.repository.broker_credentials_repository import BrokerCredentialsRepository
from common.utils.logger import init_logger

logger = init_logger("manage-credentials")


def add_credentials():
    """Add new broker credentials"""
    try:
        user_id = int(input("Enter User ID: "))
        broker_type = input("Enter Broker Type (angel_one): ").lower() or "angel_one"
        api_key = getpass.getpass("Enter API Key: ")
        api_secret = getpass.getpass("Enter API Secret: ")
        client_code = input("Enter Client Code (optional, press Enter to skip): ")
        pin = getpass.getpass("Enter PIN (optional, press Enter to skip): ")
        totp_key = getpass.getpass("Enter TOTP Key (optional, press Enter to skip): ")

        session = get_session()

        # Create credentials
        credentials = BrokerCredentials(
            user_id=user_id,
            broker_type=broker_type
        )
        credentials.set_credentials(
            api_key=api_key,
            api_secret=api_secret,
            client_code=client_code if client_code else None,
            pin=pin if pin else None,
            totp_key=totp_key if totp_key else None
        )

        session.add(credentials)
        session.commit()

        logger.info(f"✓ Credentials added for user {user_id} ({broker_type})")
        print(f"Credential ID: {credentials.id}")

    except Exception as e:
        logger.error(f"Error adding credentials: {str(e)}")
        print(f"Error: {str(e)}")


def list_credentials():
    """List all credentials"""
    try:
        session = get_session()
        repo = BrokerCredentialsRepository(session)

        credentials = session.query(BrokerCredentials).all()

        if not credentials:
            print("No credentials found")
            return

        print("\n" + "=" * 80)
        print(f"{'ID':<5} {'User':<10} {'Broker':<15} {'Status':<10} {'Created':<20}")
        print("=" * 80)

        for cred in credentials:
            status = "Active" if cred.is_active else "Inactive"
            created = cred.created_at.strftime("%Y-%m-%d %H:%M:%S") if cred.created_at else "N/A"
            print(f"{cred.id:<5} {cred.user_id:<10} {cred.broker_type:<15} {status:<10} {created:<20}")

        print("=" * 80 + "\n")

    except Exception as e:
        logger.error(f"Error listing credentials: {str(e)}")
        print(f"Error: {str(e)}")


def get_credentials():
    """Get specific credentials"""
    try:
        credential_id = int(input("Enter Credential ID: "))

        session = get_session()
        cred = session.query(BrokerCredentials).filter_by(id=credential_id).first()

        if not cred:
            print(f"Credential ID {credential_id} not found")
            return

        print(f"\nCredential ID: {cred.id}")
        print(f"User ID: {cred.user_id}")
        print(f"Broker Type: {cred.broker_type}")
        print(f"Status: {'Active' if cred.is_active else 'Inactive'}")
        print(f"Created: {cred.created_at}")
        print(f"Updated: {cred.updated_at}")

        print("\n(Credentials are encrypted and not shown)")

    except Exception as e:
        logger.error(f"Error getting credentials: {str(e)}")
        print(f"Error: {str(e)}")


def deactivate_credentials():
    """Deactivate credentials"""
    try:
        credential_id = int(input("Enter Credential ID to deactivate: "))

        session = get_session()
        repo = BrokerCredentialsRepository(session)

        if repo.deactivate(credential_id):
            logger.info(f"✓ Credential {credential_id} deactivated")
            print(f"✓ Credential {credential_id} has been deactivated")
        else:
            print(f"Credential ID {credential_id} not found")

    except Exception as e:
        logger.error(f"Error deactivating credentials: {str(e)}")
        print(f"Error: {str(e)}")


def test_connection():
    """Test broker connection"""
    try:
        credential_id = int(input("Enter Credential ID to test: "))
        broker_type = input("Broker Type (angel_one): ").lower() or "angel_one"

        session = get_session()
        cred = session.query(BrokerCredentials).filter_by(id=credential_id).first()

        if not cred:
            print(f"Credential ID {credential_id} not found")
            return

        from worker.brokers.factory import BrokerFactory

        print(f"\nTesting {broker_type} connection...")
        broker = BrokerFactory.create_broker(broker_type, cred)

        if broker.authenticate():
            print("✓ Authentication successful!")

            # Try to get positions
            positions = broker.get_positions()
            print(f"✓ Found {len(positions)} positions")

            capital = broker.get_available_capital()
            print(f"✓ Available capital: ₹{capital:,.2f}")

            broker.disconnect()
        else:
            print("✗ Authentication failed")

    except Exception as e:
        logger.error(f"Error testing connection: {str(e)}")
        print(f"Error: {str(e)}")


def main():
    """Main menu"""
    while True:
        print("\n" + "=" * 50)
        print("Broker Credentials Manager")
        print("=" * 50)
        print("1. Add new credentials")
        print("2. List all credentials")
        print("3. View specific credential")
        print("4. Deactivate credentials")
        print("5. Test connection")
        print("6. Exit")
        print("=" * 50)

        choice = input("Select option (1-6): ").strip()

        if choice == "1":
            add_credentials()
        elif choice == "2":
            list_credentials()
        elif choice == "3":
            get_credentials()
        elif choice == "4":
            deactivate_credentials()
        elif choice == "5":
            test_connection()
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid option")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "add":
            add_credentials()
        elif command == "list":
            list_credentials()
        elif command == "get":
            get_credentials()
        elif command == "test":
            test_connection()
        else:
            print("Usage: python manage_credentials.py [add|list|get|test]")
    else:
        main()
