import datetime
import json
import os
import openai
import requests
from dotenv import load_dotenv

from include.colors import print_blue, print_yellow
from include.helpers import file_safe_name

load_dotenv()

# Get the OpenAI API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set.")

openai.api_key = api_key
client = openai.OpenAI()


class AIAgent:
    def __init__(self, model="o4-mini"):
        self.model = model
        self.subject = "General AI Assistant"
        self.messages = []
        self.create = client.chat.completions.create
        self.functions = [
            {
                "type": "function",
                "function": {
                    "name": "fetch_external_info",
                    "description": "Fetches online external information for a given query.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "The search query"}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "save_content_to_file",
                    "description": "Saves content to a file.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {"type": "string", "description": "The content to save"},
                            "filepath": {"type": "string",
                                         "description": "The file path where the content will be saved"}
                        },
                        "required": ["content", "filepath"]
                    }
                }
            }
        ]

    def set_subject(self, subject, personality=None, expertise=None):
        base_prompt = f"You are an expert {subject} assistant."
        if personality:
            base_prompt = f"You are a {personality} {subject} assistant."
        if expertise:
            base_prompt += f" Your expertise level is {expertise}."
        self.subject = subject
        if os.path.exists("agents/subject_cache.json"):
            with open("agents/subject_cache.json", "r", encoding="utf-8") as f:
                subject_cache = json.load(f) or {}
        else:
            subject_cache = {}
        if subject not in subject_cache:
            subject_cache[subject] = self.send_no_history(
                f"give me the best system message for this base system message: '{base_prompt}' without any titles and responses, only the system message",
                "gpt-4.1")
            with open("agents/subject_cache.json", "w", encoding="utf-8") as f:
                json.dump(subject_cache, f, indent=4, ensure_ascii=False)
        self.set_system_message(subject_cache[subject])

    def set_system_message(self, system_message):
        self.system_message = [{"role": "system", "content": system_message}]

    def add_user_message(self, message, reset=False):
        if message:
            if not self.system_message:
                self.set_subject(self.subject)
            self.messages.append({"role": "user", "content": message})
        if reset:
            self.start_count = len(self.messages)

    def chat(self, prompt, complex=False):
        if complex:
            for _ in range(5):
                self.add_user_message(f"Make 10 unique suggestions for the following prompt: '{prompt}'")
                answer = self.send()
                print_blue(answer)
            self.add_user_message(
                "Get the best ideas from all suggestions based on coolness, quality, and odds of success, and merge them in a final idea. Elaborate the idea and write it without any explanation.")
            return self.send("gpt-4.1")
        self.add_user_message(prompt)
        return self.send("gpt-4.1")

    def send(self, model=None):
        print_blue(f"{self.subject} Thinking...")
        response = self.create(
            model=model or self.model,
            messages=self.system_message + self.messages,
            tools=self.functions
        )
        choice = response.choices[0]
        answer = choice.message.content or ""
        if choice.finish_reason == "tool_calls":
            for call in choice.message.tool_calls:
                answer += self.parse_function_call(call)
        if answer:
            self.messages.append({"role": "assistant", "content": answer})
        return answer

    def send_no_history(self, prompt, model=None):
        print_blue(f"{self.subject} Thinking...")
        response = self.create(
            model=model or self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def fetch_external_info(self, query):
        """Fetches external information for the given query."""
        url = f"https://api.duckduckgo.com/?q={query}&format=json"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            abstract = data.get("AbstractText", "")
            return abstract or "No relevant information found."
        return "Failed to fetch external information."

    def save_content_to_file(self, content, filepath):
        """Saves content to a file. Add 'root' folder to filepath if not present."""
        print_blue(f"Saving content to file: {filepath}")
        if not filepath.startswith("root" + os.sep):
            filepath = os.path.join("root", filepath)

        if not content:
            print_yellow("No content to save.")
            return
        if not filepath.endswith(".txt"):
            filepath += ".txt"
        if not os.path.exists(os.path.dirname(filepath)):
            os.makedirs(os.path.dirname(filepath))
        print_blue(f"Saving content to {filepath}...")
        # Ensure the content is a string
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

    def close(self):
        if len(self.messages) > self.start_count:
            print_blue("Saving conversation history...")
            self.save_conversation()
        else:
            print_blue("No conversation history to save.")
        print_yellow("Goodbye!")

    def save_conversation(self):
        log_folder = "logs"
        filename = file_safe_name(self.subject).lower() if self.subject else "chat_log"
        if not os.path.exists(log_folder):
            os.makedirs(log_folder)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_folder, f"{filename}_{timestamp}.json")
        obj = dict(messages=self.messages, timestamp=timestamp)
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(obj, indent=4, ensure_ascii=False))

    def parse_function_call(self, call):
        function_name = call.function.name
        kwargs = json.loads(call.function.arguments)
        if hasattr(self, function_name):
            func = getattr(self, function_name)
            if callable(func):
                try:
                    result = func(**kwargs)
                    return result
                except Exception as e:
                    return f"\n\nError calling function `{function_name}`: {str(e)}"
        return f"\n\nFunction `{function_name}` not found or not callable."
