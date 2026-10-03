import streamlit as st
import hashlib
import re

from core.agent1 import run_llm


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Pneumonia AI Assistant",
    page_icon="🫁",
    layout="wide"
)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "image_bytes" not in st.session_state:
    st.session_state.image_bytes = None

if "mime_type" not in st.session_state:
    st.session_state.mime_type = None

if "last_image_id" not in st.session_state:
    st.session_state.last_image_id = None

# Store verified web sources
if "verified_sources" not in st.session_state:
    st.session_state.verified_sources = []


# ============================================================
# FUNCTION TO PROCESS LLM RESPONSE
# ============================================================

def process_response(response):
    """
    Converts the response from run_llm into:
        answer
        sources

    Preferred format from run_llm:

    {
        "answer": "...",
        "sources": [
            {"title": "...", "url": "..."}
        ]
    }

    It also supports a normal string response.
    """

    # --------------------------------------------------------
    # If run_llm returns a dictionary
    # --------------------------------------------------------

    if isinstance(response, dict):

        answer = response.get("answer", "")

        sources = response.get("sources", [])

        if not isinstance(answer, str):
            answer = str(answer)

        if not isinstance(sources, list):
            sources = []

        return answer.strip(), sources


    # --------------------------------------------------------
    # If run_llm returns a normal string
    # --------------------------------------------------------

    if isinstance(response, str):

        answer = response.strip()

        # Try to find URLs in the response
        urls = re.findall(
            r'https?://[^\s\]\)>,]+',
            answer
        )

        sources = []

        for url in urls:

            # Remove punctuation that may be attached to URL
            url = url.rstrip(".,;:")

            sources.append({
                "title": url,
                "url": url
            })

        return answer, sources


    # --------------------------------------------------------
    # If response is another type
    # --------------------------------------------------------

    return str(response).strip(), []


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("⚙️ Agent Settings")

    st.write(
        "Adjust how the language model responds."
    )

    # --------------------------------------------------------
    # TEMPERATURE
    # --------------------------------------------------------

    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.2,
        step=0.1,
        help="Controls how creative or predictable the LLM response is."
    )

    # --------------------------------------------------------
    # TOP K
    # --------------------------------------------------------

    top_k = st.slider(
        "Top K",
        min_value=1,
        max_value=100,
        value=40,
        step=1,
        help="Controls how many likely tokens the model considers."
    )

    # --------------------------------------------------------
    # TOP P
    # --------------------------------------------------------

    top_p = st.slider(
        "Top P",
        min_value=0.0,
        max_value=1.0,
        value=0.95,
        step=0.05,
        help="Controls the probability range of tokens considered."
    )

    st.divider()

    st.subheader("Current settings")

    st.write(
        f"Temperature: **{temperature}**"
    )

    st.write(
        f"Top K: **{top_k}**"
    )

    st.write(
        f"Top P: **{top_p}**"
    )

    st.divider()

    # --------------------------------------------------------
    # CLEAR CONVERSATION
    # --------------------------------------------------------

    if st.button(
        "🗑️ Clear conversation",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.session_state.image_bytes = None

        st.session_state.mime_type = None

        st.session_state.last_image_id = None

        st.session_state.verified_sources = []

        st.rerun()


# ============================================================
# HEADER
# ============================================================

st.title("🫁 Pneumonia AI Assistant")


# ============================================================
# TOP AREA
# ============================================================

# Create two columns:
# Left  = description
# Right = verified sources checker

header_left, header_right = st.columns(
    [4, 1]
)


# ============================================================
# LEFT HEADER
# ============================================================

with header_left:

    st.write(
        "Upload a chest X-ray for automatic analysis, "
        "describe symptoms, or ask a question about pneumonia."
    )

    st.warning(
        "This application provides AI-based information "
        "and does not replace evaluation by a qualified "
        "healthcare professional."
    )


# ============================================================
# RIGHT HEADER - VERIFIED SOURCES
# ============================================================

with header_right:

    st.markdown(
        "### 🔎 Verified Sources"
    )

    # Number of sources
    source_count = len(
        st.session_state.verified_sources
    )

    if source_count > 0:

        st.success(
            f"{source_count} source(s) available"
        )

        with st.expander(
            "Check sources",
            expanded=False
        ):

            st.write(
                "Use these sources to verify or learn "
                "more about the information provided."
            )

            for i, source in enumerate(
                st.session_state.verified_sources,
                start=1
            ):

                if isinstance(source, dict):

                    title = source.get(
                        "title",
                        f"Source {i}"
                    )

                    url = source.get(
                        "url",
                        ""
                    )

                else:

                    title = f"Source {i}"

                    url = str(source)


                if url:

                    st.markdown(
                        f"**{i}. {title}**"
                    )

                    st.link_button(
                        "Open source",
                        url,
                        use_container_width=True
                    )

    else:

        st.info(
            "Verified web sources will appear here "
            "when the web-search tool is used."
        )


# ============================================================
# DISPLAY PREVIOUS CHAT
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# ============================================================
# IMAGE UPLOADER
# ============================================================

uploaded_file = st.file_uploader(
    "Upload a chest X-ray",
    type=[
        "jpg",
        "jpeg",
        "png"
    ],
    help="Upload a chest X-ray image for automatic analysis."
)


# ============================================================
# HANDLE IMAGE UPLOAD
# ============================================================

if uploaded_file is not None:

    image_bytes = uploaded_file.getvalue()

    mime_type = uploaded_file.type


    # --------------------------------------------------------
    # CREATE IMAGE ID
    # --------------------------------------------------------

    image_id = hashlib.md5(
        image_bytes
    ).hexdigest()

    new_image = (
        image_id
        != st.session_state.last_image_id
    )


    # --------------------------------------------------------
    # SAVE IMAGE
    # --------------------------------------------------------

    st.session_state.image_bytes = image_bytes

    st.session_state.mime_type = mime_type


    # --------------------------------------------------------
    # DISPLAY IMAGE
    # --------------------------------------------------------

    st.image(
        image_bytes,
        caption="Uploaded chest X-ray",
        use_container_width=True
    )


    # --------------------------------------------------------
    # AUTOMATIC ANALYSIS
    # --------------------------------------------------------

    if new_image:

        st.session_state.last_image_id = image_id

        st.info(
            "New chest X-ray detected. "
            "Starting automatic analysis..."
        )

        try:

            with st.spinner(
                "Analyzing chest X-ray..."
            ):

                raw_response = run_llm(

                    user_message=(
                        "Analyze the uploaded chest X-ray. "
                        "The user has not provided a specific "
                        "question, so automatically perform "
                        "the image analysis. "
                        "Do not ask the user for another prompt."
                    ),

                    image_bytes=image_bytes,

                    mime_type=mime_type,

                    temperature=temperature,

                    top_k=top_k,

                    top_p=top_p
                )


            # ------------------------------------------------
            # CLEAN RESPONSE
            # ------------------------------------------------

            response, sources = process_response(
                raw_response
            )


            # ------------------------------------------------
            # SAVE SOURCES
            # ------------------------------------------------

            if sources:

                st.session_state.verified_sources = sources


            # ------------------------------------------------
            # SAVE RESPONSE
            # ------------------------------------------------

            st.session_state.messages.append({

                "role": "assistant",

                "content": response

            })


            # ------------------------------------------------
            # REFRESH
            # ------------------------------------------------

            st.rerun()


        except Exception as e:

            st.error(
                f"Image analysis failed: {e}"
            )


# ============================================================
# CHAT INPUT
# ============================================================

user_question = st.chat_input(
    "Describe symptoms or ask a question about pneumonia..."
)


# ============================================================
# HANDLE USER QUESTION
# ============================================================

if user_question:

    # --------------------------------------------------------
    # SAVE USER MESSAGE
    # --------------------------------------------------------

    st.session_state.messages.append({

        "role": "user",

        "content": user_question

    })


    # --------------------------------------------------------
    # DISPLAY USER MESSAGE
    # --------------------------------------------------------

    with st.chat_message("user"):

        st.markdown(
            user_question
        )


    # --------------------------------------------------------
    # RUN AGENT
    # --------------------------------------------------------

    try:

        with st.chat_message("assistant"):

            with st.spinner(
                "Checking your information..."
            ):

                raw_response = run_llm(

                    user_message=user_question,

                    image_bytes=(
                        st.session_state.image_bytes
                    ),

                    mime_type=(
                        st.session_state.mime_type
                    ),

                    temperature=temperature,

                    top_k=top_k,

                    top_p=top_p
                )


            # ------------------------------------------------
            # CLEAN RESPONSE
            # ------------------------------------------------

            response, sources = process_response(
                raw_response
            )


            # ------------------------------------------------
            # SAVE SOURCES
            # ------------------------------------------------

            if sources:

                st.session_state.verified_sources = sources


            # ------------------------------------------------
            # DISPLAY RESPONSE
            # ------------------------------------------------

            st.markdown(
                response
            )


        # ----------------------------------------------------
        # SAVE ASSISTANT RESPONSE
        # ----------------------------------------------------

        st.session_state.messages.append({

            "role": "assistant",

            "content": response

        })


    except Exception as e:

        st.error(
            f"An error occurred: {e}"
        )