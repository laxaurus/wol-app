"""
PDF Generator Module
Converts processed document images to PDF format
"""
import cv2
import numpy as np
from PIL import Image
import fitz  # PyMuPDF
from pathlib import Path
import logging


class PDFGenerator:
    """
    A class that handles conversion of document images to PDF format
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def image_to_pdf(self, image, output_path, dpi=300):
        """
        Convert a single image to PDF
        """
        try:
            # Convert OpenCV image (BGR) to PIL image (RGB)
            if len(image.shape) == 3:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                # Grayscale image - convert to RGB by duplicating channels
                rgb_image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            
            pil_image = Image.fromarray(rgb_image)
            
            # Save as temporary image file for PDF creation
            temp_path = output_path.with_suffix('.temp.jpg')
            pil_image.save(temp_path, quality=95)
            
            # Create PDF from image using PyMuPDF
            doc = fitz.open()
            page = doc.new_page()
            
            # Calculate image dimensions for proper scaling
            img_width, img_height = pil_image.size
            page_width, page_height = page.rect.width, page.rect.height
            
            # Scale image to fit page while maintaining aspect ratio
            scale_x = page_width / img_width
            scale_y = page_height / img_height
            scale = min(scale_x, scale_y, 1.0)  # Don't upscale
            
            # Calculate centered position
            x_offset = (page_width - img_width * scale) / 2
            y_offset = (page_height - img_height * scale) / 2
            
            # Insert image
            mat = fitz.Matrix(scale, scale)
            page.insert_image(
                fitz.Rect(x_offset, y_offset, x_offset + img_width * scale, y_offset + img_height * scale),
                filename=str(temp_path)
            )
            
            # Save PDF
            doc.save(str(output_path))
            doc.close()
            
            # Remove temporary image file
            temp_path.unlink()
            
            self.logger.info(f"PDF saved successfully: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error converting image to PDF: {str(e)}")
            return False
    
    def images_to_pdf(self, images, output_path, dpi=300):
        """
        Convert multiple images to a single PDF
        """
        try:
            doc = fitz.open()
            
            for i, image in enumerate(images):
                # Convert OpenCV image (BGR) to PIL image (RGB)
                if len(image.shape) == 3:
                    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                else:
                    # Grayscale image - convert to RGB by duplicating channels
                    rgb_image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
                
                pil_image = Image.fromarray(rgb_image)
                
                # Save as temporary image file for PDF creation
                temp_path = output_path.with_name(f"{output_path.stem}_temp_{i}.jpg")
                pil_image.save(temp_path, quality=95)
                
                # Add new page
                page = doc.new_page()
                
                # Calculate image dimensions for proper scaling
                img_width, img_height = pil_image.size
                page_width, page_height = page.rect.width, page.rect.height
                
                # Scale image to fit page while maintaining aspect ratio
                scale_x = page_width / img_width
                scale_y = page_height / img_height
                scale = min(scale_x, scale_y, 1.0)  # Don't upscale
                
                # Calculate centered position
                x_offset = (page_width - img_width * scale) / 2
                y_offset = (page_height - img_height * scale) / 2
                
                # Insert image
                mat = fitz.Matrix(scale, scale)
                page.insert_image(
                    fitz.Rect(x_offset, y_offset, x_offset + img_width * scale, y_offset + img_height * scale),
                    filename=str(temp_path)
                )
                
                # Remove temporary image file
                temp_path.unlink()
            
            # Save PDF
            doc.save(str(output_path))
            doc.close()
            
            self.logger.info(f"Multi-page PDF saved successfully: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error converting images to PDF: {str(e)}")
            return False
    
    def add_metadata(self, pdf_path, metadata_dict):
        """
        Add metadata to existing PDF
        """
        try:
            doc = fitz.open(str(pdf_path))
            doc.set_metadata(metadata_dict)
            doc.saveIncr()
            doc.close()
            
            self.logger.info(f"Metadata added to PDF: {pdf_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding metadata to PDF: {str(e)}")
            return False