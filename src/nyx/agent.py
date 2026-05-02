# src/nyx/agent.py
import re
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from .model_client import get_model_client
from .prompts import NYX_SYSTEM_PROMPT
from ..tools import time, calc, wifipasswords, program_manager, wifi_cracker
from ..tools import handle_crack_wifi 


class NyxAgent:
    """
    Nyx Agent:
    - Uses memory
    - Simple tool detection (time/calc/wifi)
    - Falls back to raw LLM
    """
    def __init__(self, model_client, memory, system_prompt=NYX_SYSTEM_PROMPT):
        self.client = model_client["client"]
        self.model = model_client["model"]
        self.memory = memory
        self.system_prompt = system_prompt
        self.tools = {
            "time": time.get_time,
            "calc": calc.calculate,
            "wifipasswords": wifipasswords.show_wifi_passwords,
            "program_manager": program_manager.handle,
            "crack_wifi": wifi_cracker.handle_crack_wifi,
        }

    def handle(self, user_text: str) -> str:
        # Save input to memory
        self.memory.add("user", user_text)

        # --- Tool usage (pattern-based) ---
        user_lower = user_text.lower()
        if "time" in user_lower:
            result = self.tools["time"]()
            self.memory.add("assistant", result)
            return result
        
        # 2) Program manager commands - natural language detection
        # list programs: "list programs", "show apps", "what programs are installed"
        if re.search(r'\b(list|show|what)\b.*\b(programs|apps|applications)\b', user_lower):
            result = program_manager.handle("list", None)
            self.memory.add("assistant", result)
            return result
        
        # open/start/launch/run program: "open chrome", "start notepad"
        m_open = re.search(r'\b(open|start|launch|run)\b\s+(?P<target>.+)', user_text, flags=re.IGNORECASE)
        if m_open:
            target = m_open.group("target").strip()
            # remove polite suffixes
            target = re.sub(r'\bfor me\b|\bplease\b', '', target, flags=re.IGNORECASE).strip()
            result = program_manager.handle("open", target)
            self.memory.add("assistant", result)
            return result

        # close/kill/terminate program: "close chrome", "kill firefox"
        m_close = re.search(r'\b(close|kill|terminate|stop|quit)\b\s+(?P<target>.+)', user_text, flags=re.IGNORECASE)
        if m_close:
            target = m_close.group("target").strip()
            target = re.sub(r'\bfor me\b|\bplease\b', '', target, flags=re.IGNORECASE).strip()
            result = program_manager.handle("close", target)
            self.memory.add("assistant", result)
            return result

        if "calc" in user_lower:
            expression = user_text.replace("calc", "").strip()
            result = self.tools["calc"](expression)
            self.memory.add("assistant", result)
            return result

        if "wifipasswords" in user_lower or "wi-fi password" in user_lower:
            result = self.tools["wifipasswords"]()
            self.memory.add("assistant", result)
            return result
        
        # WiFi Cracking command - ADD THIS NEW CHECK (put it first for priority)
        if user_lower.startswith("crack wifi"):
            result = self.tools["crack_wifi"](user_text)
            self.memory.add("assistant", result)
            return result

        # --- Default: call LLM directly ---
        messages = self.memory.to_messages(self.system_prompt)
        messages.append({"role": "user", "content": user_text})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7
        )

        # Access the content properly from ChatCompletionMessage
        try:
            reply = response.choices[0].message.content
        except AttributeError:
            # fallback for older OpenAI client versions
            reply = response.choices[0].message["content"]

        # Save reply in memory
        self.memory.add("assistant", reply)
        return reply


# -----------------------------
# LangChain Agent (tool-calling)
# -----------------------------

def build_agent(tools):
    """Builds a LangChain tool-calling agent."""
    llm = get_model_client()

    prompt = ChatPromptTemplate.from_messages([
        ("system", NYX_SYSTEM_PROMPT),
        ("user", "{input}")
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    return executor


async def run_agent(query: str, tools):
    """
    Runs LangChain agent with tools.
    Falls back to raw LLM if tools are not relevant.
    """
    agent = build_agent(tools)

    try:
        result = await agent.ainvoke({"input": query})

        if "output" in result and result["output"].strip():
            return result["output"]

    except Exception as e:
        print(f"[Agent Error] {e}")

    # 🔥 Fallback → direct LLM response
    llm = get_model_client()
    response = await llm.ainvoke(query)
    return response.content
