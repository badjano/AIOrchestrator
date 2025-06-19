import glob
import json
import os

from include.colors import print_yellow
from include.orchestrator import Orchestrator


def load_start_state(folder, extension="txt"):
    files = glob.glob(f"{folder}/*.{extension}")
    initial_prompt = None
    print_yellow("Enter the index of the file to start with (or press Enter to skip): ")
    for i, file in enumerate(files):
        print_yellow(f"({i}) - {os.path.basename(file)}")
    index = None
    while index is None:
        try:
            index = int(input())
        except Exception as _:
            return None
    if index < 0 or index >= len(files):
        print_yellow("Invalid index. Starting with an empty chat.")
    elif extension == "json":
        with open(files[index], "r", encoding="utf-8") as f:
            data = json.load(f)
            initial_prompt = data.get("messages", [])
        if not initial_prompt:
            print_yellow("No messages found in the selected JSON file. Starting with an empty chat.")
            initial_prompt = []
        else:
            print_yellow(f"Starting with content from: {files[index]}")
    else:
        with open(files[index], "r", encoding="utf-8") as f:
            initial_prompt = f.read().strip()
        print_yellow(f"Starting with content: {files[index]}")
    return initial_prompt


if __name__ == "__main__":
    # start by listing files under start folder
    print_yellow("Welcome to the AI Assistant Chat!")
    print_yellow("Type 'exit' or 'quit' to end the chat.")
    print_yellow("You can also type an empty message to exit.")

    sys_msg = "You are a highly knowledgeable and articulate assistant with a PhD in Game Design. You provide detailed, well-reasoned, and practical advice on all aspects of game design, including mechanics, player psychology, narrative structure, level design, monetization, accessibility, and cross-platform development. You stay current with industry trends and academic research."

    start = load_start_state("start")
    if not start:
        start = load_start_state("logs", "json")

    agent = Orchestrator.get_instance()
    agent.add_user_message(start, True)
    try:
        while True:
            user_input = input("You: ")
            if user_input.lower() in ["exit", "quit"] or not user_input.strip():
                print("Exiting chat.")
                break
            complex = False
            if user_input.startswith("*"):
                complex = True
                user_input = user_input[1:].strip()
            reply = agent.chat(user_input, complex)
            print_yellow(f"Assistant: {reply}")
    except KeyboardInterrupt:
        print("\nExiting chat.")
    finally:
        agent.close()
