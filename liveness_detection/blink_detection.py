import cv2
import dlib
from scipy.spatial import distance

class BlinkDetector:
    """Class to detect blinks in a video stream."""
    
    def __init__(self):
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
        self.left_eye_indices = [36, 37, 38, 39, 40, 41]
        self.right_eye_indices = [42, 43, 44, 45, 46, 47]

    def detect_blinks(self, frame):
        """Detect blinks in a video frame and return the blink status."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.detector(gray)
        for face in faces:
            landmarks = self.predictor(gray, face)
            left_eye_ratio = self._calculate_eye_aspect_ratio(landmarks, self.left_eye_indices)
            right_eye_ratio = self._calculate_eye_aspect_ratio(landmarks, self.right_eye_indices)
            blink_ratio = (left_eye_ratio + right_eye_ratio) / 2
            
            if blink_ratio < 0.2:
                return True  # Blink detected
        return False  # No blink detected

    def _calculate_eye_aspect_ratio(self, landmarks, eye_points):
        """Calculate the eye aspect ratio for blink detection."""
        A = distance.euclidean((landmarks.part(eye_points[1]).x, landmarks.part(eye_points[1]).y),
                               (landmarks.part(eye_points[5]).x, landmarks.part(eye_points[5]).y))
        B = distance.euclidean((landmarks.part(eye_points[2]).x, landmarks.part(eye_points[2]).y),
                               (landmarks.part(eye_points[4]).x, landmarks.part(eye_points[4]).y))
        C = distance.euclidean((landmarks.part(eye_points[0]).x, landmarks.part(eye_points[0]).y),
                               (landmarks.part(eye_points[3]).x, landmarks.part(eye_points[3]).y))
        return (A + B) / (2.0 * C)
