

try:
    from google.adk.agents import Agent, LlmAgent
    print(f"Agent has run: {hasattr(Agent, 'run')}")
    print(f"LlmAgent has run: {hasattr(LlmAgent, 'run')}")
    
    # Check if Agent is a superclass of LlmAgent
    print(f"LlmAgent inherits from Agent: {issubclass(LlmAgent, Agent)}")
except ImportError as e:
    print(f"ImportError: {e}")

