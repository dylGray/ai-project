# OpenAI API Chat Application (for now)

## Introduction
This project is an interactive chat application that allows users to communicate with AI models. The application is designed to eventually support toggling between different AI models, providing flexibility based on the user's needs. Currently, the base model is the OpenAI API, and the specific models available for interaction are still under development.

## Installation
To get started, clone the repository and install the necessary dependencies:

```bash
git clone https://github.com/yourusername/OpenAI-API-Chat-App.git
cd OpenAI-API-Chat-App
pip install -r requirements.txt
```

## Usage
Before using the application, make sure you have an OpenAI API key. You can obtain one from the [OpenAI website](https://platform.openai.com/signup/).

Set your API key as an environment variable:

```bash
export OPENAI_API_KEY='your-api-key'
```

Run the Flask development server:

```bash
python app.py
```

Visit `http://127.0.0.1:5000` in your browser to access the chat interface.

## Features
- **Interactive Chat**: Communicate with an AI model in real-time.
- **Model Flexibility (Coming Soon)**: The ability to toggle between different AI models is under development.
- **Customizable Prompts**: The application uses a personalized system prompt based on user data.

## Development Status
This application is actively in development. While the base functionality is operational, features like model toggling and additional enhancements are being worked on.

## Contributing
Contributions are welcome! Feel free to fork the repository and submit a pull request.

## License
This project is licensed under the MIT License.