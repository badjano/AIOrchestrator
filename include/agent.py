import datetime
import json
import os
import traceback
from urllib.parse import quote_plus

import openai
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from include.colors import *
from include.helpers import file_safe_name

load_dotenv()

# Get the OpenAI API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set.")

openai.api_key = api_key
client = openai.OpenAI()


class AIAgent:
    def __init__(self, model="gpt-4o-mini"):
        self.create = client.chat.completions.create
        self.model = model
        self.set_subject("General AI Assistant")
        self.messages = [{"role": "user",
                          "content": "Make sure to save the files of the project like scripts, documentation and configs and search the internet when needed by using tools."}]
        self.start_count = len(self.messages)
        self.functions = [
            # {
            #     "type": "function",
            #     "function": {
            #         "name": "fetch_external_info",
            #         "description": "Fetches online external information for a given query.",
            #         "parameters": {
            #             "type": "object",
            #             "properties": {
            #                 "query": {"type": "string", "description": "The search query"}
            #             },
            #             "required": ["query"]
            #         }
            #     }
            # },
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
        self.subject = file_safe_name(subject).lower()
        if os.path.exists("agents/subject_cache.json"):
            with open("agents/subject_cache.json", "r", encoding="utf-8") as f:
                subject_cache = json.load(f) or {}
        else:
            subject_cache = {}
        if self.subject not in subject_cache:
            subject_cache[self.subject] = self.send_no_history(
                f"give me the best system message for this base system message: '{base_prompt}' without any titles and responses, only the system message",
                "gpt-4-turbo")
            with open("agents/subject_cache.json", "w", encoding="utf-8") as f:
                json.dump(subject_cache, f, indent=4, ensure_ascii=False)
        self.set_system_message(subject_cache[self.subject])

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
                print_orange(answer)
            self.add_user_message(
                "Get the best ideas from all suggestions based on coolness, quality, and odds of success, and merge them in a final idea. Elaborate the idea and write it without any explanation.")
            return self.send("gpt-4-turbo")
        self.add_user_message(prompt)
        return self.send("gpt-4-turbo")

    def send(self, model=None):
        print_orange(f"{self.subject} Thinking...")
        response = self.create(
            model=model or self.model,
            messages=self.system_message + self.messages,
            tools=self.functions
        )
        choice = response.choices[0]
        answer = choice.message.content or ""
        if choice.finish_reason == "tool_calls":
            for call in choice.message.tool_calls:
                if answer:
                    answer += "\n\n"
                answer += self.parse_function_call(call)
        if answer:
            self.messages.append({"role": "assistant", "content": answer})
        return answer

    def send_no_history(self, prompt, model=None):
        print_orange(f"{self.subject} Thinking...")
        response = self.create(
            model=model or self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def fetch_external_info(self, query):
        """Fetches external information for the given query and returns markdown-formatted string."""
        safe_query = quote_plus(query)
        url = f"https://www.google.com/search?q={safe_query}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

            # remove HTML tags and extract text
            soup = BeautifulSoup(response.text, "html.parser")
            strip_html_text = soup.get_text(separator="\n").strip()

            return strip_html_text or "No results found."
        except requests.exceptions.RequestException as e:
            return f"Error fetching external information. {e}"

    def save_content_to_file(self, content, filepath):
        """Saves content to a file. Add 'root' folder to filepath if not present."""
        if not filepath.startswith("root" + os.sep):
            filepath = os.path.join("root", filepath)

        if not content:
            print_yellow("No content to save.")
            return
        if not os.path.exists(os.path.dirname(filepath)):
            os.makedirs(os.path.dirname(filepath))
        print_orange(f"Saving content to {filepath}...")
        # Ensure the content is a string
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Content saved to {filepath}."

    def close(self):
        if len(self.messages) > self.start_count:
            print_orange("Saving conversation history...")
            self.save_conversation()
        else:
            print_orange("No conversation history to save.")
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
                    return func(**kwargs) or "Function executed successfully, but no result returned."
                except Exception as e:
                    traceback.print_exc()
                    return f"Error calling function `{function_name}`: {str(e)}"
        return f"Function `{function_name}` not found or not callable."


if __name__ == "__main__":
    os.chdir("../")
    agent = AIAgent()
    answer = agent.fetch_external_info("bitcoin")
    print_yellow(f"Fetched info: {answer}")
    agent.close()