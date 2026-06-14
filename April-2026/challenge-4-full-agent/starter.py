import os
os.environ["BYPASS_TOOL_CONSENT"] = "true"
os.environ["MEM0_LLM_PROVIDER"] = "litellm"
os.environ["MEM0_LLM_MODEL"] = "bedrock/amazon.nova-micro-v1:0"

from datetime import date, datetime
import requests
from strands import Agent, tool
from strands.hooks import BeforeToolCallEvent
from strands_tools import calculator, mem0_memory

MODEL = "us.amazon.nova-pro-v1:0"
USER_ID = "user"

@tool
def weather(city: str) -> str:
    """Get the current weather for a city.
    Args:
        city: The name of the city.
    """
    try:
        r = requests.get(f"https://wttr.in/{city}?format=3", timeout=5)
        return r.text
    except:
        return f"Weather in {city}: Sunny, 30°C"

@tool
def age_calculator(birth_date: str) -> str:
    """Calculate age from a birth date.
    Args:
        birth_date: Date of birth in YYYY-MM-DD format.
    """
    today = date.today()
    born = datetime.strptime(birth_date, "%Y-%m-%d").date()
    age = today.year - born.year - (
        (today.month, today.day) < (born.month, born.day)
    )
    return f"Someone born on {birth_date} is {age} years old."

# Streaming callback — prints tokens as they arrive
def stream_handler(**event):
    if "data" in event:
        print(event["data"], end="", flush=True)
    elif "current_tool_use" in event:
        tool_name = event["current_tool_use"].get("name", "")
        if tool_name:
            print(f"\n🔧 Using tool: {tool_name}")

agent = Agent(
    model=MODEL,
    tools=[calculator, weather, age_calculator, mem0_memory],
    callback_handler=stream_handler,
    system_prompt=f"""You are a fun, helpful assistant! 🤖
You have access to: calculator, weather, age_calculator, and memory tools.
- Use calculator for any math
- Use weather to check any city's weather  
- Use age_calculator for birth dates
- Use mem0_memory to remember and recall user info (name, city, preferences, etc.)
- ALWAYS pass user_id="{USER_ID}" on every mem0_memory call
- STORE personal facts as soon as the user shares them
- Before answering questions about the user, RETRIEVE or LIST memories first
Be friendly and use emojis!"""
)

def ensure_memory_user_id(event: BeforeToolCallEvent) -> None:
    if event.tool_use.get("name") == "mem0_memory":
        event.tool_use.setdefault("input", {})["user_id"] = USER_ID

agent.add_hook(ensure_memory_user_id, BeforeToolCallEvent)

print("🤖 Full Agent — Tools + Memory + Streaming")
print("Type 'quit' to exit\n")

while True:
    user_input = input("You: ").strip()
    if user_input.lower() in ["quit", "exit", "q"]:
        print("Bye! 👋")
        break
    if not user_input:
        continue
    print("Agent: ", end="")
    agent(user_input)
    print("\n")

print("\n✅ Challenge 4 complete!")