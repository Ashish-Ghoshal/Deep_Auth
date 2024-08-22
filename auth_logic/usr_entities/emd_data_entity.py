import uuid

class FaceEmbeddingDetails:
    """Represents detailed face embeddings for user verification."""

    def __init__(self, unique_user_id: str = None, embedding_vector=None) -> None:
        self.unique_user_id = unique_user_id or self.create_unique_id()
        self.embedding_vector = embedding_vector

    def create_unique_id(self) -> str:
        """Generate a unique identifier for the user."""
        return str(uuid.uuid4())

    def to_dict_representation(self) -> dict:
        """Convert face embedding details to a dictionary."""
        return {
            "unique_user_id": self.unique_user_id,
            "embedding_vector": self.embedding_vector,
        }

    def __repr__(self) -> str:
        """String representation of the face embedding details."""
        return str(self.to_dict_representation())
