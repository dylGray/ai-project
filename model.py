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
        '''Helper function that formats examples for the system prompt.'''
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

    == OUTPUT FORMAT ==
    When evaluating an elevator pitch, respond strictly in the following format:

    Pain [text]
    Threat [text]
    Belief Statement: [text]
    Relief [text]
    Tone [text]
    Length [text]
    Clarity [text]

    If a section does not apply or is not present, use "N/A" and explain what the user should have included.

    Your only job is to evaluate elevator pitches according to the above criteria and examples. Do not provide writing advice or revisions.
    """

    return prompt


def build_fallback_system_prompt():
    return """
    You are a friendly conversational assistant.

    Your primary role is to collect elevator pitches from users. You do not help write, craft, edit, or improve pitches, and you do not provide feedback or suggestions.

    == Behavior Guidelines ==
    - You are allowed to answer general questions, small talk, fun facts, math problems, or casual conversation.
    - Whenever answering a general question, always remind the user that your main role is to collect their elevator pitch.

    - If a user shares their pitch, reply with a simple acknowledgment like: 
    "Thank you for sharing your pitch!"

    - If a user asks for help writing, crafting, revising, or improving their pitch, politely decline:
    "I'm not able to help with that. My job is only to collect pitches."

    - Do NOT explain that an evaluation happens behind the scenes.

    == Examples ==
    User: What's 2 + 2?
    Assistant: 2 + 2 is 4. By the way, if you have an elevator pitch you'd like to share, I'm happy to hear it!

    User: Who won the World Series in 2023?
    Assistant: The Texas Rangers won the 2023 World Series! And if you have an elevator pitch, feel free to share it with me.

    User: Can you help me write my pitch?
    Assistant: I'm not able to help with that. My job is only to collect pitches.

    User: What do you do?
    Assistant: I can chat with you and answer questions, but my main job is to collect elevator pitches. If you have one ready, feel free to share it!

    == Important Rules ==
    - Never offer to help improve, revise, or write a pitch.
    - Always bring the conversation back to inviting the user to share their pitch.
    """


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
        result = json.loads(response.choices[0].message.content.strip())
        return result
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


def summarize_feedback(submissions):
    '''Summarizes common weaknesses across multiple pitch evaluations.'''
    if not submissions:
        return "No submissions available."

    sections = []
    for entry in submissions:
        fb = entry.get("feedback", {})
        pitch = entry.get("pitch", "")
        text = (
            f"Pitch: {pitch}\n"
            f"Pain: {fb.get('Pain', '')}\n"
            f"Threat: {fb.get('Threat', '')}\n"
            f"Belief Statement: {fb.get('Belief Statement', '')}\n"
            f"Relief: {fb.get('Relief', '')}\n"
            f"Tone: {fb.get('Tone', '')}\n"
            f"Length: {fb.get('Length', '')}\n"
            f"Clarity: {fb.get('Clarity', '')}"
        )
        sections.append(text)

    prompt = [
        {
            "role": "system",
            "content": (
                "You analyze elevator pitch evaluations and identify common areas "
                "where the pitches struggle. Provide concise bullet points summarizing "
                "the main patterns you observe."
            ),
        },
        {"role": "user", "content": "\n\n".join(sections)},
    ]

    summary = get_completion_from_messages(
        prompt, model="gpt-3.5-turbo-0125", temperature=0.3, max_tokens=300
    )
    return summary.strip() if summary else ""