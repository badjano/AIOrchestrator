from threading import Thread, Lock
from include.agent import AIAgent
from include.colors import *


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
        self.messages = [{"role": "user",
                          "content": "You are not supposed to answer the questions directly, you have to pass on to"
                                     " multiple specialized agents. Your role is to orchestrate the agents and manage"
                                     " their interactions and make sure to have agents from different areas so the"
                                     " project has all the necessary information. Make sure to tell the agents to save"
                                     " the files of the project like scripts, documentation and configs and search the"
                                     " internet when needed by using tools."}]
        self.start_count = len(self.messages)
        self.functions += [
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

    def send_to_agent(self, agent_subject, message):
        agent = self.agents.get(agent_subject)
        if not agent:
            agent = AIAgent(self.model)
            agent.set_subject(agent_subject)
            self.agents[agent_subject] = agent
        if not message:
            print_yellow("No message provided to send to the agent.")
            return "No message provided."

        print_orange(f"Sending message to agent '{agent_subject}': {message}")
        answer = agent.chat(message)
        self.add_user_message(f"Agent '{agent_subject}' response: {answer}")
        return answer

    def broadcast(self, message):
        threads = []
        responses = {}

        def agent_thread(subject, agent):
            agent.add_user_message(message)
            responses[subject] = agent.chat(message)

        print_orange(f"Broadcasting message to all agents: {message}")

        for subject, agent in self.agents.items():
            t = Thread(target=agent_thread, args=(subject, agent))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()  # Wait for all threads to finish

        return responses
