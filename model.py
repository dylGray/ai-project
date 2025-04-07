import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("API Key not found. Check your .env file.")

client = OpenAI(api_key=api_key)

def load_user_profile(path="profile.json"):
    '''function to load in my unique data'''
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading profile: {e}")
        return None
    
def build_system_prompt(profile):
    '''function to build system message at the start of each session'''
    prof_skills = ', '.join(profile['skills']['proficient_in'])
    learning_skills = ', '.join(profile['skills']['learning'])
    interests = ', '.join(profile['interests'])
    goals = ', '.join(profile['goals'])

    return (
        f"You are GPT-4, a personal AI assistant for {profile['name']}, "
        f"the {profile['role']} with a background in {profile['education']}. "
        f"You're proficient in {prof_skills} and currently learning {learning_skills}. "
        f"Dylan is interested in {interests}. "
        f"Your tone should always be {profile['tone']}. "
        f"His goals include: {goals}. "
        f"Give personalized, actionable, and helpful advice that fits Dylan’s skill level and ambitions."
    )

def get_completion_from_messages(messages, model="gpt-4", temperature=0.5, max_tokens=500):
    '''function to call OpenAI API to interact with pre-trained AI model'''
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
    '''function to run this AI model locally in the terminal'''
    print('🧠 Welcome to Your Personal AI Assistant! (type "exit" or "quit" to end session)\n')

    profile = load_user_profile()
    if not profile:
        print("❌ Could not load profile. Exiting.")
        return

    system_prompt = build_system_prompt(profile)
    messages = [{"role": "system", "content": system_prompt}]

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break

        messages.append({"role": "user", "content": user_input})
        response = get_completion_from_messages(messages)
        if response:
            print(f"\nDylan's AI 🤖: {response}\n")
            messages.append({"role": "assistant", "content": response})
        else:
            print("Something went wrong. Try again.")

if __name__ == "__main__":
    chat()