import io
import sys
import logging
from ast import Bytes
from typing import List
import numpy as np
from deepface import DeepFace
from PIL import Image
import mediapipe as mp
import cv2
from usr_constants.embed_cfg import DET_BACKEND, EMB_MODEL, FORCE_DET, SIM_THRESH
from connect_data.usr_db_ops import UserDatabaseOperations
from auth_logic.usr_exceptions.error_handler import CustomError
from liveness_detection.blink_detection import BlinkDetector  # Import the BlinkDetector

# Set up logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("EmbeddingOps")

# Mediapipe setup
mp_detect = mp.solutions.face_detection
mp_draw = mp.solutions.drawing_utils

class LoginCheck:
    def __init__(self, user_id: str) -> None:
        self.user_id = user_id
        self.db = UserDatabaseOperations()
        self.user_data = self.db.get_embed(user_id)
        self.blink_detector = BlinkDetector()  # Initialize BlinkDetector

    def check_valid(self) -> bool:
        """Check if user data is valid."""
        try:
            if not self.user_data.get("ID") or not self.user_data.get("Embed"):
                log.warning(f"No valid data for user: {self.user_id}")
                return False
            return True
        except Exception as e:
            raise CustomError(e, sys) from e

    def detect_liveness(self, img: np.ndarray) -> bool:
        """Detect liveness using blink detection."""
        return self.blink_detector.detect_blinks(img)

    @staticmethod
    def get_face(img: np.ndarray) -> np.ndarray:
        """Detect the closest face using Mediapipe."""
        try:
            with mp_detect.FaceDetection(model_selection=1, min_detection_confidence=0.5) as detect:
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                results = detect.process(img_rgb)

                if not results.detections:
                    log.info("No face found.")
                    return None

                max_area = 0
                main_face = None

                for detection in results.detections:
                    bbox = detection.location_data.relative_bounding_box
                    h, w, _ = img.shape
                    x, y, bw, bh = (int(bbox.xmin * w), int(bbox.ymin * h),
                                    int(bbox.width * w), int(bbox.height * h))
                    area = bw * bh
                    if area > max_area:
                        max_area = area
                        main_face = img[y:y + bh, x:x + bw]

                return main_face if main_face else None

        except Exception as e:
            raise CustomError(e, sys) from e

    @staticmethod
    def make_embed(face: np.ndarray) -> np.ndarray:
        """Create embedding for the face."""
        try:
            face = LoginCheck.get_face(face)
            if face is None:
                raise CustomError("No valid face.", sys)
            
            embed = DeepFace.represent(
                img_path=face,
                model_name=EMB_MODEL,
                enforce_detection=FORCE_DET,
            )
            return embed
        except Exception as e:
            raise CustomError(e, sys) from e

    @staticmethod
    def get_embeds(images: List[Bytes]) -> List[np.ndarray]:
        """Generate list of embeddings from images."""
        log.info("Creating embeddings from images.")
        embeds = []
        for data in images:
            img = Image.open(io.BytesIO(data))
            arr = np.array(img)
            embed = LoginCheck.make_embed(arr)
            embeds.append(embed)
        return embeds

    @staticmethod
    def avg_embeds(embeds: List[np.ndarray]) -> List:
        """Compute average embedding."""
        avg = np.mean(embeds, axis=0).tolist()
        log.info("Average embedding calculated.")
        return avg

    @staticmethod
    def calc_sim(db_embed, current_embed) -> bool:
        """Calculate similarity between embeddings."""
        try:
            similarity = np.dot(db_embed, current_embed) / (
                np.linalg.norm(db_embed) * np.linalg.norm(current_embed)
            )
            return similarity
        except Exception as e:
            raise CustomError(e, sys) from e

    def match_embed(self, images: bytes) -> bool:
        """Match current embed to stored data."""
        try:
            if self.check_valid():
                for data in images:
                    img = Image.open(io.BytesIO(data))
                    arr = np.array(img)
                    
                    if not self.detect_liveness(arr):
                        log.warning("Liveness check failed.")
                        return False

                embeds = self.get_embeds(images)
                avg = self.avg_embeds(embeds)
                
                stored = self.user_data["Embed"]
                sim = self.calc_sim(stored, avg)

                if sim >= SIM_THRESH:
                    log.info(f"User {self.user_id} authenticated.")
                    return True
                else:
                    log.warning(f"User {self.user_id} failed auth.")
                    return False
            else:
                log.error(f"Data invalid for user {self.user_id}.")
                return False
        except Exception as e:
            raise CustomError(e, sys) from e

class RegProcess:
    def __init__(self, user_id: str) -> None:
        self.user_id = user_id
        self.db = UserDatabaseOperations()

    def save_embed(self, images: bytes):
        """Save user embedding to DB."""
        try:
            embeds = LoginCheck.get_embeds(images)
            avg = LoginCheck.avg_embeds(embeds)
            self.db.save_embed(self.user_id, avg)
            log.info(f"Embeddings for user {self.user_id} saved.")
        except Exception as e:
            raise CustomError(e, sys) from e
