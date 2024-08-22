# usr_emb_ops.py

import logging
from usr_db_conf.mongo_setup import MongoDBConn
from usr_constants.db_cfg import EMBED_COLLECT

# Set up logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("EmbedStoreOps")

class EmbDataHandler:
    """Manages DB operations for user embeddings."""

    def __init__(self) -> None:
        # Initialize MongoDB connection
        self.client = MongoDBConn()
        self.collection_name = EMBED_COLLECT
        self.collection = self.client.get_database()[self.collection_name]
        log.info("Embedding Data Handler initialized.")

    def add_embed(self, user_id: str, embed_data) -> None:
        """Insert embedding into the collection."""
        try:
            self.collection.insert_one({"user_id": user_id, "embed_data": embed_data})
            log.info(f"Embedding added for user {user_id}.")
        except Exception as e:
            log.error(f"Failed to add embedding: {e}")
            raise

    def get_embed(self, user_id: str) -> dict:
        """Fetch a user's embedding by ID."""
        try:
            log.info(f"Fetching embedding for user {user_id}.")
            return self.collection.find_one({"user_id": user_id})
        except Exception as e:
            log.error(f"Failed to fetch embedding: {e}")
            return None

    def delete_embed(self, user_id: str) -> None:
        """Remove a user's embedding by ID."""
        try:
            self.collection.delete_one({"user_id": user_id})
            log.info(f"Embedding deleted for user {user_id}.")
        except Exception as e:
            log.error(f"Failed to delete embedding")
