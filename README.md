# Pneumonia Triage Agent

## Overview

The Pneumonia Triage Agent is an AI-based application that combines a pre-trained pneumonia image-classification model with an LLM agent, Red Flag Checker, web search, and a Streamlit interface.

It is designed to analyze a chest X-ray and provide an informational triage response based on the available results.

Note: This project is for educational and research purposes only and is not a medical diagnosis system.

## How It Works

The user opens the Streamlit application and can enter information and upload a chest X-ray.

The uploaded image is passed to the pneumonia prediction tool.

The image is converted to grayscale and resized to 28 × 28 pixels.

The processed image is sent to the pre-trained Keras model.

The model returns a pneumonia prediction probability:

0 = No Pneumonia

1 = Pneumonia

The Red Flag Checker looks for potentially serious warning signs in the user's information.

The Web Search Tool researches pneumonia-related information and provides supporting sources.

The LLM Agent combines the model result, red-flag information, user input, and web research to generate the final response.

The result is displayed in the Streamlit interface.

## Model

The model used by the project is:

best_pneumonia_model.keras

This model was already trained before our project. We did not train it.

The original training data was provided in .npz format. The .npz dataset was used during model training, while our application uses the trained .keras model for prediction.

## Main Components

- Streamlit – User interface and image upload.

- Pneumonia Prediction Tool – Processes the uploaded X-ray and runs the trained model.

- LLM Agent – Coordinates the tools and generates the response.

- Red Flag Checker – Checks for potentially urgent warning signs.

- Web Search – Finds relevant pneumonia information and sources.

- LangChain – Connects the LLM with the tools.

## Project Structure

Pneumonia_Project/

├── core/
     └── agent
├── app.py
     └──pneumonia_traige_agent
├── tools/
      └── image_analysis
      └── llm_tools
      └── red_flag_tool
      └── web_search
      └── pneumonia_tool
├── app.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md

Installation

git clone <repository-url>
cd Pneumonia_Project
pip install -r requirements.txt

Add the required API keys to .env and make sure the model file is in the correct folder.

# Run

- streamlit run app.py

# Limitations

- The model and LLM can make mistakes, and a model probability is not the same as a medical diagnosis. Users should consult qualified healthcare professionals for medical decisions.

