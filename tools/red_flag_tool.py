from langchain_core.tools import tool

RED_FLAGS = {
    "Severe trouble breathing":[
        "difficulty breathing", "trouble breathing", "struggling to breathe",
        "can't breathe", "gasping", "hard to breathe", "cannot breathe"
    ],
    "bluish lips and face":[
        "blue lips", "bluish lips", "lips turning blue", "blue face", "turning blue", "face turning blue", "bluish face"
    ],
    "severe chest pain":[
        "chest pains", "pains around the chest", "sharp chest pains", "stabbing chest pain"
    ],
     "Rapid breathing or low blood pressure": [
        "breathing fast", "fast breathing", "rapid breathing", "breathing very fast", "low blood pressure", "rapid heart beat"
    ],
      "Confusion or altered mental state": [
        "very drowsy", "hard to wake", "difficult to wake", "unresponsive",
        "won't wake up", "limp", "confused", "trouble staying awake"
    ],
}

# A tool an agent can call
@tool
def check_red_flags(symptoms:str) ->str:
    """Check the symptoms a parent has described for danger signs that
    require urgent attention, such as difficulty breathing or bluish lips.
    Call this after gathering symptoms, using everything the user has
    said so far. This is a fixed rule check, not a diagnosis."""

    text = symptoms.lower()

    # An empty list to collect the red flag found
    found=[]

    for flag_name, phrases in RED_FLAGS.items():
        for phrase in phrases:
            if phrase in text:
                found.append(flag_name)
                break

    if found:  
        return (
            "RED FLAG FOUND: " + ", ".join(found) + ". "
            "Urgency must be escalated regardless of the X-ray result."
            "seek urgent medical attention"
        )

    return (
        "No red flags detected in the symptoms described so far. "
        "This does not mean the patient is safe; it only means none of the "
        "listed danger signs were reported yet."
    )

