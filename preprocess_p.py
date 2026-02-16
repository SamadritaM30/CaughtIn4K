import cv2
import numpy as np
import os
from datetime import datetime

class ImageProcessor:
    def __init__(self, target_size=(224, 224), color_mode='rgb'):
        self.target_size = target_size
        self.color_mode = color_mode
        # CLAHE is used for industrial contrast enhancement
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))

    def preprocess(self, source):
        """
        Processes image for Anomaly Detection.
        Includes Contrast Enhancement (CLAHE) to highlight defects.
        """
        raw_img = self._load_image(source)
        if raw_img is None:
            raise ValueError("Image could not be loaded.")

        # 1. Preserve Metadata (as per your Class Diagram)
        metadata = {
            "original_resolution": f"{raw_img.shape[1]}x{raw_img.shape[0]}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # 2. Convert Color Space
        if self.color_mode == 'grayscale':
            gray = cv2.cvtColor(raw_img, cv2.COLOR_BGR2GRAY)
            # Enhance contrast so defects (scratches/dents) are visible
            enhanced = self.clahe.apply(gray)
        else:
            # For RGB, we enhance the L channel in LAB space to avoid color distortion
            lab = cv2.cvtColor(raw_img, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            l = self.clahe.apply(l)
            enhanced = cv2.merge((l, a, b))
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2RGB)

        # 3. Noise Reduction (Bilateral filter preserves edges/defects better than Gaussian)
        denoised = cv2.bilateralFilter(enhanced, 5, 75, 75)

        # 4. Resize and Normalize
        resized = cv2.resize(denoised, self.target_size)
        normalized = resized.astype("float32") / 255.0

        if self.color_mode == 'grayscale':
            normalized = np.expand_dims(normalized, axis=-1)

        # Return both the processed image and metadata for your 'Image' class
        return normalized, metadata

    def _load_image(self, source):
        if isinstance(source, str):
            return cv2.imread(source) if os.path.exists(source) else None
        elif isinstance(source, bytes):
            nparr = np.frombuffer(source, np.uint8)
            return cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return None

    def augment_for_self_supervised(self, image):
        """
        Creates variations of 'normal' images. 
        Required for Section 3.2 of your SRS.
        """
        # Example: Random rotation or slight brightness shifts
        rows, cols, _ = image.shape
        M = cv2.getRotationMatrix2D((cols/2, rows/2), np.random.uniform(-10, 10), 1)
        augmented = cv2.warpAffine(image, M, (cols, rows))
        return augmented

# --- Example Usage ---
if __name__ == "__main__":
    proc = ImageProcessor()
    
    # Simulate raw input from DFD 'Industrial Camera'
    dummy_img = (np.random.rand(500,500,3) * 255).astype('uint8')
    _, buffer = cv2.imencode('.jpg', dummy_img)
    
    try:
        processed_data, info = proc.preprocess(buffer.tobytes())
        print(f"Success! Shape: {processed_data.shape}")
        print(f"Metadata captured: {info}")
    except Exception as e:
        print(f"Error: {e}")