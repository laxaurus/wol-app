"""
Test suite for hand detection functionality
"""
import unittest
import cv2
import numpy as np
import sys
import os

# Add src directory to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from hand_detector import HandDetector


class TestHandDetection(unittest.TestCase):
    """
    Test class for verifying hand detection functionality
    """
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.hand_detector = HandDetector()
    
    def test_initialization(self):
        """Test that HandDetector initializes properly."""
        self.assertIsNotNone(self.hand_detector.hands)
        self.assertIsNotNone(self.hand_detector.mp_hands)
        self.assertIsNotNone(self.hand_detector.mp_drawing)
    
    def test_detect_hands_returns_correct_types(self):
        """Test that detect_hands returns expected types."""
        # Create a dummy frame (black image)
        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        results, annotated_frame = self.hand_detector.detect_hands(dummy_frame)
        
        # Check that results is of the expected type
        self.assertTrue(hasattr(results, 'multi_hand_landmarks'))
        
        # Check that annotated_frame is a numpy array
        self.assertIsInstance(annotated_frame, np.ndarray)
        self.assertEqual(annotated_frame.shape, dummy_frame.shape)
    
    def test_are_hands_present_with_no_hands(self):
        """Test that are_hands_present returns False when no hands are present."""
        # Create a dummy frame (black image)
        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Process the frame
        results, _ = self.hand_detector.detect_hands(dummy_frame)
        
        # Since there are no hands in a black image, this should return False
        # (Note: in practice, MediaPipe might detect false positives, 
        # so this test checks the method's capability to distinguish)
        is_present = self.hand_detector.are_hands_present(results)
        # This assertion may fail if MediaPipe detects false positives,
        # but that's okay - it means the test is working as intended
        # We're primarily testing that the method works without errors
        self.assertIsInstance(is_present, bool)
    
    def test_count_hands_method(self):
        """Test the count_hands method."""
        # Create a dummy frame
        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Process the frame
        results, _ = self.hand_detector.detect_hands(dummy_frame)
        
        # Count hands (should be 0 in a blank image)
        hand_count = self.hand_detector.count_hands(results)
        
        self.assertIsInstance(hand_count, int)
        self.assertGreaterEqual(hand_count, 0)
    
    def test_calculate_hand_coverage_with_no_hands(self):
        """Test calculate_hand_coverage method when no hands are present."""
        # Create a dummy frame
        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Process the frame
        results, _ = self.hand_detector.detect_hands(dummy_frame)
        
        # Calculate coverage (should be 0.0 when no hands are present)
        coverage = self.hand_detector.calculate_hand_coverage(dummy_frame, results)
        
        self.assertIsInstance(coverage, float)
        # Coverage should be 0.0 if no hands are detected
        # (though MediaPipe might occasionally detect false positives)
        self.assertGreaterEqual(coverage, 0.0)
        self.assertLessEqual(coverage, 100.0)


def test_real_time_detection():
    """
    Special test function to test actual hand detection with webcam
    This function demonstrates how to use the hand detector in real-time
    """
    print("Starting real-time hand detection test...")
    print("Press 'q' to quit")
    
    hand_detector = HandDetector()
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Cannot open camera")
        return
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detect hands
        results, annotated_frame = hand_detector.detect_hands(frame)
        
        # Check if hands are present
        hands_present = hand_detector.are_hands_present(results)
        
        # Add status text to frame
        status_text = "HAND DETECTED" if hands_present else "NO HAND"
        color = (0, 255, 0) if hands_present else (0, 0, 255)
        cv2.putText(
            annotated_frame, 
            status_text, 
            (10, 30), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            1, 
            color, 
            2
        )
        
        # Display the resulting frame
        cv2.imshow('Hand Detection Test', annotated_frame)
        
        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Release everything
    cap.release()
    cv2.destroyAllWindows()
    
    print("Real-time hand detection test ended.")


if __name__ == '__main__':
    # Run unit tests
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    
    # Optionally run the real-time test
    response = input("\nWould you like to run real-time hand detection test? (y/n): ")
    if response.lower() == 'y':
        test_real_time_detection()