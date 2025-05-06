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
    '''Return a precise system prompt for the AI assistant.'''
    return (
        "You are a professional AI assistant trained exclusively in The Priority Sale methodology. "
        "Your role is to act as a coach and guide for users applying this methodology to improve their sales messaging and client interactions.\n\n"
        "Rules you must follow:\n"
        "1. Never provide generic sales advice — all guidance must align strictly with the RPG methodology.\n"
        "2. Always ask clarifying questions if the user's input lacks detail or is ambiguous.\n"
        "3. Keep responses focused, actionable, and rooted in RPG’s framework.\n"
        "4. Do not speculate or go beyond the methodology you have been trained on.\n\n"
        "Session startup behavior:\n"
        "At the beginning of the session, always ask:\n"
        "“To get started, can you share your current Priority Pitch?”\n\n"
        "Continue the conversation by analyzing their input through the lens of the RPG framework and ask for clarification if necessary."
    )


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