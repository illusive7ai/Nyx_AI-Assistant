from .model_client import get_model_client
from .agent import NyxAgent
from .audio_io import speak, listen
from .memory import Memory
from .prompts import NYX_SYSTEM_PROMPT

def run_nyx():
    print("🌙 Nyx AI started. Say 'quit' to exit.\n")

    client = get_model_client()
    memory = Memory()
    agent = NyxAgent(client, memory, NYX_SYSTEM_PROMPT)

    while True:
        # Step 1: Input
        user_text = listen()
        if not user_text:
            continue
        if user_text.lower() in ["quit", "exit", "bye"]:
            speak("Goodbye!")
            break

        # Step 2: Agent reasoning
        response = agent.handle(user_text)

        # Step 3: Output (handled entirely by speak)
        speak(response)
