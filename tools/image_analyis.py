
from urllib import response

from langchain_core.tools import tool
from google import genai
from dotenv import load_dotenv
import os
import base64
from google.genai import types


# Load environment variables
load_dotenv()


# Create Gemini client
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


@tool
def analyze_pneumonia_image(image_bytes: bytes, mime_type: str) -> str:
    """
    Analyze an uploaded chest X-ray image using Gemini.

    This tool should only be called when a chest X-ray image
    has been uploaded by the user.

    The image is analyzed without requiring the user to
    provide a prompt.
    """

    # Convert image bytes to base64
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    # Instructions Gemini should follow for every uploaded image
    prompt = """
    Analyze this chest X-ray image for educational purposes.

    You should automatically analyze the image without requiring
    the user to provide a question or prompt.

    Explain the following in simple English:

    1. Whether the uploaded image appears to be a chest X-ray.
    2. What can generally be observed in the lungs.
    3. Whether there are visible unusual areas or patterns.
    4. Whether any visible patterns could be associated with pneumonia.
    5. Explain your observations clearly and simply.

    Do not invent findings that cannot be seen in the image.

    Do not give a definitive medical diagnosis.
    Make it clear that AI image analysis cannot replace
    assessment by a qualified medical professional.
    """

# Send image + instructions to Gemini

# Decode base64 string to bytes
    image_bytes = base64.b64decode(image_base64)

    response = client.models.generate_content(
        model="gemini-3.8-flash",  # Or "gemini-1.5-flash"
        contents=[
            types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type,
            ),
             prompt,
        ],
    )

    return response.text or 'No analysis available.'
