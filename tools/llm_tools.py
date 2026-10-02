from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Import your tools
from tools.Pneumonia_tool import predict_pneumonia
from tools.image_analyis import analyze_pneumonia_image
from tools.web_search import pneumonia_web_search

import os

load_dotenv()

# Put all tools into one list
tools = [
    predict_pneumonia,
    analyze_pneumonia_image,
    pneumonia_web_search
]

def get_llm(
        temperature=0.2,
        top_k=20,
        top_p=0.95
):
    # Create the LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.8-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=temperature,
        top_k=top_k,
        top_p=top_p
    )

    return llm.bind_tools(tools)