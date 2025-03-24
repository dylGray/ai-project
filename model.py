import os
import openai
from dotenv import load_dotenv
from outlook_calendar import format_calendar_events  # Import calendar function

load_dotenv()

if "OPENAI_API_KEY" not in os.environ:
    raise ValueError("API Key not found. Check your .env file.")

openai.api_key = os.environ['OPENAI_API_KEY']

def get_completion_from_messages(messages, model="gpt-4", temperature=0.5, max_tokens=500):
    """Function that fetches completion from OpenAI API with error handling"""
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature, 
            max_tokens=max_tokens,
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Error fetching completion: {e}")
        return None

def get_productivity_recommendations():
    """Function that generates productivity suggestions based on the calendar schedule."""
    calendar_summary = format_calendar_events()  # Get the user's schedule
    
    messages = [
        {"role": "system", "content": "You are an AI productivity assistant that optimizes the user's daily schedule."},
        {"role": "user", "content": f"My schedule for today is:\n{calendar_summary}\nHow can I make my day more productive?"}
    ]
    
    return get_completion_from_messages(messages, model="gpt-4", temperature=0.5, max_tokens=500)

if __name__ == "__main__":
    recommendations = get_productivity_recommendations()
    print("\n📅 AI Productivity Recommendations:\n")
    print(recommendations)
