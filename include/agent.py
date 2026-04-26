import datetime
import json
import os
import traceback
from urllib.parse import quote_plus

import openai
from openai import OpenAI
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from include.colors import *
from include.helpers import file_safe_name

# For local GGUF loading
try:
    from llama_cpp import Llama
    HAS_LLAMA_CPP = True
except ImportError:
    HAS_LLAMA_CPP = False

import re

load_dotenv()

# --- CONFIGURATION ---
MODEL_PATH = r"E:\llm-models\lmstudio-community\gemma-4-26B-A4B-it-GGUF\gemma-4-26B-A4B-it-Q4_K_M.gguf"
LM_STUDIO_URL = os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1")
DEFAULT_MODEL = "gpt-4o-mini"
USE_LOCAL_SERVER = os.getenv("USE_LOCAL_SERVER", "true").lower() == "true"

local_llm = None

def get_local_llm():
    global local_llm
    if local_llm is None and HAS_LLAMA_CPP:
        if os.path.exists(MODEL_PATH):
            try:
                local_llm = Llama(model_path=MODEL_PATH, n_ctx=4096, n_gpu_layers=-1, verbose=False)
            except Exception:
                pass
    return local_llm

class AIAgent:
    def __init__(self, model=None, tools_whitelist=None, system_message=None):
        self.model = model or (os.path.basename(MODEL_PATH) if USE_LOCAL_SERVER else DEFAULT_MODEL)
        self.subject = "General AI Assistant"
        self.messages = [{"role": "user",
                          "content": "Make sure to save the files of the project like scripts, documentation and configs and search the internet when needed by using tools."}]
        self.start_count = len(self.messages)
        
        # Define all possible functions
        self.all_functions = {
            "save_content_to_file": {
                "type": "function",
                "function": {
                    "name": "save_content_to_file",
                    "description": "Saves content to a file.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {"type": "string", "description": "The content to save"},
                            "filepath": {"type": "string", "description": "The file path where the content will be saved"}
                        },
                        "required": ["content", "filepath"]
                    }
                }
            },
            "fetch_external_info": {
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
            }
        }

        # Filter functions based on whitelist
        if tools_whitelist is None:
            self.functions = list(self.all_functions.values())
        else:
            self.functions = [v for k, v in self.all_functions.items() if k in tools_whitelist]

        if system_message:
            self.set_system_message(system_message)
        
        if USE_LOCAL_SERVER:
            self.client = OpenAI(base_url=LM_STUDIO_URL, api_key="lm-studio")
        else:
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def set_subject(self, subject, personality=None, expertise=None):
        base_prompt = f"You are an expert {subject} assistant."
        if personality:
            base_prompt = f"You are a {personality} {subject} assistant."
        if expertise:
            base_prompt += f" Your expertise level is {expertise}."
        self.subject = file_safe_name(subject).lower()
        
        if os.path.exists("agents/subject_cache.json"):
            with open("agents/subject_cache.json", "r", encoding="utf-8") as f:
                try:
                    subject_cache = json.load(f) or {}
                except:
                    subject_cache = {}
        else:
            subject_cache = {}
            
        if self.subject not in subject_cache:
            print_yellow(f"Generating system message for {self.subject}...")
            subject_cache[self.subject] = self.send_no_history(
                f"give me the best system message for this base system message: '{base_prompt}' without any titles and responses, only the system message"
            )
            os.makedirs("agents", exist_ok=True)
            with open("agents/subject_cache.json", "w", encoding="utf-8") as f:
                json.dump(subject_cache, f, indent=4, ensure_ascii=False)
        self.set_system_message(subject_cache[self.subject])

    def set_system_message(self, system_message):
        self.system_message = [{"role": "system", "content": system_message}]

    def add_user_message(self, message, reset=False):
        if message:
            if not hasattr(self, 'system_message') or not self.system_message:
                self.set_subject(self.subject)
            self.messages.append({"role": "user", "content": message})
        if reset:
            self.start_count = len(self.messages)

    def chat(self, prompt, complex=False):
        if complex:
            for _ in range(3):
                self.add_user_message(f"Make 5 unique suggestions for the following prompt: '{prompt}'")
                answer = self.send()
                print_orange(f"{self.subject} Suggestion: {answer}")
            self.add_user_message(
                "Get the best ideas from all suggestions based on coolness, quality, and odds of success, and merge them in a final idea. Elaborate the idea and write it without any explanation.")
            return self.send()
        self.add_user_message(prompt)
        return self.send()

    def send(self, model_name=None):
        print_orange(f"{self.subject} Thinking...")
        model_to_use = model_name or self.model
        
        try:
            response = self.client.chat.completions.create(
                model=model_to_use,
                messages=self.system_message + self.messages,
                tools=self.functions if self.functions else None,
                tool_choice="auto" if self.functions else None
            )
            
            message = response.choices[0].message
            answer = message.content or ""
            
            if message.tool_calls:
                self.messages.append(message)
                for tool_call in message.tool_calls:
                    tool_result_str = str(self.parse_function_call(tool_call))
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": tool_result_str
                    })
                return self.send(model_name)
            
            if answer:
                self.messages.append({"role": "assistant", "content": answer})
            return answer

        except Exception as e:
            print_red(f"Error in send for {self.subject}: {e}")
            return f"Error: {e}"

    def send_no_history(self, prompt, model_name=None):
        model_to_use = model_name or self.model
        try:
            response = self.client.chat.completions.create(
                model=model_to_use,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1024
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {e}"

    def fetch_external_info(self, query):
        """Fetches external information for the given query."""
        print_orange(f"Searching for: {query}")
        safe_query = quote_plus(query)
        url = f"https://www.google.com/search?q={safe_query}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            return soup.get_text(separator="\n").strip()[:5000]
        except Exception as e:
            return f"Error: {e}"

    def save_content_to_file(self, content, filepath):
        """Saves content to a file."""
        if not filepath.startswith("root" + os.sep):
            filepath = os.path.join("root", filepath)
        if not content:
            return "No content to save."
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            print_orange(f"Saving content to {filepath}...")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Content saved to {filepath}."
        except Exception as e:
            return f"Error: {e}"

    def close(self):
        if len(self.messages) > self.start_count:
            self.save_conversation()
        print_yellow(f"Agent {self.subject} closed.")

    def save_conversation(self):
        log_folder = "logs"
        filename = file_safe_name(self.subject).lower() if self.subject else "chat_log"
        os.makedirs(log_folder, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_folder, f"{filename}_{timestamp}.json")
        obj = dict(messages=[m if isinstance(m, dict) else m.model_dump() for m in self.messages], timestamp=timestamp)
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=4, ensure_ascii=False)

    def parse_function_call(self, tool_call):
        function_name = tool_call.function.name
        kwargs = json.loads(tool_call.function.arguments)
        if hasattr(self, function_name):
            func = getattr(self, function_name)
            if callable(func):
                try:
                    return func(**kwargs) or "Success."
                except Exception as e:
                    return f"Error: {e}"
        return f"Function `{function_name}` not found."
