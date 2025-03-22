import os
import openai
import json
from dotenv import load_dotenv, find_dotenv

# Load environment variables
_ = load_dotenv(find_dotenv())

# Check if API key is available
if "OPENAI_API_KEY" not in os.environ:
    raise ValueError("API Key not found. Check your .env file.")

openai.api_key = os.environ['OPENAI_API_KEY']

def get_completion_from_messages(messages, model="gpt-3.5-turbo", temperature=0, max_tokens=1000):
    """Fetches completion from OpenAI API with error handling"""
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

delimiter = "####"
system_message = f"""
You will be provided with customer service queries.
The customer service query will be delimited with {delimiter} characters.
Output a python list of objects, where each object has the following format:
    'category': <category_name>,
    'products': <list_of_products>
Only output the list of objects, with nothing else.
"""

user_message = "tell me about the SmartX ProPhone and the FotoSnap DSLR Camera. Also tell me about your TVs"

messages = [
    {"role": "system", "content": system_message},
    {"role": "user", "content": f"{delimiter}{user_message}{delimiter}"}
]

# Fetching product categories and names
category_and_product_response = get_completion_from_messages(messages)
print("Raw API Response:", category_and_product_response)

# Convert the response to a structured format
def parse_response(input_string):
    try:
        return json.loads(input_string.replace("'", "\""))  # Convert single to double quotes
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in response")
        return []

category_and_product_list = parse_response(category_and_product_response)
print("Parsed Response:", category_and_product_list)

# Product information database
products = {
    "SmartX ProPhone": {"category": "Smartphones and Accessories", "description": "A powerful smartphone with advanced camera features.", "price": 899.99},
    "FotoSnap DSLR Camera": {"category": "Cameras and Camcorders", "description": "Capture stunning photos with this versatile DSLR camera.", "price": 599.99},
    "CineView 4K TV": {"category": "Televisions and Home Theater Systems", "description": "A stunning 4K TV with smart features.", "price": 599.99},
    "CineView OLED TV": {"category": "Televisions and Home Theater Systems", "description": "Experience true blacks and vibrant colors with this OLED TV.", "price": 1499.99},
}

# Retrieve product details
def get_product_details(data_list):
    output = ""
    for item in data_list:
        if "products" in item:
            for product in item["products"]:
                if product in products:
                    output += json.dumps(products[product], indent=4) + "\n"
                else:
                    print(f"Warning: Product '{product}' not found")
        elif "category" in item:
            category_products = [p for p, v in products.items() if v["category"] == item["category"]]
            for p in category_products:
                output += json.dumps(products[p], indent=4) + "\n"
    return output

product_info = get_product_details(category_and_product_list)
print("Product Information:", product_info)

# Generate the final response
final_messages = [
    {"role": "system", "content": "You are a helpful customer service assistant."},
    {"role": "user", "content": user_message},
    {"role": "assistant", "content": f"Relevant product information:\n{product_info}"},
]

final_response = get_completion_from_messages(final_messages)
print("Final Response:", final_response)
