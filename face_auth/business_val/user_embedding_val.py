import io
import sys
from ast import Bytes
from typing import List

import numpy as np
from deepface import DeepFace
from deepface.commons.functions import detect_face
from PIL import Image

from face_auth.constant.embedding_constants import (
    DETECTOR_BACKEND,
    EMBEDDING_MODEL_NAME,
    ENFORCE_DETECTION,
    SIMILARITY_THRESHOLD,
)
from face_auth.data_access.user_embedding_data import UserEmbeddingData
from face_auth.exception import AppException
from face_auth.logger import logging

import mediapipe as mp  # Add Mediapipe
import cv2  # Add OpenCV for bounding box calculation

# Initialize Mediapipe face detection
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils


class UserLoginEmbeddingValidation:
    def __init__(self, uuid_: str) -> None:
        self.uuid_ = uuid_
        self.user_embedding_data = UserEmbeddingData()
        self.user = self.user_embedding_data.get_user_embedding(uuid_)

    def validate(self) -> bool:
        try:
            if self.user["UUID"] is None:
                return False
            if self.user["user_embed"] is None:
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
    def generateEmbedding(img_array: np.ndarray) -> np.ndarray:
        """
        Generate embedding from the image array by selecting the closest face.
        """
        try:
            # Detect the closest face using the custom method
            closest_face = UserLoginEmbeddingValidation.detect_closest_face(img_array)
            
            if closest_face is None:
                raise AppException("No face detected or no valid face found.", sys)
            
            # Generate embedding from the closest face
            embed = DeepFace.represent(
                img_path=closest_face,
                model_name=EMBEDDING_MODEL_NAME,
                enforce_detection=False,
            )
            return embed
        except Exception as e:
            raise AppException(e, sys) from e

    @staticmethod
    def generateEmbeddingList(files: List[Bytes]) -> List[np.ndarray]:
        """
        Generate embedding list from image array.
        """
        embedding_list = []
        for contents in files:
            img = Image.open(io.BytesIO(contents))
            # Read image array
            img_array = np.array(img)
            # Detect faces and generate embedding
            embed = UserLoginEmbeddingValidation.generateEmbedding(img_array)
            embedding_list.append(embed)
        return embedding_list

    @staticmethod
    def averageEmbedding(embedding_list: List[np.ndarray]) -> List:
        """Function to calculate the average embedding of the list of embeddings"""
        avg_embed = np.mean(embedding_list, axis=0)
        return avg_embed.tolist()

    @staticmethod
    def cosine_simmilarity(db_embedding, current_embedding) -> bool:
        """Function to calculate cosine similarity between two embeddings"""
        try:
            return np.dot(db_embedding, current_embedding) / (
                np.linalg.norm(db_embedding) * np.linalg.norm(current_embedding)
            )
        except Exception as e:
            raise AppException(e, sys) from e

    def compareEmbedding(self, files: bytes) -> bool:
        """Function to compare the embedding of the current image with the embedding of the database"""
        try:
            if self.user:
                logging.info("Validating User Embedding ......")
                # Validate user embedding
                if not self.validate():
                    return False

                logging.info("Embedding Validation Successful.......")
                # Generate embedding list
                logging.info("Generating Embedding List .......")
                embedding_list = UserLoginEmbeddingValidation.generateEmbeddingList(files)

                logging.info("Embedding List generated.......")
                # Calculate average embedding
                logging.info("Calculating Average Embedding .......")
                avg_embedding_list = UserLoginEmbeddingValidation.averageEmbedding(embedding_list)
                logging.info("Average Embedding calculated.......")

                # Get embedding from database
                db_embedding = self.user["user_embed"]

                logging.info("Calculating Cosine Similarity .......")
                # Calculate cosine similarity
                simmilarity = UserLoginEmbeddingValidation.cosine_simmilarity(db_embedding, avg_embedding_list)
                logging.info("Cosine Similarity calculated.......")

                if simmilarity >= SIMILARITY_THRESHOLD:
                    logging.info("User Authenticated Successfully.......")
                    return True
                else:
                    logging.info("User Authentication Failed.......")
                    return False

            logging.info("User Authentication Failed.......")
            return False
        except Exception as e:
            raise AppException(e, sys) from e

class UserRegisterEmbeddingValidation:
    def __init__(self, uuid_: str) -> None:
        self.uuid_ = uuid_
        self.user_embedding_data = UserEmbeddingData()

    def saveEmbedding(self, files: bytes):
        """This function will generate embedding list and save it to database
        Args:
            files (dict): Bytes of images

        Returns:
            Embedding: saves the image to database
        """
        try:
            embedding_list = UserLoginEmbeddingValidation.generateEmbeddingList(files)
            avg_embedding_list = UserLoginEmbeddingValidation.averageEmbedding(
                embedding_list
            )
            self.user_embedding_data.save_user_embedding(self.uuid_, avg_embedding_list)
        except Exception as e:
            raise AppException(e, sys) from e
