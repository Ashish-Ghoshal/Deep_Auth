# validation_process.py

import re
import sys
from typing import Optional
from passlib.context import CryptContext

from auth_logic.data_access.usr_db_ops import UserDatabaseOperations  
from auth_logic.usr_entities.usr_data_entity import UserData  
from auth_logic.usr_exceptions.app_errors import CustomApplicationError 
from auth_logic.usr_log.logger_setup import logger  

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class ValidateUserLogin:
    """Class responsible for validating user login details."""
    
    def __init__(self, email_address: str, password_main: str):
        self.email_address = email_address  
        self.password_main = password_main  
        self.email_regex = re.compile(
            r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
        )
        self.min_pwd_length = 8
        self.max_pwd_length = 16
        logger.info("Login validation initialized.")

    def verify_user_inputs(self) -> dict:
        """Validates email and password inputs."""
        errors = self.check_errors()
        if errors:
            return {"status": False, "msg": errors}
        return {"status": True}

    def check_errors(self) -> list:
        """Check for input errors and return list of errors."""
        error_msgs = []
        if not self.email_address:
            error_msgs.append("Email is required")
        if not self.password_main:
            error_msgs.append("Password is required")
        if not self.is_valid_email():
            error_msgs.append("Invalid Email format")
        if not self.is_pwd_length_valid():
            error_msgs.append(f"Password must be between {self.min_pwd_length} and {self.max_pwd_length} characters.")
        if not self.has_uppercase():
            error_msgs.append("Password must contain at least one uppercase letter.")
        if not self.has_lowercase():
            error_msgs.append("Password must contain at least one lowercase letter.")
        if not self.has_digit():
            error_msgs.append("Password must contain at least one digit.")
        if not self.has_special_char():
            error_msgs.append("Password must contain at least one special character.")
        if not self.is_password_complex():
            error_msgs.append("Password is too common or simple.")
        return error_msgs

    def is_valid_email(self) -> bool:
        """Validate the email address using regex."""
        return bool(re.fullmatch(self.email_regex, self.email_address))

    def is_pwd_length_valid(self) -> bool:
        """Checks if the password length is within the required range."""
        return self.min_pwd_length <= len(self.password_main) <= self.max_pwd_length

    def has_uppercase(self) -> bool:
        """Checks if the password contains at least one uppercase letter."""
        return any(char.isupper() for char in self.password_main)

    def has_lowercase(self) -> bool:
        """Checks if the password contains at least one lowercase letter."""
        return any(char.islower() for char in self.password_main)

    def has_digit(self) -> bool:
        """Checks if the password contains at least one digit."""
        return any(char.isdigit() for char in self.password_main)

    def has_special_char(self) -> bool:
        """Checks if the password contains at least one special character."""
        special_chars = "!@#$%^&*()-_=+[{]}\\|;:'\",<.>/?`~"
        return any(char in special_chars for char in self.password_main)

    def is_password_complex(self) -> bool:
        """Checks if the password is not too simple or common."""
        common_passwords = ["password", "123456", "qwerty", "letmein"]
        return self.password_main not in common_passwords

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Check if the plain password matches the stored hashed password."""
        return bcrypt_context.verify(plain_password, hashed_password)

    def authenticate_user(self) -> Optional[str]:
        """Authenticate the user based on email and password."""
        try:
            login_status = self.verify_user_inputs()
            if login_status["status"]:
                user_data = UserDatabaseOperations()
                user = user_data.fetch_user({"email": self.email_address})
                if user and self.verify_password(self.password_main, user["password"]):
                    return user
                logger.info("Invalid login attempt")
            return None
        except Exception as ex:
            logger.error(f"Authentication error: {ex}")
            raise CustomApplicationError(ex, sys) from ex

class ValidateUserRegistration:
    """Class responsible for validating and registering new users."""

    def __init__(self, user: UserData):
        self.user = user
        self.email_regex = re.compile(
            r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
        )
        self.user_identifier = self.user.identifier  # Updated to match refactor
        self.user_data = UserDatabaseOperations()

    def verify_registration_details(self) -> dict:
        """Validates the registration details."""
        error_msgs = self.check_user_details()
        if error_msgs:
            return {"status": False, "msg": error_msgs}
        return {"status": True}

    def check_user_details(self) -> list:
        """Validate user registration details."""
        errors = []
        errors.extend(self.validate_basic_info())
        errors.extend(self.validate_password())
        return errors

    def validate_basic_info(self) -> list:
        """Validate basic user information like email and username."""
        basic_info_errors = []
        if not self.user.full_name:
            basic_info_errors.append("Name is required")
        if not self.user.user_handle:
            basic_info_errors.append("Username is required")
        if not self.user.email_address:
            basic_info_errors.append("Email is required")
        if not self.is_valid_email():
            basic_info_errors.append("Invalid Email format")
        return basic_info_errors

    def validate_password(self) -> list:
        """Validate passwords for registration."""
        pwd_errors = []
        if not self.user.password_main or not self.user.password_confirm:
            pwd_errors.append("Both passwords are required")
        if self.user.password_main != self.user.password_confirm:
            pwd_errors.append("Passwords do not match")
        return pwd_errors

    def is_valid_email(self) -> bool:
        """Check if the email format is valid."""
        return bool(re.fullmatch(self.email_regex, self.user.email_address))

    def save_user(self):
        """Save user details after successful validation."""
        try:
            secured_password = bcrypt_context.hash(self.user.password_main) 
            user_record = {
                "Name": self.user.full_name,
                "username": self.user.user_handle,
                "password": secured_password,  
                "email": self.user.email_address,
                "ph_no": self.user.phone_number,
                "UUID": self.user_identifier,  
            }
            self.user_data.add_user(user_record)
            logger.info("New user registered successfully.")
        except Exception as ex:
            logger.error(f"Error saving user: {ex}")
            raise CustomApplicationError(ex, sys) from ex
