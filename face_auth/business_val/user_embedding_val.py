import io
import sys
from ast import Bytes
from typing import List

import numpy as np
from deepface import DeepFace
from deepface.commons.functions import detect_face
from PIL import Image

from face_auth.constant.embedding_constants import (
    DET_BACKEND,
    EMBED_MODEL,
    FORCE_DETECT,
    SIM_THRESH,
)
from face_auth.data_access.user_embedding_data import EmbeddingDB
from face_auth.exception import AppException
from face_auth.logger import logging


class UserLoginEmbedVal:
    def __init__(self, uuid: str) -> None:
        self.uuid = uuid
        self.user_data = EmbeddingDB()
        self.user = self.user_data.fetch_embedding(uuid)

    def validate(self) -> bool:
        try:
            if self.user["UUID"] is None or self.user["user_embed"] is None:
                return False
            return True
        except Exception as e:
            raise e

    @staticmethod
    def get_embed(img_arr: np.ndarray) -> np.ndarray:
        """Generate embedding from image array"""
        try:
            faces = detect_face(
                img_arr,
                detector_backend=DET_BACKEND,
                enforce_detection=FORCE_DETECT,
            )
            # Generate embedding
            embed = DeepFace.represent(
                img_path=faces[0],
                model_name=EMBED_MODEL,
                enforce_detection=False,
            )
            return embed
        except Exception as e:
            raise AppException(e, sys) from e

    @staticmethod
    def get_embed_list(files: List[Bytes]) -> List[np.ndarray]:
        """Generate embedding list from image files"""
        embed_list = []
        for content in files:
            img = Image.open(io.BytesIO(content))
            img_arr = np.array(img)
            embed = UserLoginEmbedVal.get_embed(img_arr)
            embed_list.append(embed)
        return embed_list

    @staticmethod
    def avg_embed(embed_list: List[np.ndarray]) -> List:
        """Calculate average embedding from a list"""
        avg_embed = np.mean(embed_list, axis=0)
        return avg_embed.tolist()

    @staticmethod
    def cosine_sim(db_embed, curr_embed) -> bool:
        """Calculate cosine similarity between two embeddings"""
        try:
            sim = np.dot(db_embed, curr_embed) / (
                np.linalg.norm(db_embed) * np.linalg.norm(curr_embed)
            )
            return sim
        except Exception as e:
            raise AppException(e, sys) from e

    def compare_embed(self, files: bytes) -> bool:
        """Compare current image embedding with database embedding"""
        try:
            if self.user:
                logging.info("Validating User Embedding...")
                if not self.validate():
                    return False

                logging.info("Embedding Validation Successful...")
                logging.info("Generating Embedding List...")
                embed_list = UserLoginEmbedVal.get_embed_list(files)

                logging.info("Embedding List Generated...")
                logging.info("Calculating Average Embedding...")
                avg_embed_list = UserLoginEmbedVal.avg_embed(embed_list)
                logging.info("Average Embedding Calculated...")

                db_embed = self.user["user_embed"]

                logging.info("Calculating Cosine Similarity...")
                sim = UserLoginEmbedVal.cosine_sim(db_embed, avg_embed_list)
                logging.info("Cosine Similarity Calculated...")

                if sim >= SIM_THRESH:
                    logging.info("User Authenticated Successfully...")
                    return True
                else:
                    logging.info("User Authentication Failed...")
                    return False
            logging.info("User Authentication Failed...")
            return False
        except Exception as e:
            raise AppException(e, sys) from e

    # def get_user_embed_obj(self, uuid: str) -> Embedding:
    #     """Get user embedding object"""
    #     try:
    #         user_embed = self.user_data.get_user_embed(uuid)
    #         return user_embed
    #     except Exception as e:
    #         raise AppException(e, sys) from e


class UserRegisterEmbedVal:
    def __init__(self, uuid: str) -> None:
        self.uuid = uuid
        self.user_data = EmbeddingDB()

    def save_embed(self, files: bytes):
        """Generate and save embedding to database"""
        try:
            embed_list = UserLoginEmbedVal.get_embed_list(files)
            avg_embed_list = UserLoginEmbedVal.avg_embed(embed_list)
            self.user_data.add_embedding(self.uuid, avg_embed_list)
        except Exception as e:
            raise AppException(e, sys) from e
