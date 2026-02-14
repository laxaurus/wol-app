"""
AI Hand-Detection System for Automated Document Scanning
Main application module
"""
import cv2
import mediapipe as mp
import numpy as np
from PIL import Image
import argparse
import logging
import sys
import os
from pathlib import Path


class HandDetectionDocumentScanner:
    """
    A class that combines hand detection with document scanning capabilities.
    Uses MediaPipe for hand detection and OpenCV for image processing.
    """
    
    def __init__(self, config_path=None):
        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Configuration
        self.config = self.load_config(config_path) if config_path else self.default_config()
        
        # Initialize hand detection model
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        
        # Initialize camera
        self.cap = None
        self.is_scanning = False
        self.document_points = []
        
        # Logging setup
        self.setup_logging()
        
    def load_config(self, config_path):
        """Load configuration from JSON file"""
        # Implementation will be added later
        return self.default_config()
    
    def default_config(self):
        """Default configuration values"""
        return {
            'hand_detection_threshold': 0.7,
            'document_capture_timeout': 5.0,  # seconds
            'capture_resolution': (1920, 1080),
            'output_format': 'pdf',  # pdf, jpg, png
            'save_directory': './scanned_docs/',
            'debug_mode': True
        }
    
    def setup_logging(self):
        """Setup logging configuration"""
        level = logging.DEBUG if self.config['debug_mode'] else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            handlers=[
                logging.FileHandler('hand_detection_scanner.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def initialize_camera(self, camera_index=0):
        """Initialize camera capture"""
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            raise RuntimeError(f"Could not open camera {camera_index}")
            
        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config['capture_resolution'][0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config['capture_resolution'][1])
        
        self.logger.info("Camera initialized successfully")
        
    def detect_hands(self, frame):
        """Detect hands in the given frame"""
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
    
    def find_document_boundary(self, frame):
        """
        Find document boundary by detecting rectangular shapes in the frame
        when hands are not detected
        """
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply edge detection
        edges = cv2.Canny(blurred, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Look for rectangular contours (potential documents)
        document_contour = None
        for contour in contours:
            # Approximate contour to polygon
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            # Check if it's approximately rectangular and large enough
            if len(approx) == 4 and cv2.contourArea(approx) > 10000:
                # Calculate aspect ratio to ensure it's document-like
                x, y, w, h = cv2.boundingRect(approx)
                aspect_ratio = w / h
                
                if 0.5 < aspect_ratio < 2.0:  # Reasonable aspect ratio for documents
                    document_contour = approx
                    break
        
        return document_contour
    
    def perspective_correction(self, frame, pts):
        """
        Apply perspective correction to extract document
        """
        # Order points in a specific order: top-left, top-right, bottom-right, bottom-left
        rect = self.order_points(pts.reshape(4, 2))
        
        # Compute the width and height of the new image
        (tl, tr, br, bl) = rect
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))
        
        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))
        
        # Define destination points for the corrected perspective
        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]], dtype="float32")
        
        # Compute the perspective transform matrix and apply it
        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(frame, M, (maxWidth, maxHeight))
        
        return warped
    
    def order_points(self, pts):
        """
        Order points in a specific order: top-left, top-right, bottom-right, bottom-left
        """
        rect = np.zeros((4, 2), dtype="float32")
        
        # Sum and difference to identify corners
        s = pts.sum(axis=1)
        diff = np.diff(pts, axis=1)
        
        rect[0] = pts[np.argmin(s)]      # Top-left (smallest sum)
        rect[2] = pts[np.argmax(s)]      # Bottom-right (largest sum)
        rect[1] = pts[np.argmin(diff)]   # Top-right (smallest difference)
        rect[3] = pts[np.argmax(diff)]   # Bottom-left (largest difference)
        
        return rect
    
    def enhance_document(self, image):
        """
        Enhance the extracted document image
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
            
        # Apply adaptive threshold for better contrast
        enhanced = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Optional: Apply slight Gaussian blur to reduce noise
        enhanced = cv2.GaussianBlur(enhanced, (1, 1), 0)
        
        return enhanced
    
    def save_document(self, image, filename):
        """
        Save the processed document in the specified format
        """
        # Create output directory if it doesn't exist
        output_dir = Path(self.config['save_directory'])
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine file path
        filepath = output_dir / filename
        
        # Save in the specified format
        if self.config['output_format'].lower() == 'pdf':
            # For now, save as image and convert to PDF later
            img_path = str(filepath.with_suffix('.jpg'))
            cv2.imwrite(img_path, image)
            
            # TODO: Convert to PDF using PyMuPDF or similar library
            self.logger.info(f"Document saved as {img_path}")
        else:
            img_path = str(filepath.with_suffix('.' + self.config['output_format']))
            cv2.imwrite(img_path, image)
            self.logger.info(f"Document saved as {img_path}")
    
    def run(self):
        """
        Main execution loop
        """
        try:
            self.initialize_camera()
            
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                # Detect hands
                hand_results, annotated_frame = self.detect_hands(frame)
                
                # Check if hands are detected
                hands_detected = hand_results.multi_hand_landmarks is not None
                
                if not hands_detected:
                    # Try to detect document boundary
                    doc_contour = self.find_document_boundary(frame)
                    
                    if doc_contour is not None:
                        # Draw document boundary
                        cv2.drawContours(annotated_frame, [doc_contour], -1, (0, 255, 0), 2)
                        
                        # Check if we're ready to capture
                        if not self.is_scanning:
                            self.logger.info("Document detected. Ready to scan...")
                            # Add visual indicator
                            cv2.putText(
                                annotated_frame, 
                                "READY TO SCAN - REMOVE HANDS", 
                                (50, 50), 
                                cv2.FONT_HERSHEY_SIMPLEX, 
                                1, 
                                (0, 255, 0), 
                                2
                            )
                        
                        # If scanning is active, capture the document
                        if self.is_scanning:
                            # Apply perspective correction
                            corrected_doc = self.perspective_correction(frame, doc_contour)
                            
                            # Enhance the document
                            enhanced_doc = self.enhance_document(corrected_doc)
                            
                            # Save the document
                            import datetime
                            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                            filename = f"document_{timestamp}"
                            self.save_document(enhanced_doc, filename)
                            
                            # Reset scanning state
                            self.is_scanning = False
                            self.logger.info("Document captured and saved!")
                            
                    else:
                        # No document detected
                        cv2.putText(
                            annotated_frame, 
                            "NO DOCUMENT DETECTED", 
                            (50, 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 
                            1, 
                            (0, 0, 255), 
                            2
                        )
                else:
                    # Hands detected - stop scanning
                    self.is_scanning = False
                    cv2.putText(
                        annotated_frame, 
                        "HANDS DETECTED - PLACE DOCUMENT", 
                        (50, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 
                        1, 
                        (0, 165, 255), 
                        2
                    )
                
                # Show instructions
                cv2.putText(
                    annotated_frame, 
                    "Press 's' to start scanning, 'q' to quit", 
                    (50, annotated_frame.shape[0] - 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    0.6, 
                    (255, 255, 255), 
                    1
                )
                
                # Display the frame
                cv2.imshow('Hand Detection Document Scanner', annotated_frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    # Start scanning mode
                    self.is_scanning = True
                    self.logger.info("Scanning mode activated")
        
        except Exception as e:
            self.logger.error(f"Error during execution: {str(e)}")
            raise
        finally:
            # Cleanup
            if self.cap is not None:
                self.cap.release()
            cv2.destroyAllWindows()
            self.logger.info("Application closed")


def main():
    parser = argparse.ArgumentParser(description='AI Hand-Detection System for Automated Document Scanning')
    parser.add_argument('--config', type=str, help='Path to configuration file')
    parser.add_argument('--camera', type=int, default=0, help='Camera index (default: 0)')
    
    args = parser.parse_args()
    
    scanner = HandDetectionDocumentScanner(args.config)
    scanner.run()


if __name__ == "__main__":
    main()