import tensorflow as tf
import numpy as np
import cv2
import os
from browse.logger_config import logger

class ASL_CNN:
    def __init__(self,model_path):
        logger.warning(f'loading the model , {model_path}')
        self.class_labels = [str(i) for i in range(10)] + [chr(i) for i in range(ord('A'), ord('Z') + 1)]
        self.model = tf.keras.models.load_model(model_path)

    def preprocess_image(self,img_path, img_size=(255, 255)):
        img = cv2.imread(img_path)  # Read image
        img = cv2.resize(img, img_size)  # Resize to match training size
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (11, 11), 0)
        _, binary = cv2.threshold(blurred, 30, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
            img = img / 255.0  
            img = np.expand_dims(img, axis=0)
            return img, (x, y, w, h)
        return None, None 
    
    def predict_class_on_image(self,sample_image_path):
        processed_image, bbox = AC.preprocess_image(sample_image_path)
        predictions = self.model.predict(processed_image)
        predicted_class_index = np.argmax(predictions)  # Get the class index
        predicted_class_name = self.class_labels[predicted_class_index]
        return  predicted_class_name, bbox

# AC = ASL_CNN("assets/asl_cnn_model.h5")
# sample_image_path = "assets/hand1_0_bot_seg_5_cropped.jpeg"


# if AC is not None:
#     predicted_class_name,bbox = AC.predict_class_on_image(sample_image_path=sample_image_path)
#     print(f"Predicted Class: {predicted_class_name}")
#     print(f"Bounding Box Coordinates: x={bbox[0]}, y={bbox[1]}, width={bbox[2]}, height={bbox[3]}")
# else:
#     print("No hand detected in the image.")
