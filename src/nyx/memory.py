import json
from pathlib import Path

class Memory:
    def __init__(self, file="nyx_memory.json"):
        self.file = Path(file)
        if self.file.exists():
            self.data = json.loads(self.file.read_text())
        else:
            self.data = []

    def add(self, role: str, content: str):
        self.data.append({"role": role, "content": content})
        self.file.write_text(json.dumps(self.data, indent=2))

    def to_messages(self, system_prompt: str):
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(self.data[-10:])  # keep recent 10 exchanges
        return messages
