import cv2
import numpy as np
import os

class ImageProcessor:
    """
    Handles loading and preprocessing of images specifically for CNN training.
    """
    
    def __init__(self, target_size=(224, 224), color_mode='rgb'):
        """
        :param target_size: Tuple (width, height) - standard is (224, 224) for VGG/ResNet.
        :param color_mode: 'rgb' for 3 channels, 'grayscale' for 1 channel.
        """
        self.target_size = target_size
        self.color_mode = color_mode

    def preprocess(self, source):
        """
        Input: 
            source: Can be a file path (str) or raw image bytes.
        Output: 
            A normalized numpy array of shape (224, 224, 3) ready for a CNN.
        """
    
        img_array = self._load_image(source)
        
        if img_array is None:
            raise ValueError(f"Could not load image from source: {source}")

    
        if self.color_mode == 'grayscale':
            img_array = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
        else:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)

        
        img_array = cv2.GaussianBlur(img_array, (3, 3), 0)
        img_array = cv2.resize(img_array, self.target_size)
        img_normalized = img_array.astype("float32") / 255.0

        if self.color_mode == 'grayscale':
            img_normalized = np.expand_dims(img_normalized, axis=-1)

        return img_normalized

    def _load_image(self, source):
        """Helper to load from path or bytes."""
        
        if isinstance(source, str):
            if os.path.exists(source):
                return cv2.imread(source)
            else:
                return None
        
        elif isinstance(source, bytes):
            nparr = np.frombuffer(source, np.uint8)
            return cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return None


if __name__ == "__main__":

    processor = ImageProcessor(target_size=(224, 224))
    
    
    # In a real scenario: valid_images = glob.glob("dataset/defective/*.jpg")
    
    # dummy image processing
    dummy_image = np.zeros((500, 500, 3), dtype=np.uint8)
    cv2.rectangle(dummy_image, (50, 50), (450, 450), (255, 0, 0), -1)
    success, encoded_image = cv2.imencode('.jpg', dummy_image)
    raw_bytes = encoded_image.tobytes()

    print("--- Starting Preprocessing ---")
    
    try:
    
        cnn_input = processor.preprocess(raw_bytes)
        
        print(f"Original Shape (Simulated): 500x500x3")
        print(f"Processed Shape: {cnn_input.shape}")      
        print(f"Data Type: {cnn_input.dtype}")            
        print(f"Value Range: {cnn_input.min()} to {cnn_input.max()}") 
        
        '''For using in model.fit() we usually need to add a batch dimension
        shape becomes (1, 224, 224, 3)'''
        batch_input = np.expand_dims(cnn_input, axis=0)
        print(f"Batch Shape (ready for model.predict/fit): {batch_input.shape}")

    except Exception as e:
        print(f"Error: {e}")