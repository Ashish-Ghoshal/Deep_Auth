# usr_data_entity.py

import uuid
import logging

# Logger setup
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("UserLogger")

class UserData:
    """Represents user details in the system."""

    def __init__(
        self,
        full_name: str,
        user_handle: str,
        email_address: str,
        phone_number: str,
        password_main: str,
        password_confirm: str,
        identifier: str = None,
    ):
        self.full_name = full_name
        self.user_handle = user_handle
        self.email_address = email_address
        self.phone_number = phone_number
        self.password_main = password_main
        self.password_confirm = password_confirm
        self.identifier = identifier or self.create_id()

        log.info(f"UserData instance created with ID: {self.identifier}")

    def create_id(self) -> str:
        """Generates and returns a unique identifier."""
        unique_identifier = str(uuid.uuid4()) + str(uuid.uuid4())[:3]
        log.debug(f"Generated unique identifier: {unique_identifier}")
        return unique_identifier

    def to_dict(self) -> dict:
        """Transforms the user data into a dictionary."""
        user_dict = self.__dict__
        log.debug(f"User data converted to dictionary: {user_dict}")
        return user_dict

    def __repr__(self) -> str:
        """Returns string representation of the user data."""
        return str(self.to_dict())
