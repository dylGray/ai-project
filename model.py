import os
import openai
import tiktoken
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file

openai.api_key  = os.environ['OPENAI_API_KEY']

# these LLM models take in user input and analyzes the text into tokens (words, punctuation, etc.)
# these tokens, the English language, are typically broken into 4 chars long, or 3/4 of a word
# there are limits to the number of tokens that can be processed at once, processing the user input and models output

def get_completion_and_token_count(messages, 
                                   model="gpt-3.5-turbo", 
                                   temperature=0, 
                                   max_tokens=500):
    
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature, 
        max_tokens=max_tokens,
    )
    
    content = response.choices[0].message["content"]
    
    # how to track the number of tokens used in the response
    token_dict = {
        'prompt_tokens':response['usage']['prompt_tokens'],
        'completion_tokens':response['usage']['completion_tokens'],
        'total_tokens':response['usage']['total_tokens'],
    }

    return content, token_dict

messages = [
    {'role':'system', 
    'content':"""You are an assistant who responds in the style of Dr Seuss."""},    
    {'role':'user',
    'content':"""write me a very short poem about a happy carrot"""},  
] 
response, token_dict = get_completion_and_token_count(messages)
print(response)
print(token_dict)