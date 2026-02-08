"""EasyOCR wrapper utilities."""

from __future__ import annotations

import cv2
import numpy as np
from typing import Iterable, List
from PIL import Image

import easyocr


def create_reader(languages: Iterable[str] | None = None, *, gpu: bool = False) -> easyocr.Reader:
    """Create an EasyOCR Reader.

    Args:
        languages: Iterable of language codes like ["en"]. Defaults to ["en"].
        gpu: Whether to use GPU acceleration.
    """
    lang_list = list(languages) if languages else ["en"]
    return easyocr.Reader(lang_list, gpu=gpu)


def read_text(image_path: str, languages: Iterable[str] | None = None, *, gpu: bool = False) -> List[str]:
    """Read text from an image and return the detected strings."""
    reader = create_reader(languages, gpu=gpu)
    results = reader.readtext(image_path, detail=0)
    return list(results)


def detect_document_contour(image: np.ndarray) -> np.ndarray | None:
    """Detect the largest rectangular document contour in an image.
    
    Args:
        image: OpenCV image (BGR format)
        
    Returns:
        4-point contour of the document or None if not found
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 75, 200)
    
    # Find contours
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]
    
    # Find the first contour with 4 points
    for contour in contours:
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
        
        if len(approx) == 4:
            return approx
    
    return None


def order_points(pts: np.ndarray) -> np.ndarray:
    """Order points in top-left, top-right, bottom-right, bottom-left order.
    
    Args:
        pts: 4x2 array of corner points
        
    Returns:
        Ordered 4x2 array of corner points
    """
    rect = np.zeros((4, 2), dtype="float32")
    
    # Sum: top-left will have smallest sum, bottom-right largest
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    
    # Diff: top-right will have smallest diff, bottom-left largest
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    
    return rect


def four_point_transform(image: np.ndarray, pts: np.ndarray) -> np.ndarray:
    """Apply perspective transform to get top-down view of document.
    
    Args:
        image: OpenCV image
        pts: 4-point contour of the document
        
    Returns:
        Warped/cropped image with perspective correction
    """
    rect = order_points(pts.reshape(4, 2))
    (tl, tr, br, bl) = rect
    
    # Calculate width of the new image
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))
    
    # Calculate height of the new image
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))
    
    # Destination points for the transform
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]
    ], dtype="float32")
    
    # Calculate perspective transform matrix and apply it
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    
    return warped


def crop_document_from_image(image: Image.Image) -> Image.Image:
    """Detect and crop document from a wide-angle photo.
    
    Args:
        image: PIL Image
        
    Returns:
        Cropped PIL Image (returns original if no document detected)
    """
    # Convert PIL to OpenCV format
    img_array = np.array(image.convert('RGB'))
    img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    
    # Detect document contour
    contour = detect_document_contour(img_cv)
    
    if contour is not None:
        # Apply perspective transform
        warped = four_point_transform(img_cv, contour)
        # Convert back to PIL
        warped_rgb = cv2.cvtColor(warped, cv2.COLOR_BGR2RGB)
        return Image.fromarray(warped_rgb)
    
    # Return original if no document detected
    return image
