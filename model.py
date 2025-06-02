import os
import json
import yaml
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("API Key not found. Check your .env file.")

client = OpenAI(api_key=api_key)

def build_system_prompt():
    '''
    Builds an efficient, structured system prompt from YAML files.

    - Loads framework principles and grading criteria from YAML files
    - Minimizes token usage while retaining clarity and structure
    - Returns prompt string for injection into OpenAI API
    '''

    try:
        with open("priority_assets/framework.yaml", "r") as f:
            framework = yaml.safe_load(f)
    except Exception as e:
        print(f"Warning: Could not load framework.yaml: {e}")
        framework = {}

    try:
        with open("priority_assets/grading.yaml", "r") as f:
            grading = yaml.safe_load(f)
    except Exception as e:
        print(f"Warning: Could not load grading.yaml: {e}")
        grading = {}

    # build prompt
    lines = []

    lines.append("You are an AI trained to strictly evaluate elevator pitches using the Priority Pitch methodology.\n")

    lines.append("== Framework Overview ==")
    lines.append(framework.get("overview", {}).get("description", ""))

    lines.append("\n== Core Principles ==")
    for key, value in framework.get("core_principles", {}).items():
        lines.append(f"- {key.replace('_', ' ').title()}: {value}")

    lines.append("\n== Required Components ==")
    for comp in framework.get("components", []):
        lines.append(f"- {comp['name']}: {comp['description']}")

    lines.append("\n== Evaluation Criteria ==")
    for criterion in grading.get("criteria", []):
        lines.append(f"{criterion['name']}: {criterion['signal']}")
        lines.append(f"Example: {criterion['example']}\n")

    lines.append("Respond in this exact format:\n")
    for criterion in grading.get("criteria", []):
        lines.append(f"**{criterion['name']}** Your detailed evaluation")

    return "\n".join(lines)

def build_fallback_system_prompt():
    """
    This fallback prompt is used whenever the user message is NOT detected as a pitch.
    The AI should:
      1. Answer the user’s question / greeting / small-talk naturally.
      2. If the user asks for help with their elevator pitch, respond with:
         "I cannot help you with your elevator pitch. My only functionality is to evaluate your elevator pitch in the backend based on our sales methodology. Feel free to share your pitch whenever you're ready."
      3. Otherwise, politely remind them that this is an elevator-pitch grading tool,
         and invite them to share an actual pitch.
    """
    lines = [
        "You are a friendly, conversational assistant. ",
        "Your job is twofold:\n",
        "  1. If the user is asking a question or just chatting, respond normally—",
        "     answer their question, engage in small talk, or be helpful.\n",
        "  2. If the user asks for help, advice, or suggestions on writing, revising, or improving their elevator pitch, respond strictly with: ",
        '     \"I cannot help you with your elevator pitch. My only functionality is to evaluate your elevator pitch in the backend based on our sales methodology.\"\n',
        "  3. At the end of your response, once you have addressed the user’s actual message, ",
        "softly remind them that this tool’s main purpose is to evaluate elevator pitches. ",
        "For example: “By the way, this app is built to evaluate elevator pitches using the Priority Pitch method. Whenever you’re ready, share your pitch and I’ll grade it.”\n\n",
        "Be warm and natural. Do not lecture or judge; simply answer and then funnel them back.\n"
    ]
    return "".join(lines)

def is_valid_pitch(user_input):
    '''Classifies user input as either a pitch or non-pitch.'''

    classification_prompt = [
        {
            "role": "system",
            "content": (
                "You are a classifier that determines whether a user's message is:\n"
                "(A) an elevator pitch, or\n"
                "(B) something else like a greeting, small talk, question, or irrelevant message.\n\n"
                "Respond in this exact JSON format:\n"
                '{"is_pitch": true|false, "reason": "Greeting|SmallTalk|Question|Joke|PitchLike|Empty|Other"}\n\n'
                "Examples:\n"
                'Input: "Who am I speaking with?" → {"is_pitch": false, "reason": "Question"}\n'
                'Input: "Our customers are struggling to keep up with demand..." → {"is_pitch": true, "reason": "PitchLike"}'
            )
        },
        {"role": "user", "content": user_input}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=classification_prompt,
            temperature=0,
            max_tokens=50,
        )
        return json.loads(response.choices[0].message.content.strip())
    except Exception as e:
        print("Error during input classification:", e)
        return {"is_pitch": True, "reason": "Fallback"}

def get_completion_from_messages(messages, model="gpt-4", temperature=0.4, max_tokens=500):
    '''Sends a prompt and message history to OpenAI's GPT model to get a generated completion.'''

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