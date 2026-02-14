# AI Hand-Detection System for Automated Document Scanning

This project implements an intelligent document scanning system that uses computer vision and machine learning to detect hands in real-time video feed and automatically capture documents when hands are not obstructing the view.

## Features

- Real-time hand detection using Google's MediaPipe framework
- Automatic document boundary detection when hands are not present
- Perspective correction to straighten skewed documents
- Document enhancement for improved readability
- Support for saving documents as images or PDF files
- Intuitive user interface with visual feedback

## Project Structure

```
hand_detection_scanner/
├── src/                    # Source code
│   ├── main.py             # Main application entry point
│   ├── hand_detector.py    # Hand detection functionality
│   ├── document_processor.py # Document processing algorithms
│   └── pdf_generator.py    # PDF generation utilities
├── config/                 # Configuration files
├── data/                   # Data files (not versioned)
├── docs/                   # Documentation
├── tests/                  # Unit tests
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```bash
python src/main.py
```

Additional options:
```bash
python src/main.py --camera 1         # Use different camera
python src/main.py --config config.json  # Load custom config
```

### Controls
- Press 's' to start scanning when document is detected and hands are clear
- Press 'q' to quit the application

## How It Works

1. The system continuously captures video frames from the camera
2. MediaPipe detects hands in each frame
3. When no hands are detected, the system looks for rectangular document shapes
4. Once a document is detected, the user can press 's' to capture it
5. The system applies perspective correction to straighten the document
6. Enhancement algorithms improve the document's appearance
7. The final document is saved as an image or PDF

## Dependencies

- OpenCV (cv2)
- MediaPipe
- NumPy
- Pillow (PIL)
- scikit-image
- PyMuPDF (fitz)

## Customization

Configuration options can be modified in the main application class or loaded from a JSON file.

## Troubleshooting

- If the camera doesn't work, try specifying a different camera index with `--camera`
- Adjust the document detection sensitivity by modifying the contour area threshold in `document_processor.py`
- For lighting issues, adjust the Canny edge detection thresholds

## Future Improvements

- OCR integration for text recognition
- Batch processing for multiple documents
- Cloud storage integration
- Mobile app version