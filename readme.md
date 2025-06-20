# AI Agents Orchestrator

This project is an AI-powered multi-agent orchestration framework. It enables you to manage and interact with multiple specialized AI agents, each with their own subject expertise, using OpenAI's API. The system supports advanced features such as agent orchestration, broadcasting, function calling, conversation logging, colored CLI, and flexible prompt loading.

## Features

- **Multi-Agent Orchestration:** Manage and coordinate multiple AI agents, each with a unique subject and system prompt.
- **Interactive CLI:** Start chat sessions, load previous conversations or initial prompts from files, and interact with agents in real time.
- **Function Calling:** Agents can fetch external information (web search) and save content to files using OpenAI tool calls.
- **Broadcasting:** Send messages to all agents in parallel and collect their responses.
- **Conversation Logging:** All conversations are saved with timestamps for future reference.
- **Customizable System Messages:** Agents generate system prompts tailored to their subject, with caching for efficiency.
- **Colored Terminal Output:** User prompts and agent responses are color-coded for clarity.
- **Extensible Agent Roles:** Easily add new agent types or change their behavior via [`include/orchestrator.py`](include/orchestrator.py) and [`agents/subject_cache.json`](agents/subject_cache.json).
- **Safe File Naming:** Helper utilities ensure file paths are safe and consistent.

## Project Structure

```
main.py
include/
    agent.py
    colors.py
    helpers.py
    orchestrator.py
agents/
    subject_cache.json
jsons/
logs/
start/
requirements.txt
readme.md
```

- [`main.py`](main.py): Entry point for the CLI chat interface and orchestrator startup.
- [`include/agent.py`](include/agent.py): Defines the `AIAgent` class, function calling, web search, and file saving.
- [`include/orchestrator.py`](include/orchestrator.py): Implements the `Orchestrator` class for managing and broadcasting to agents.
- [`include/colors.py`](include/colors.py): Utility functions for colored terminal output and colored input prompts.
- [`include/helpers.py`](include/helpers.py): Helper functions (e.g., file-safe naming).
- [`agents/subject_cache.json`](agents/subject_cache.json): Stores system prompts for agent subjects.
- `logs/`: Stores conversation logs in JSON format.
- `start/`: Contains initial prompt files for starting new sessions.
- `jsons/`: (Reserved for additional data/configuration files.)

## Getting Started

### Prerequisites

- Python 3.8+
- [OpenAI Python SDK](https://github.com/openai/openai-python)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [colorful](https://pypi.org/project/colorful/)
- [requests](https://pypi.org/project/requests/)
- [beautifulsoup4](https://pypi.org/project/beautifulsoup4/)
- An OpenAI API key

### Installation

1. Clone the repository:

    ```sh
    git clone <repo-url>
    cd <repo-directory>
    ```

2. Install dependencies:

    ```sh
    pip install -r requirements.txt
    ```

3. Set your OpenAI API key in a `.env` file:

    ```
    OPENAI_API_KEY=your_openai_api_key_here
    ```

### Usage

Run the main script:

```sh
python main.py
```

- You will be prompted to select an initial prompt file or start a new chat.
- Type your messages to interact with the AI assistant.
- Type `exit` or `quit` (or send an empty message) to end the session.

### Customization

- Add or modify agent roles and system prompts in [`agents/subject_cache.json`](agents/subject_cache.json).
- Add initial prompts in the [`start/`](start/) directory.
- Review and analyze conversation logs in the [`logs/`](logs/) directory.
- Extend agent logic or orchestration in [`include/orchestrator.py`](include/orchestrator.py).

## License

This project is for educational and research purposes.

---

**Author:** Badjano