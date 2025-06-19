from threading import Thread, Lock
from include.agent import AIAgent
from include.colors import print_yellow, print_blue


class Orchestrator(AIAgent):

    @classmethod
    def get_instance(cls, model="o4-mini"):
        """Returns the current orchestrator instance."""
        if not hasattr(cls, "_current_orchestrator"):
            cls._current_orchestrator = cls(model)
        return cls._current_orchestrator

    def __init__(self, model="o4-mini"):
        super().__init__(model)
        self.set_subject("AI Agents Orchestrator")
        self.functions += [
            {
                "type": "function",
                "function": {
                    "name": "add_agent",
                    "description": "Adds a new AI agent with a specific subject.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "subject": {"type": "string", "description": "The subject for the new agent"},
                            "model": {"type": "string", "description": "The model to use for the agent",
                                      "default": "o4-mini"}
                        },
                        "required": ["subject"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "send_to_agent",
                    "description": "Sends a message to a specific agent.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "agent_subject": {"type": "string",
                                              "description": "The subject of the agent to send the message to"},
                            "message": {"type": "string", "description": "The message to send"}
                        },
                        "required": ["agent_subject", "message"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "broadcast",
                    "description": "Broadcasts a message to all agents.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "message": {"type": "string", "description": "The message to broadcast"}
                        },
                        "required": ["message"]
                    }
                }
            }
        ]
        self.agents = {}

    def add_agent(self, subject, model="o4-mini"):
        if subject:
            print_blue(f"Adding agent with subject: {subject} and model: {model}")
            agent = AIAgent(model)
            agent.set_subject(subject)
            self.agents[subject] = agent

    def send_to_agent(self, agent_subject, message):
        agent = self.agents.get(agent_subject)
        if not agent:
            return f"No agent found with subject: {agent_subject}"

        print_blue(f"Sending message to agent '{agent_subject}': {message}")
        agent.add_user_message(message)
        return agent.chat(message)

    def broadcast(self, message):
        threads = []
        responses = {}

        def agent_thread(subject, agent):
            agent.add_user_message(message)
            responses[subject] = agent.chat(message)

        print_blue(f"Broadcasting message to all agents: {message}")

        for subject, agent in self.agents.items():
            t = Thread(target=agent_thread, args=(subject, agent))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()  # Wait for all threads to finish

        return responses
