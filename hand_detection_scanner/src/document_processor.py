"""
Document Processing Module
Handles document boundary detection, perspective correction, and enhancement
"""
import cv2
import numpy as np
from PIL import Image
import logging


class DocumentProcessor:
    """
    A class responsible for document-specific processing tasks:
    - Document boundary detection
    - Perspective correction
    - Document enhancement
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
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
        max_area = 0
        
        for contour in contours:
            # Approximate contour to polygon
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            # Check if it's approximately rectangular and large enough
            if len(approx) == 4 and cv2.contourArea(approx) > 10000:
                # Calculate aspect ratio to ensure it's document-like
                x, y, w, h = cv2.boundingRect(approx)
                aspect_ratio = w / h
                
                if 0.5 <= aspect_ratio <= 2.0:  # Reasonable aspect ratio for documents
                    area = cv2.contourArea(approx)
                    if area > max_area:
                        max_area = area
                        document_contour = approx
        
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
        Enhance the extracted document image with various techniques
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
        
        # Optional: Apply unsharp masking for sharpening
        # Create the unsharped mask
        gaussian = cv2.GaussianBlur(enhanced, (0, 0), 2.0)
        unsharp = cv2.addWeighted(enhanced, 1.5, gaussian, -0.5, 0)
        
        return unsharp
    
    def extract_and_process_document(self, frame):
        """
        Complete pipeline: find boundary -> perspective correction -> enhancement
        Returns the processed document image or None if no document found
        """
        # Find document boundary
        doc_contour = self.find_document_boundary(frame)
        
        if doc_contour is None:
            return None
        
        # Apply perspective correction
        corrected_doc = self.perspective_correction(frame, doc_contour)
        
        # Enhance the document
        enhanced_doc = self.enhance_document(corrected_doc)
        
        return enhanced_doc