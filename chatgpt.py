# version 0.8

#TODO: stream, handle token limit, stop using input() handle input manually, handle API key

import json
import os
import sys
import shutil
import re
from ansiwrap import fill
from colorama import Fore, Style, init
from datetime import datetime
import openai

# constants
MODEL = "gpt-4"
# TEMPERATURE = 0.6 # currently unused

# Simple prompt for yes or no, for insertion into increasingly long strings
YES_OR_NO = f"{Fore.RESET}({Fore.GREEN}y{Fore.RESET}, {Fore.RED}n{Fore.RESET})"

WELCOME_MESSAGE = f"Welcome to {Fore.GREEN}ChatGPT{Fore.RESET}, type {Fore.YELLOW}/exit{Fore.RESET} to exit, or type {Fore.YELLOW}/help{Fore.RESET} for a list of commands"
ARROW = "> " + Fore.RESET

# find the conversation folder based on the path of the script file
CONVERSATIONS_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "conversations"
)

if not os.path.exists(CONVERSATIONS_DIR):
    os.makedirs(CONVERSATIONS_DIR)

class Command:
    """
    Class to hold all commands for simplicity
    """

    commands = []

    def __init__(self, keywords, function, message, args_num=0, usage=None):
        """
        Initializes a new Command object.

        Args:
            keywords (str or list): Keyword(s) associated with the command.
            function (callable): The function to execute when the command is invoked.
            message (str): A brief description of the command.
            args_num (int, optional): The number of expected arguments. Defaults to 0.
            usage (str, optional): Usage instructions for the command. Defaults to None.

        Raises:
            ValueError: If the keywords input is not a string or a list of strings.
        """
        if isinstance(keywords, str):
            self.keywords = [keywords]
        elif isinstance(keywords, list) and all(isinstance(item, str) for item in keywords):
            self.keywords = keywords
        else:
            raise ValueError("Input must be a string or a list of strings.")
        
        self.args_num = args_num
        self.function = function
        self.message = message
        self.usage = usage
        Command.commands.append(self)

    @classmethod
    def help(cls):
        """
        Displays the available commands and their descriptions.
        """
        print("Available commands:")
        for command in Command.commands:
            print(f"{Fore.YELLOW}/{command.keywords[0]}", end="\t")
            print(Fore.RESET + command.message)
            if command.usage != None:
                print(f"\t{Fore.BLACK + Style.BRIGHT}USAGE: /{command.keywords[0]} {command.usage + Style.RESET_ALL}")

    @classmethod
    def match_command(cls, command_name):
        """
        Finds the command based on a keyword.

        Args:
            command_name (str): The keyword to search for.

        Returns:
            Command or None: The matched command if found, otherwise None.
        """
        for command in cls.commands:
            if command_name in command.keywords:
                return command
        return None

    @classmethod
    def run(cls, prompt):
        """
        Runs the command based on the provided prompt.

        Args:
            prompt (str): The command and its arguments.
        """
        # Split the prompt into the command and its arguments
        command_name, *args = prompt.split(" ")

        # Find the matching command based on the command name
        command = cls.match_command(command_name)

        if command is not None:
            # Extract the required number of arguments
            args = args[:command.args_num]

            if command.args_num > 0:
                # Call the command's function with the provided arguments
                command.function(*args)
            else:
                # Call the command's function without any arguments
                command.function()
        else:
            print(f"{Fore.RED}Command unrecognized: {command_name}{Fore.RESET}")
            print("Type /help for a list of commands")

class Message:
    """
    Represents a message in the conversation
    """

    messages = []  # Store all the messages in a list
    AI_COLOR = Fore.YELLOW  # Default color for the AI

    COLOR_MAP = {
        "{RED}": Fore.RED,
        "{GREEN}": Fore.GREEN,
        "{YELLOW}": Style.BRIGHT
        + Fore.YELLOW,  # yellow is the AI's default color so BRIGHT yellow is substituted
        "{BLUE}": Fore.BLUE,
        "{MAGENTA}": Fore.MAGENTA,
        "{CYAN}": Fore.CYAN,
        "{WHITE}": Fore.WHITE,
        "{RESET}": Style.RESET_ALL + AI_COLOR,  # reset it but still keep it yellow
        "{BRIGHT}": Style.BRIGHT,
    }  # Colors available to the AI

    def __init__(self, content, role=None):
        """
        Initialize a Message object.

        Args:
            content (str): The content of the message.
            role (str, optional): The role of the message. Defaults to None (user).
        """
        self.content = content
        """The content of the message"""
        self.role = "user" if role == None else role
        """The role of the message"""
        Message.messages.append(self)

    def get(self=None):
        """
        Get the message(s) in the conversation.

        If ran on an object it returns the just it's message object, if ran on the class it returns all of the messages

        Returns:
            dict or list of dict: A single message or a list of messages with their role and content.
        """
        # If the function is called on the class self will be None for some reason ¯\_(ツ)_/¯
        if (self != None):
            return {"role": self.role, "content": self.content}
        else:
            return [
                {"role": message.role, "content": message.content}
                for message in Message.messages
            ]

    @classmethod
    def send(cls, msgContent=None):
        """
        Add the latest message, send the conversation to the OpenAI API and retrieve the AI's response.

        Returns:
            str: The AI's response.
        """
        if msgContent != None:
            Message(msgContent)  # add the message to the list
        print("Thinking...", end="\r")
        # send it all to the AI and get just the message
        try:
            response = (
                openai.ChatCompletion.create(model=MODEL, messages=Message.get())
                .choices[0]
                .message
            )

            # save just the message, return just the content
            Message(response.content, response.role)

            print("            ", end="\r")

            return cls.format_content(response)  # Format it

        except Exception as e:
            return f"{Fore.RED}ERROR: {e}"

    @classmethod
    def format_content(cls, message, history=False):
        """
        Format the content of the message by replacing color placeholders with color codes.

        Args:
            content (str): The content of the message.

        Returns:
            str: The formatted content.
        """
        content = message.content
        
        # replace placeholders with colors listed in color map, but not for system messages
        if message.role != "system":
            for placeholder, color_code in cls.COLOR_MAP.items():
                content = content.replace(placeholder, color_code)

        # get the terminal width
        terminal_width, _ = shutil.get_terminal_size()

        color = cls.AI_COLOR if message.role == "assistant" else Fore.BLUE if message.role == "user" else Fore.RESET

        initial_indent = ""
        subsequent_indent = ""
        if history:
            initial_indent = (f"{cls.AI_COLOR}GPT" if message.role == "assistant" else f"{Fore.BLUE}You" if message.role == "user" else f"{Fore.RESET}Sys") + ": "
            subsequent_indent = "     "

        # Okay, so this part is a mess, it splits the lines in the input first because of a bug in ansiwrap,
        # then it adds the color to the beginning of each line because colors don't work after new lines because ¯\_(ツ)_/¯
        # then combine them back together because ansiwrap can't be trusted around new lines
        formatted = []
        for i, line in enumerate(content.split("\n")):
            formatted.append(
                fill(
                    color + line + Fore.RESET,
                    width=terminal_width,
                    replace_whitespace=False,
                    initial_indent = initial_indent if i == 0 else subsequent_indent,
                    subsequent_indent = subsequent_indent
                )
            )

        return "\n".join(formatted)

    @classmethod
    def reset(cls, silent = False):
        cls.messages = []
        # Send the AI a system message
        Message(
            "You are communicating through the terminal. You can use {COLOR} to change the color of your text for emphasis or whatever you want. Colors available are RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET. You can also switch to BRIGHT colors using {BRIGHT}, and switch back using {RESET}",
            "system",
        )
        if not silent:
            print("Conversation reset")

    @classmethod
    def retry(cls):
        '''
        Retry for a different response
        '''
        cls.messages.pop(-1)
        print(cls.send())

    @classmethod
    def export_json(cls, filename=None):
        """
        Save the conversation messages to a JSON file.

        Args:
            filename (str, optional): The filename of the conversation to save
        """
        # If filename wasn't specified, ask for name or auto generate
        while True:
            if filename is None or filename == "":
                terminal_width, _ = shutil.get_terminal_size()
                print(fill("What would you like to name the file? (Press enter for autogenerated name)", terminal_width))
                filename = input(ARROW)
                if filename == "":
                    # get timestamp and make a filename based on it
                    now = datetime.now()
                    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
                    filename = f"conversation-{timestamp}"
                elif filename == "/cancel":
                    return
            if len(filename) < 1 or re.search(r'[<>:"/\\|?*\0]', filename):
                print(f"{Fore.RED}Invalid name.{Fore.RESET}")
                filename = None
            else:
                break
        
        # make sure it ends in json
        filename += ".json" if filename[-5:] != ".json" else ""

        filepath = os.path.join(CONVERSATIONS_DIR, filename)

        messages_data = [
            {"role": message.role, "content": message.content}
            for message in cls.messages
        ]

        try:
            with open(filepath, "w") as file:
                json.dump(messages_data, file, indent=4)
            print("Conversation saved to:", filepath)
        except PermissionError:
            print(Fore.RED + "ERROR: Permission denied.")
        except Exception as e:
            print(Fore.RED + "ERROR SAVING JSON: " + type(e).__name__)

    @classmethod
    def import_json(cls, filename=None, check=None):
        '''
        Load the conversation from a JSON file

        Args:
            filename (str, optional): The filename of the conversation to load
            check (str, optional): Skips the checks
        '''
        if check != None and filename == "-y":
            filename = check
            check = "-y"

        if check != "-y":
            if filename == "-y":
                filename = None
            else:
                print(f"{Fore.RED}This will clear the current conversation, are you sure? {YES_OR_NO}")
                ques = input(ARROW)
                if ques.lower() == "n":
                    return
        
        # If filename not specified, ask for filename
        if filename == None:
            print("Saved conversations: ")
            for file in os.listdir(CONVERSATIONS_DIR):
                if file[-5:] == ".json":
                    print(f"\t{Fore.YELLOW}" + file[:-5])
            print(f"{Fore.RESET}Input the name of the file.")
            filename = input(ARROW)

        # ensure it ends in '.json'
        filename += ".json" if filename[-5:] != ".json" else ""

        filepath = os.path.join(CONVERSATIONS_DIR, filename)

        if not os.path.isfile(filepath):
            print(f'{Fore.RED}File "{filename}" could not be found')
            return

        with open(filepath, "r") as file:
            data = json.load(file)

        Message.messages = []

        for message in data:
            role = message["role"]
            content = message["content"]
            message = Message(content, role)

        print(f"{Fore.GREEN}Conversation loaded.")
    
    @classmethod
    def history(cls, all=None):
        '''
        Displays the history of the conversation
        '''

        num_messages = 0
        
        for message in Message.messages:
            if message.role == "system" and all != "-a": continue
            num_messages += 1
            print(cls.format_content(message, True), end="\n\n")
        if num_messages == 0:
            print(f"{Fore.RED}There are no messages in history{Fore.RESET}")
    
    @classmethod
    def go_back(cls, num=None):
        try:
            num = int(num)
        except (TypeError, ValueError):
            num = 1
        try:
            for _ in range(2*num):
                cls.messages.pop(-1)
            print(f"{Fore.GREEN}Went back {num} time(s)")
        except IndexError as e:
            print(f"{Fore.RED}Reached the beginning of the conversation")
    
    @staticmethod
    def goodbye():
        Message.reset(silent=True)
        print(Message.send("Goodbye"))
        exit()

# Set up the commands
Command(["bye", "goodbye"], Message.goodbye, "Exit the program and receive a goodbye message")
Command(["exit", "e"], exit, "Exit the program immediately")
Command(["help", "h"], Command.help, "Display this message again")
Command(["save", "s"], Message.export_json, "Save the current conversation to a file", args_num=1, usage="[filename]")
Command(["load", "l"], Message.import_json, "Load a previous conversation", args_num=2, usage="[filename] [-y]")
Command(["hist", "list", "ls"], Message.history, "View the history of the conversation", args_num=1) # secret -a argument to view system messages
Command(["back", "b"], Message.go_back, "Go back in the conversation a certain number of times", args_num=1, usage="[number]")
Command(["retry", "r"], Message.retry, "Generate another response to your last message")
Command(["reset"], Message.reset, "Reset the conversation to its initial state")

# setup
Message.reset(silent=True)

init()  # Initialize colorama for terminal text color support

terminal_width, _ = shutil.get_terminal_size()

# AskGPT mode, include the question in the command and it will try to answer as briefly as it can
if len(sys.argv) > 1:
    args = sys.argv
    if len(args) == 2:
        prompt = args[1].strip('"').strip("'")
    else:
        prompt = " ".join(args[1:])
    Message(
            "You will be asked one short question. You will be as brief as possible with your response, using incomplete sentences if necessary. You will respond with text only, no new lines or markdown elements. After you respond it will be the end of the conversation, do not say goodbye",
            "system",
        )
    print(Message.send(prompt))
    quit()

# Reset the screen, not necessary
os.system('cls' if os.name == 'nt' else 'clear')
print("\033[1;1H", end="")

# Welcome message
print(fill(WELCOME_MESSAGE, width=terminal_width, replace_whitespace=False))

#LOOP

while True:
    # Get input
    prompt = input(Style.RESET_ALL + Fore.BLUE + "Chat " + ARROW)

    if prompt and prompt[0] == "/" and prompt[1:]:
        Command.run(prompt[1:])
    else:
        print(Message.send(prompt))