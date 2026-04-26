from threading import Thread, Lock
import json
import os
from include.agent import AIAgent
from include.colors import *

class Orchestrator(AIAgent):
    _instance = None
    _lock = Lock()

    @classmethod
    def get_instance(cls, model=None):
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls(model)
        return cls._instance

    def __init__(self, model=None):
        super().__init__(model)
        self.set_subject("AI Agents Orchestrator")
        self.system_message = [{"role": "system", "content": 
            "You are the Lead Orchestrator. Your role is to solve complex tasks by delegating them to specialized agents. "
            "You have access to a pool of agents with different specialties. "
            "When a task is complex, break it down and use 'send_to_agent' to get help. "
            "Always synthesize the agents' responses into a final, coherent answer for the user."}]
        
        self.functions += [
            {
                "type": "function",
                "function": {
                    "name": "send_to_agent",
                    "description": "Delegates a task to a specialized agent.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "agent_type": {"type": "string", "description": "The type of agent (e.g., researcher, coder, reviewer)"},
                            "message": {"type": "string", "description": "The specific task or question for the agent"}
                        },
                        "required": ["agent_type", "message"]
                    }
                }
            }
        ]
        self.agents = {}
        self.config_path = "jsons/agent_config.json"
        self.load_config()

    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.agent_config = json.load(f)
        else:
            self.agent_config = {}
            print_red(f"Config file not found at {self.config_path}")

    def send_to_agent(self, agent_type, message):
        # Normalize agent_type
        agent_type = agent_type.lower()
        
        if agent_type not in self.agents:
            # Check if we have a profile for this type
            profile = self.agent_config.get(agent_type)
            if profile:
                print_yellow(f"Creating specialized agent: {profile['subject']}")
                agent = AIAgent(
                    model=profile.get("model"),
                    tools_whitelist=profile.get("tools"),
                    system_message=profile.get("backstory")
                )
                agent.subject = profile.get("subject")
                self.agents[agent_type] = agent
            else:
                # Fallback to generic agent
                print_yellow(f"No profile found for '{agent_type}', creating generic agent.")
                agent = AIAgent(self.model)
                agent.set_subject(agent_type)
                self.agents[agent_type] = agent

        agent = self.agents[agent_type]
        print_orange(f"Delegating to {agent.subject}...")
        answer = agent.chat(message)
        
        # Add to orchestrator memory
        self.add_user_message(f"Update from {agent.subject}: {answer}")
        return answer

    def broadcast(self, message):
        threads = []
        responses = {}

        def agent_thread(agent_id, agent_obj):
            responses[agent_id] = agent_obj.chat(message)

        print_orange(f"Broadcasting to all active agents...")
        for agent_id, agent_obj in self.agents.items():
            t = Thread(target=agent_thread, args=(agent_id, agent_obj))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        return responses

    def close(self):
        for agent in self.agents.values():
            agent.close()
        super().close()
