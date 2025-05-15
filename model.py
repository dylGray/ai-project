import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("API Key not found. Check your .env file.")

client = OpenAI(api_key=api_key)

def build_system_prompt():
    '''
    Build the system prompt for the AI model by loading context and instructions from markdown files.

    High-level overview:
    - Reads the Priority Pitch framework, grading criteria, coaching guidance, and prompt examples from local files.
    - Concatenates the contents into a single string (context) to provide the model with all necessary background and rules.
    - Appends strict instructions on how to evaluate, grade, and give feedback on user-submitted pitches.
    - Returns the full prompt string, which is sent as the "system" message to the OpenAI API.
    '''
    
    try:
        with open("priority_assets/framework.md", "r") as f:
            framework_md = f.read()
    except Exception as e:
        framework_md = ""
        print(f"Warning: Could not load framework.md: {e}")
        
    try:
        with open("priority_assets/grading.md", "r") as f:
            grading_md = f.read()
    except Exception as e:
        grading_md = ""
        print(f"Warning: Could not load grading.md: {e}")
        
    try:
        with open("priority_assets/coaching.md", "r") as f:
            coaching_md = f.read()
    except Exception as e:
        coaching_md = ""
        print(f"Warning: Could not load coaching.md: {e}")

    # build the prompt context by concatenating the files content
    context = (
        "Priority Pitch Context:\n\n"
        "--- Framework ---\n"
        f"{framework_md}\n\n"
        "--- Grading Criteria ---\n"
        f"{grading_md}\n\n"
        "--- Coaching Guidance ---\n"
        f"{coaching_md}\n\n"
    )
    
    instructions = (
        "You are an AI assistant trained to rigorously evaluate elevator pitches "
        "based on the framework, grading criteria, and coaching guidance provided above.\n\n"
        "Each pitch must be graded using the following categories:\n"
        "Pain, Threat, Belief Statement, Relief, Tone, Length, and Clarity.\n\n"
        "For each category, indicate 'Yes' if it is clearly and effectively present, or 'No' if it is missing or weak. "
        "Follow this format exactly:\n\n"

        "**Pain** Your detailed evaluation of how well the pitch describes the prospect's pain.\n\n"
        "**Threat** Your detailed evaluation of the clarity and impact of the threat.\n\n"
        "**Belief Statement** Your detailed evaluation of whether it starts correctly and focuses on the prospect.\n\n"
        "**Relief** Your detailed evaluation of how well the solution is presented without listing features.\n\n"
        "**Tone** Your evaluation of the language's emotional resonance and clarity.\n\n"
        "**Length** Your evaluation regarding whether the pitch fits within the ideal word count.\n\n"
        "**Clarity** Your evaluation on how easily the pitch could be spoken aloud.\n\n"
    )

    return context + instructions

def get_completion_from_messages(messages, model="gpt-4", temperature=0.4, max_tokens=500):
    '''Calls OpenAI API to interact with the pre-trained AI model.'''
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error fetching completion: {e}")
        return None

def is_valid_pitch(user_input):
    '''
    Uses GPT to decide if the message resembles an elevator pitch.
    Returns True if it seems like a pitch; False if it's just a greeting, question, etc.
    '''
    try:
        check_prompt = [
            {
                "role": "system",
                "content": (
                    "You are a strict classifier that only answers 'Yes' or 'No'. "
                    "Say 'Yes' if the input appears to be an attempt at an elevator pitch, even if incomplete. "
                    "Say 'No' if it’s just a greeting, question, or something unrelated."
                )
            },
            {"role": "user", "content": user_input}
        ]

        response = client.chat.completions.create(
            model="gpt-4",
            messages=check_prompt,
            temperature=0,
            max_tokens=1,
        )

        result = response.choices[0].message.content.strip().lower()
        return result == "yes"

    except Exception as e:
        print("Error during pitch classification:", e)
        return True  # default to allowing if uncertain
