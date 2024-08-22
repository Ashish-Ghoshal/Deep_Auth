import cv2
import dlib
from scipy.spatial import distance

class LivenessDetector:
    def __init__(self):
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

    def detect_blinks(self, frame):
        # Use Dlib to detect face and eye landmarks
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.detector(gray)
        for face in faces:
            landmarks = self.predictor(gray, face)
            left_eye_ratio = self._get_eye_aspect_ratio(landmarks, [36, 37, 38, 39, 40, 41])
            right_eye_ratio = self._get_eye_aspect_ratio(landmarks, [42, 43, 44, 45, 46, 47])
            blink_ratio = (left_eye_ratio + right_eye_ratio) / 2
            if blink_ratio < 0.2:
                return True
        return False

    def _get_eye_aspect_ratio(self, landmarks, eye_points):
        # Calculate eye aspect ratio to detect blinks
        A = distance.euclidean(landmarks.part(eye_points[1]).x, landmarks.part(eye_points[5]).x)
        B = distance.euclidean(landmarks.part(eye_points[2]).x, landmarks.part(eye_points[4]).x)
        C = distance.euclidean(landmarks.part(eye_points[0]).x, landmarks.part(eye_points[3]).x)
        return (A + B) / (2.0 * C)
