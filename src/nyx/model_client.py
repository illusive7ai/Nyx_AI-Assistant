import os
from openai import OpenAI

def get_model_client():
    base = os.getenv("LMSTUDIO_API_BASE", "http://localhost:1234/v1")
    model = os.getenv("LMSTUDIO_MODEL", "qwen")
    client = OpenAI(base_url=base, api_key="lm-studio")  # dummy key
    return {"client": client, "model": model}
