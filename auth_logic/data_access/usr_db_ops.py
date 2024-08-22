# usr_db_ops.py

from usr_db_conf.mongo_setup import MongoClientWrapper
from usr_constants.db_names import USERS_COLLECTION  
from usr_entities.user import UserData  

import logging

# Logger setup
logging.basicConfig(level=logging.DEBUG)
db_logger = logging.getLogger("DatabaseLogger")

class UserDatabaseOperations:
    """Handles MongoDB interactions for user records."""

    def __init__(self) -> None:
        self.client = MongoClientWrapper()
        self.collection_name = USERS_COLLECTION
        self.collection = self.client.get_database()[self.collection_name]
        db_logger.info(f"Connected to collection: {self.collection_name}")

    def insert_new_user(self, user: UserData) -> None:
        """Inserts a new user into the database."""
        db_logger.debug(f"Inserting user: {user.username}")
        self.collection.insert_one(user.to_dict())

    def find_user_by_query(self, query: dict):
        """Fetch a single user based on a specified query."""
        db_logger.debug(f"Querying user with: {query}")
        return self.collection.find_one(query)

    def retrieve_all_users(self):
        """Retrieve all users from the collection."""
        db_logger.debug("Retrieving all users from the collection.")
        return list(self.collection.find({}))

    def delete_user_by_id(self, user_id: str) -> None:
        """Removes a user by their unique ID."""
        db_logger.debug(f"Deleting user with ID: {user_id}")
        result = self.collection.delete_one({"UUID": user_id})
        if result.deleted_count == 1:
            db_logger.info(f"User with ID: {user_id} successfully deleted.")
        else:
            db_logger.warning(f"No user found with ID: {user_id} to delete.")

    def clear_all_users(self) -> None:  # Renamed from delete_all_users
        """Deletes all user records in the collection."""
        db_logger.warning("Deleting all users from the collection.")
        self.collection.delete_many({})
        db_logger.info("All user records have been successfully deleted.")
