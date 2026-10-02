from langchain_core.tools import tool
from tensorflow import keras
from PIL import Image
import numpy as np

model = keras.models.load_model("tools/best_pneumonia_model.keras")

@tool
def predict_pneumonia(image_path: str) -> str:
    """
    Analyze a chest X-ray image for signs of pneumonia.
    Only call this tool when the user has uploaded an image.
    """

    image = Image.open(image_path)

    # Same preprocessing used during training
    image = image.convert("L")
    image = image.resize((28, 28))
    image = np.array(image)

    # Batch + channel dimensions
    image = np.expand_dims(image, axis=-1)
    image = np.expand_dims(image, axis=0)

    prediction = model.predict(image, verbose=0)

    probability = float(prediction[0][0])

    # If model outputs a probability between 0 and 1
    pneumonia_probability = probability * 100
    normal_probability = (1 - probability) * 100

    if probability >= 0.1:
        label = "Pneumonia"
    else:
        label = "Normal"

    return (
        f"Prediction: {label}\n"
        f"Pneumonia probability: {pneumonia_probability:.2f}%\n"
        f"Normal probability: {normal_probability:.2f}%"
    )