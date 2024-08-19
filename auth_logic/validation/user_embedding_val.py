import io
import sys
from ast import Bytes
from typing import List

import numpy as np
from deepface import DeepFace
from deepface.commons.functions import detect_face
from PIL import Image


import mediapipe as mp  # Add Mediapipe
import cv2  # Add OpenCV for bounding box calculation

# Initialize Mediapipe face detection
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

from auth_logic.constant.embedding_constants import (
    DET_BACKEND,
    EMBED_MODEL,
    FORCE_DETECT,
    SIM_THRESH,
)
from auth_logic.data_access.user_embedding_data import EmbeddingDB
from auth_logic.exception import AppException
from auth_logic.logger import logging


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
    def detect_closest_face(img_array: np.ndarray) -> np.ndarray:
        """
        Detect the closest face in the image using Mediapipe.
        """
        try:
            with mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5) as face_detection:
                # Convert the image to RGB
                image_rgb = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
                results = face_detection.process(image_rgb)
                
                if not results.detections:
                    logging.info("No face detected.")
                    return None
                
                # Find the largest bounding box (closest face)
                largest_box = None
                max_area = 0
                closest_face = None

                for detection in results.detections:
                    bboxC = detection.location_data.relative_bounding_box
                    ih, iw, _ = img_array.shape
                    x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(bboxC.width * iw), int(bboxC.height * ih)
                    area = w * h
                    if area > max_area:
                        max_area = area
                        largest_box = (x, y, w, h)
                        closest_face = img_array[y:y + h, x:x + w]

                if closest_face is not None:
                    logging.info(f"Closest face detected with bounding box area: {max_area}")
                    return closest_face
                else:
                    logging.info("No valid face detected.")
                    return None

        except Exception as e:
            raise AppException(e, sys) from e

    @staticmethod
    def get_embed(img_arr: np.ndarray) -> np.ndarray:
        """Generate embedding from image array"""
        try:
            # Detect the closest face using the custom method
            closest_face = UserLoginEmbedVal.detect_closest_face(img_arr)
            
            if closest_face is None:
                raise AppException("No face detected or no valid face found.", sys)
            # Generate embedding
            embed = DeepFace.represent(
                img_path=closest_face,
                model_name=EMBED_MODEL,
                enforce_detection=FORCE_DETECT,
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
