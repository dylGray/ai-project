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
    '''Return a generic system prompt for the AI assistant.'''
    return "You are a helpful assistant."

def get_completion_from_messages(messages, model="gpt-4", temperature=0.5, max_tokens=500):
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