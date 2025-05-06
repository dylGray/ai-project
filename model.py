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

# how we tell the AI model what to do
def build_system_prompt():
    '''Return a system prompt that provides all necessary context for the AI assistant.'''
    # Load the markdown and json files
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

    # Build the prompt context by concatenating the files' content.
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
        "evaluate it using the Priority Pitch Framework, Grading Criteria, and Coaching Guidance provided.\n\n"

        "You must return your evaluation in the following strict format:\n\n"

        "**Grade: A**\n\n"

        "**Pain**:\nClear, emotionally resonant. Describes a real daily frustration.\n\n"
        "**Threat**:\nWell-articulated. Connects pain to a broader business consequence.\n\n"
        "**Belief Statement**:\nStarts with 'We believe…' and focuses on the prospect’s worldview.\n\n"
        "**Relief**:\nSolution addresses the threat. Avoids features; explains outcome.\n\n"
        "**Tone**:\nEmotional, simple, and easy to understand.\n\n"
        "**Length**:\nWithin 100–150 words. Ideal.\n\n"
        "**Clarity**:\nEasy to read and say out loud.\n\n"

        "⚠️ Always:\n"
        "- Start with the grade on its own line, formatted as **Grade: X**.\n"
        "- Include a blank line after the grade.\n"
        "- Use **bold section headers** (Pain, Threat, Belief Statement, etc.), followed by a colon and a newline.\n"
        "- Separate every section with a blank line — DO NOT group sections into a single paragraph.\n"
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

def chat():
    '''Run the AI model locally in the terminal.'''
    print('🧠 Welcome to Your Personal AI Assistant! (type "exit" or "quit" to end session)\n')

    system_prompt = build_system_prompt()
    messages = [{"role": "system", "content": system_prompt}]

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break

        messages.append({"role": "user", "content": user_input})
        response = get_completion_from_messages(messages)
        if response:
            print(f"\nAI 🤖: {response}\n")
            messages.append({"role": "assistant", "content": response})
        else:
            print("Something went wrong. Try again.")

if __name__ == "__main__":
    chat()