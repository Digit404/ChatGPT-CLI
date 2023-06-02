# ChatGPT CLI

This project is a terminal-based interface for interacting with OpenAI's ChatGPT model. It allows users to have text-based conversations with the AI, ask questions, and receive responses.

## Features

- Simple and intuitive command-based interface
- Colorful and formatted messages for easy readability
- Conversation history and navigation
- Saving and loading conversations from JSON files
- Retry option to generate alternative responses
- AskGPT mode for brief answers to questions

## Installation

1. Get an [Open AI API key](https://platform.openai.com/account/api-keys)

2. Set API key as OPENAI_API_KEY environment variable
	```shell
	export OPENAI_API_KEY='sk-...'
	```

3. Clone the repository:

   ```shell
   git clone https://github.com/Digit404/ChatGPT-CLI.git
   ```

4. Install the required dependencies:

   ```shell
   pip install -r requirements.txt
   ```

5. Works best when added to PATH, so it can be used from anywhere!

## Usage

1. Start the ChatGPT terminal interface:

   ```shell
   python chatgpt.py
   ```

2. Or add the prompt after the file to get a brief answer to your question

	```shell
	python chatgpt.py "What is the capital of Ecuador?"
	```

## Commands

The following commands are available within the terminal interface:

- `/help`: Display a list of available commands and their descriptions.
- `/exit` or `/e`: Exit the program and receive a goodbye message.
- `/save [filename]` or `/s [filename]`: Save the current conversation to a JSON file.
- `/load [filename] [-y]` or `/l [filename] [-y]`: Load a previous conversation from a JSON file.
- `/hist`, `/list`, or `/ls`: View the history of the conversation.
- `/back [number]` or `/b [number]`: Go back in the conversation a certain number of times.
- `/retry` or `/r`: Generate another response to your last message.
- `/reset`: Reset the conversation to its initial state.
