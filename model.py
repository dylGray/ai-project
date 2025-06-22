import os
import json
import yaml
from dotenv import load_dotenv
from openai import OpenAI
from functools import lru_cache

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("API Key not found. Check your .env file.")

client = OpenAI(api_key=api_key)

@lru_cache(maxsize=8)
def load_yaml_cached(path):
    '''Loads and caches YAML files'''
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        if not content.endswith("\n"):
            content += "\n"
            with open(path, "w", encoding="utf-8") as f_out:
                f_out.write(content)
        return yaml.safe_load(content)
    except Exception as e:
        print(f"Warning: Could not load {path}: {e}")
        return {}

def build_system_prompt():
    '''Builds an efficient, structured system prompt from pitch_assets.'''
    framework = load_yaml_cached("pitch_assets/framework.yaml")
    grading = load_yaml_cached("pitch_assets/grading.yaml")
    examples = load_yaml_cached("pitch_assets/examples.yaml")

    # framework overview
    overview = framework.get("overview", {}).get("summary", "")

    # principles
    principles = framework.get("principles", [])
    principles_str = "\n".join(f"- {p['name']}: {p['rule']}" for p in principles)

    # components
    components = framework.get("components", [])
    components_str = "\n".join(
        f"- {c['name']}: {c['goal']} (Must include: {c['must_include']})" for c in components
    )

    # grading criteria
    criteria = grading.get("criteria", [])
    criteria_str = "\n".join(
        f"- {c['name']}: {c['signal']}\n  Example: {c['example']}" for c in criteria
    )

    # notes
    notes = grading.get("notes", [])
    notes_str = "\n".join(f"- {n}" for n in notes)

    # examples
    pitch_examples = examples.get("pitches", [])

    def format_examples(examples, kind):
        '''Formats examples for the system prompt.'''
        if not examples:
            return ""
        example_output = f"\n== {kind} Elevator Pitch Example(s) ==\n"
        for ex in examples:
            example_output += f"Title: {ex.get('title', '')}\n"
            example_output += f"Audience: {ex.get('audience', '')}\n"
            example_output += f"Word Count: {ex.get('word_count', '')}\n"
            example_output += f"Reading Level: {ex.get('reading_level', '')}\n"
            example_output += f"Pitch:\n{ex.get('content', '').strip()}\n"
            eval_type = ex.get('evaluation', {}).get('type', '').lower()
            if eval_type == "good":
                strengths = ex.get('evaluation', {}).get('strengths', [])
                if strengths:
                    example_output += "Strengths: " + "; ".join(strengths) + "\n"
                improvements = ex.get('evaluation', {}).get('improvements', [])
                if improvements:
                    example_output += "Possible Improvements: " + "; ".join(improvements) + "\n"
            elif eval_type == "ok":
                strengths = ex.get('evaluation', {}).get('strengths', [])
                if strengths:
                    example_output += "Strengths: " + "; ".join(strengths) + "\n"
                weaknesses = ex.get('evaluation', {}).get('weaknesses', [])
                if weaknesses:
                    example_output += "Weaknesses: " + "; ".join(weaknesses) + "\n"
                improvements = ex.get('evaluation', {}).get('improvements', [])
                if improvements:
                    example_output += "Suggested Improvements: " + "; ".join(improvements) + "\n"
            elif eval_type == "bad":
                weaknesses = ex.get('evaluation', {}).get('weaknesses', [])
                if weaknesses:
                    example_output += "Weaknesses: " + "; ".join(weaknesses) + "\n"
                improvements = ex.get('evaluation', {}).get('improvements', [])
                if improvements:
                    example_output += "How to Improve: " + "; ".join(improvements) + "\n"
            example_output += "\n"
        return example_output

    good_examples = [ex for ex in pitch_examples if ex.get("evaluation", {}).get("type", "").lower() == "good"]
    ok_examples = [ex for ex in pitch_examples if ex.get("evaluation", {}).get("type", "").lower() == "ok"]
    bad_examples = [ex for ex in pitch_examples if ex.get("evaluation", {}).get("type", "").lower() == "bad"]

    # Prompt assembly
    prompt = f"""
You are an AI trained to strictly evaluate elevator pitches using the Priority Pitch methodology.
You have access to the full Priority Pitch framework, grading criteria, and canonical examples of good and bad pitches. Use all of these resources to inform your evaluation.

== Framework Overview ==
{overview}

== Principles ==
{principles_str}

== Required Components ==
{components_str}

== Grading Criteria ==
{criteria_str}

== Grading Notes ==
{notes_str}

== Examples ==
{format_examples(good_examples, 'Good')}{format_examples(ok_examples, 'OK')}{format_examples(bad_examples, 'Bad')}

Your only job is to evaluate elevator pitches according to the above criteria and examples. Do not provide writing advice or revisions.
"""
    return prompt

def build_fallback_system_prompt():
    '''Builds a fallback system prompt for non-pitch interactions.'''
    lines = [
        "You are a friendly, conversational assistant. ",
        "Your job is twofold:\n",
        "  1. If the user is asking a question or just chatting, respond normally—",
        "     answer their question, engage in small talk, or be helpful.\n",
        "  2. If the user asks for help, advice, or suggestions on writing, revising, or improving their elevator pitch, respond strictly with: ",
        '     "I cannot help you with your elevator pitch. My only functionality is to evaluate your elevator pitch based on The Priority Sales methodology."\n',
        "  3. At the end of your response, once you have addressed the user’s actual message, ",
        "softly remind them that this tool’s main purpose is to evaluate elevator pitches, not improve them or provide feedback. ",
        "Be warm and natural. Do not lecture or judge; simply answer and then funnel them back.\n"
    ]
    return "".join(lines)

def is_valid_pitch(user_input):
    '''
    Classifies user input as either a pitch or non-pitch, with inline placeholder detection.
    Makes a call to OpenAI's GPT model to classify the input.
    '''
    placeholders = ["here is my pitch", "my pitch is", "test", "sample", "coming soon", "tbd", "to be added", "n/a", "na", "none", "placeholder", "draft", "lorem ipsum", "write my pitch", "i will write my pitch", "this is my pitch", "pitch", "elevator pitch", "submit", "hello", "hi", "-", "...", "?", "!", "[your pitch here]", "[insert pitch]"]

    normalized = user_input.strip().lower()
    if normalized in placeholders:
        return {"is_pitch": False, "reason": "Placeholder"}
    for ph in placeholders:
        if normalized.startswith(ph) or normalized.endswith(ph):
            return {"is_pitch": False, "reason": "Placeholder"}
    if len(normalized) < 15:
        return {"is_pitch": False, "reason": "Placeholder"}
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

@lru_cache(maxsize=1)
def get_cached_system_prompt():
    return build_system_prompt()

@lru_cache(maxsize=1)
def get_cached_fallback_system_prompt():
    return build_fallback_system_prompt()