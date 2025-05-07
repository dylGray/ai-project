import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("API Key not found. Check your .env file.")
else:
    print(f"API Key: {api_key}")

client = OpenAI(api_key=api_key)

def build_system_prompt():
    '''
    Build the system prompt for the AI model by loading context and instructions from markdown and JSON files.

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
        
    try:
        with open("priority_assets/prompts.json", "r") as f:
            prompts_json = f.read()
    except Exception as e:
        prompts_json = ""
        print(f"Warning: Could not load prompts.json: {e}")

    # build the prompt context by concatenating the files content
    context = (
        "Priority Pitch Context:\n\n"
        "--- Framework ---\n"
        f"{framework_md}\n\n"
        "--- Grading Criteria ---\n"
        f"{grading_md}\n\n"
        "--- Coaching Guidance ---\n"
        f"{coaching_md}\n\n"
        "--- Follow-Up Prompt Examples ---\n"
        f"{prompts_json}\n\n"
    )
    
    instructions = (
        "You are a professional AI assistant trained to evaluate Priority Pitches. When a user submits a Priority Pitch, "
        "evaluate it rigorously using the Priority Pitch Framework, Grading Criteria, and Coaching Guidance provided. "
        "Keep in mind that most pitches will not meet the criteria; therefore, be strict in your grading and clear in your feedback.\n\n"

        "First, analyze the user's pitch and identify which of the following required elements are present: "
        "Pain, Threat, Belief Statement, Relief, Tone, Length, and Clarity. "
        "List the elements that are present in the pitch, and then clearly state which elements are missing.\n\n"

        "If any required elements are missing, inform the user exactly which ones are missing and explain that a full and accurate grade cannot be given until all required elements are included. "
        "Encourage the user to revise their pitch to include the missing elements for a complete assessment.\n\n"

        "If all required elements are present, proceed to return your evaluation in the following strict format:\n\n"

        "When listing your evaluation for each required element, include a ✅ if the element is clearly present, or a ❌ if it is missing or weak. Place the icon directly next to the section title."

        "**Grade: X**\n\n"
        "**Pain** ✅ or ❌\n[Your detailed evaluation of how well the pitch describes the prospect's pain.]\n\n"
        "**Threat** ✅ or ❌\n[Your detailed evaluation of the clarity and impact of the threat.]\n\n"
        "**Belief Statement** ✅ or ❌\n[Your detailed evaluation of whether it starts correctly and focuses on the prospect.]\n\n"
        "**Relief** ✅ or ❌\n[Your detailed evaluation of how well the solution is presented without listing features.]\n\n"
        "**Tone** ✅ or ❌\n[Your evaluation of the language's emotional resonance and clarity.]\n\n"
        "**Length** ✅ or ❌\n[Your evaluation regarding whether the pitch fits within the ideal word count.]\n\n"
        "**Clarity** ✅ or ❌\n[Your evaluation on how easily the pitch could be spoken aloud.]\n\n"

        "Always:\n"
        "- Use a harsh grading scale; if there are any deviations from the guidelines, penalize accordingly.\n"
        "- Start with the grade on its own line, formatted as **Grade: X**.\n"
        "- Include a blank line after the grade.\n"
        "- Separate each evaluation section with a blank line. Do not group multiple sections into a single paragraph.\n"
        "- Do not provide a revised pitch unless explicitly asked.\n"
    )

    return context + instructions

def get_completion_from_messages(messages, model="gpt-4", temperature=0.4, max_tokens=500):
    '''Call OpenAI API to interact with the pre-trained AI model.'''
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