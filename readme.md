# AI Agents Orchestrator

This project is an AI-powered assistant and orchestrator framework that allows you to manage and interact with multiple AI agents, each with their own subject expertise. It leverages OpenAI's API and supports advanced features such as broadcasting messages to all agents, saving conversations, and fetching external information.

## Features

- **Orchestrator Pattern:** Manage multiple AI agents with different subjects and models.
- **Interactive CLI:** Start a chat session, load initial prompts from files, and interact with agents.
- **Function Calling:** Agents can fetch external information and save content to files.
- **Conversation Logging:** All conversations are saved with timestamps for future reference.
- **Customizable System Messages:** Agents generate system prompts tailored to their subject.

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
```

- `main.py`: Entry point for the CLI chat interface.
- `include/agent.py`: Defines the `AIAgent` class and its capabilities.
- `include/orchestrator.py`: Implements the `Orchestrator` class for managing agents.
- `include/colors.py`: Utility functions for colored terminal output.
- `include/helpers.py`: Helper functions (e.g., file-safe naming).
- `agents/`: Stores subject cache for system messages.
- `logs/`: Stores conversation logs.
- `start/`: Contains initial prompt files.

## Getting Started

### Prerequisites

- Python 3.8+
- [OpenAI Python SDK](https://github.com/openai/openai-python)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [colorful](https://pypi.org/project/colorful/)
- An OpenAI API key

### Installation

1. Clone the repository:

    ```sh
    git clone <repo-url>
    cd <repo-directory>
    ```

2. Install dependencies:

    ```sh
    pip install openai python-dotenv colorful requests
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
- Type `exit` or `quit` to end the session.

### Customization

- Add new agents or change their subjects by modifying the orchestrator logic in [`include/orchestrator.py`](include/orchestrator.py).
- Add initial prompts in the `start/` directory.
- Review and analyze conversation logs in the `logs/` directory.

## License

This project is for educational and research purposes.

---

**Author:** Badjano