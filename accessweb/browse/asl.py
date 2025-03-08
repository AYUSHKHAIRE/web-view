import tensorflow as tf
import numpy as np
import cv2
import base64
from browse.logger_config import logger

class ASL_CNN:
    def __init__(self, model_path):
        logger.warning(f'Loading the model: {model_path}')
        self.class_labels = [str(i) for i in range(10)] + [chr(i) for i in range(ord('A'), ord('Z') + 1)]
        self.model = tf.keras.models.load_model(model_path)

    def preprocess_image_from_base64(self, base64_string, img_size=(255, 255)):
        try:
            if "," in base64_string:
                base64_data = base64_string.split(",")[1]
            else:
                base64_data = base64_string

            image_bytes = base64.b64decode(base64_data)
            image_array = np.frombuffer(image_bytes, dtype=np.uint8)
            img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            
            if img is None:
                logger.error("Invalid Base64 image format.")
                return None, None

            # Save the raw incoming image
            cv2.imwrite("incoming_image.png", img)

            img = cv2.resize(img, img_size)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (11, 11), 0)
            _, binary = cv2.threshold(blurred, 30, 255, cv2.THRESH_BINARY)

            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(largest_contour)

                # Normalize image
                img = img / 255.0
                img = np.expand_dims(img, axis=0)

                return img, (x, y, w, h)

            return None, None
        except Exception as e:
            logger.error(f"Error processing Base64 image: {e}")
            return None, None

    def predict_class_on_base64(self, base64_string):
        processed_image, bbox = self.preprocess_image_from_base64(base64_string)
        if processed_image is None:
            return None, None
        predictions = self.model.predict(processed_image)
        predicted_class_index = np.argmax(predictions)  # Get the class index
        predicted_class_name = self.class_labels[predicted_class_index]
        return predicted_class_name, bbox

# Example Usage:
# AC = ASL_CNN("assets/asl_cnn_model.h5")
# base64_string = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."  # Replace with actual Base64
# predicted_class, bbox = AC.predict_class_on_base64(base64_string)
# print(f"Predicted Class: {predicted_class}")
# print(f"Bounding Box: {bbox}")
