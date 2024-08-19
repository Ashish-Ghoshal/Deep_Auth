from auth_logic.config.database import MongodbClient
from auth_logic.constant.database_constants import EMBEDDING_COLLECTION_NAME


class EmbeddingDB:
    """Handles MongoDB operations for user embeddings."""

    def __init__(self) -> None:
        self.client = MongodbClient()
        self.col_name = EMBEDDING_COLLECTION_NAME
        self.col = self.client.database[self.col_name]

    def add_embedding(self, uuid: str, embedding) -> None:
        """Insert a user's embedding into the collection."""
        self.col.insert_one({"UUID": uuid, "user_embed": embedding})

    def fetch_embedding(self, uuid: str) -> dict:
        """Retrieve a user's embedding based on UUID."""
        return self.col.find_one({"UUID": uuid})
