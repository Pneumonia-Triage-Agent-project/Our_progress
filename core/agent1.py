from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    ToolMessage
)

from tools.llm_tools import get_llm

from tools.Pneumonia_tool import predict_pneumonia
from tools.image_analyis import analyze_pneumonia_image
from tools.web_search import pneumonia_web_search
from tools.red_flag_tool import check_red_flags

import tempfile
import os


# ============================================================
# TOOLS
# ============================================================

tools = {
    "predict_pneumonia": predict_pneumonia,
    "analyze_pneumonia_image": analyze_pneumonia_image,
    "pneumonia_web_search": pneumonia_web_search,
    "check_red_flags": check_red_flags
}


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are a pneumonia information assistant.

You have four tools:

1. predict_pneumonia
   Uses the trained pneumonia classification model
   to analyze an uploaded chest X-ray.

2. analyze_pneumonia_image
   Uses Gemini to describe visible observations
   from an uploaded chest X-ray.

3. check_red_flags
   Checks symptoms for predefined emergency warning signs.

4. pneumonia_web_search
   Searches reliable online sources for pneumonia information.

RULES:

- Only analyze an image when an image has been uploaded.
- If an image is uploaded, analyze it automatically.
- The user does not need to provide another prompt.
- Clearly separate the trained model prediction from
  Gemini's image observations.
- Never present an AI prediction as a confirmed diagnosis.
- If the user describes symptoms, use the red-flag checker.
- If red flags are detected, clearly state that urgent
  medical attention is recommended.
- A normal X-ray result must never override a detected
  red flag.
- Use web search when reliable current information or
  verification is needed.
- When web search is used, mention the important sources
  in the answer.
- Use simple English.

RESPONSE FORMAT:

### 🫁 Chest X-ray Analysis

**Trained Model Prediction**
Explain the model result and probabilities.

**Image Observations**
Explain the visible observations from the image.

**Red-Flag Assessment**
Only include this section when symptoms were provided.

**What This Means**
Explain the results in simple language.

**Important**
Remind the user that AI analysis does not replace
professional medical assessment.

Never output:
- JSON
- Python dictionaries
- API response objects
- AIMessage objects
- metadata
- signatures
- "type": "text"
- "extras"
- internal tool information
"""


# ============================================================
# CLEAN CONTENT
# ============================================================

def clean_content(content):
    """
    Convert LangChain/Gemini content into plain text.
    """

    # Normal string
    if isinstance(content, str):
        return content.strip()

    # Gemini/LangChain content blocks
    if isinstance(content, list):

        text_parts = []

        for item in content:

            if isinstance(item, dict):

                if item.get("type") == "text":

                    text = item.get("text", "")

                    if text:
                        text_parts.append(
                            str(text)
                        )

            elif isinstance(item, str):

                text_parts.append(item)

        return "\n\n".join(
            text_parts
        ).strip()

    return str(content).strip()


# ============================================================
# RUN LLM
# ============================================================

def run_llm(
    user_message,
    image_bytes=None,
    mime_type=None,
    temperature=0.2,
    top_k=40,
    top_p=0.95
):

    # --------------------------------------------------------
    # CREATE LLM
    # --------------------------------------------------------

    llm_with_tools = get_llm(
        temperature=temperature,
        top_k=top_k,
        top_p=top_p
    )


    # --------------------------------------------------------
    # STORE IMAGE RESULTS
    # --------------------------------------------------------

    image_results = []


    # ========================================================
    # IMAGE ANALYSIS
    # ========================================================

    if image_bytes is not None:

        image_path = None

        try:

            # ------------------------------------------------
            # Create temporary image file
            # ------------------------------------------------

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".png"
            ) as temp_file:

                temp_file.write(
                    image_bytes
                )

                image_path = temp_file.name


            # ------------------------------------------------
            # TRAINED MODEL
            # ------------------------------------------------

            prediction_result = (
                predict_pneumonia.invoke({
                    "image_path": image_path
                })
            )


            # ------------------------------------------------
            # GEMINI IMAGE ANALYSIS
            # ------------------------------------------------

            try:

                gemini_result = (
                    analyze_pneumonia_image.invoke({
                        "image_bytes": image_bytes,
                        "mime_type": mime_type
                    })
                )

            except Exception as e:

                gemini_result = (
                    "Gemini image analysis is temporarily "
                    "unavailable. The trained model result "
                    "is still available."
                )


            # ------------------------------------------------
            # SAVE RESULTS
            # ------------------------------------------------

            image_results.append(
                f"""
TRAINED MODEL RESULT:

{clean_content(prediction_result)}


GEMINI IMAGE OBSERVATIONS:

{clean_content(gemini_result)}
"""
            )


        finally:

            if image_path is not None:

                if os.path.exists(image_path):

                    os.remove(image_path)


    # ========================================================
    # BUILD USER MESSAGE
    # ========================================================

    if image_results:

        user_content = f"""
{user_message}

A chest X-ray has been uploaded and automatically analyzed.

The analysis results are:

{image_results[0]}

Use these results to produce a clean explanation.

Clearly separate:

1. Trained Model Prediction
2. Image Observations
3. Red-Flag Assessment if symptoms were provided
4. What This Means

Do not claim that the AI has confirmed a diagnosis.
"""

    else:

        user_content = user_message


    # ========================================================
    # CREATE INITIAL MESSAGES
    # ========================================================

    messages = [

        SystemMessage(
            content=SYSTEM_PROMPT
        ),

        HumanMessage(
            content=user_content
        )

    ]


    # ========================================================
    # FIRST LLM CALL
    # ========================================================

    response = llm_with_tools.invoke(
        messages
    )

    messages.append(
        response
    )


    # ========================================================
    # TOOL LOOP
    # ========================================================

    while response.tool_calls:

        for tool_call in response.tool_calls:

            tool_name = tool_call["name"]

            tool_args = tool_call["args"]

            selected_tool = tools.get(
                tool_name
            )


            # ------------------------------------------------
            # TOOL NOT FOUND
            # ------------------------------------------------

            if selected_tool is None:

                tool_result = (
                    f"Tool '{tool_name}' was not found."
                )


            # ------------------------------------------------
            # IMAGE TOOL WITHOUT IMAGE
            # ------------------------------------------------

            elif (
                tool_name in [
                    "predict_pneumonia",
                    "analyze_pneumonia_image"
                ]
                and image_bytes is None
            ):

                tool_result = (
                    "No chest X-ray has been uploaded. "
                    "Do not use the image analysis tool."
                )


            # ------------------------------------------------
            # RED FLAG TOOL WITHOUT SYMPTOMS
            # ------------------------------------------------

            elif (
                tool_name == "check_red_flags"
                and not tool_args.get("symptoms")
            ):

                tool_result = (
                    "No symptoms were provided. "
                    "Do not perform a red-flag assessment yet."
                )


            # ------------------------------------------------
            # RUN TOOL
            # ------------------------------------------------

            else:

                tool_result = selected_tool.invoke(
                    tool_args
                )


            # ------------------------------------------------
            # CONVERT TOOL RESULT TO TEXT
            # ------------------------------------------------

            tool_result = clean_content(
                tool_result
            )


            # ------------------------------------------------
            # ADD TOOL RESULT
            # ------------------------------------------------

            messages.append(
                ToolMessage(
                    content=tool_result,
                    tool_call_id=tool_call["id"]
                )
            )


        # ----------------------------------------------------
        # ASK LLM TO CONTINUE
        # ----------------------------------------------------

        response = llm_with_tools.invoke(
            messages
        )

        messages.append(
            response
        )


    # ========================================================
    # FINAL RESPONSE
    # ========================================================

    return clean_content(
        response.content
    )