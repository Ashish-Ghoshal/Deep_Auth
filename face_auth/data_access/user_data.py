from face_auth.config.database import MongodbClient
from face_auth.constant.database_constants import USER_COLLECTION_NAME
from face_auth.entity.user import User


class UserDB:
    """Handles MongoDB operations for user data."""

    def __init__(self) -> None:
        self.client = MongodbClient()
        self.col_name = USER_COLLECTION_NAME
        self.col = self.client.database[self.col_name]

    def add_user(self, user: User) -> None:
        """Insert a new user into the collection."""
        self.col.insert_one(user)

    def fetch_user(self, query: dict):
        """Retrieve a single user based on the query."""
        return self.col.find_one(query)

    def fetch_all_users(self):
        """Retrieve all users (not implemented)."""
        pass

    def remove_user(self, user_id: str) -> None:
        """Delete a user by user ID (not implemented)."""
        pass

    def remove_all_users(self) -> None:
        """Delete all users (not implemented)."""
        pass
