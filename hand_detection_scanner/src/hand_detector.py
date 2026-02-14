"""
Hand Detection Module
Uses MediaPipe to detect hands in video frames
"""
import cv2
import mediapipe as mp
import numpy as np
import logging


class HandDetector:
    """
    A class that handles hand detection using MediaPipe
    """
    
    def __init__(self, min_detection_confidence=0.7, min_tracking_confidence=0.7):
        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Initialize hand detection model
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
        self.logger = logging.getLogger(__name__)
        
    def detect_hands(self, frame):
        """
        Detect hands in the given frame
        Returns detection results and annotated frame
        """
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        results = self.hands.process(rgb_frame)
        
        # Draw hand landmarks if detected
        annotated_frame = frame.copy()
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    annotated_frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )
        
        return results, annotated_frame
    
    def are_hands_present(self, results):
        """
        Check if hands are present in the detection results
        """
        return results.multi_hand_landmarks is not None
    
    def get_hand_landmarks(self, results):
        """
        Get the hand landmarks from detection results
        """
        return results.multi_hand_landmarks
    
    def count_hands(self, results):
        """
        Count the number of hands detected
        """
        if results.multi_hand_landmarks:
            return len(results.multi_hand_landmarks)
        return 0
    
    def calculate_hand_coverage(self, frame, results):
        """
        Calculate approximate coverage of hands in the frame
        """
        if not results.multi_hand_landmarks:
            return 0.0
        
        total_hand_area = 0
        frame_height, frame_width = frame.shape[:2]
        total_frame_area = frame_height * frame_width
        
        for hand_landmarks in results.multi_hand_landmarks:
            # Get bounding box for hand landmarks
            x_coords = [landmark.x for landmark in hand_landmarks.landmark]
            y_coords = [landmark.y for landmark in hand_landmarks.landmark]
            
            x_min, x_max = min(x_coords), max(x_coords)
            y_min, y_max = min(y_coords), max(y_coords)
            
            hand_width = x_max - x_min
            hand_height = y_max - y_min
            
            hand_area = hand_width * hand_height * total_frame_area
            total_hand_area += hand_area
        
        coverage_percentage = (total_hand_area / total_frame_area) * 100
        return coverage_percentage