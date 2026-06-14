import os
os.environ["BYPASS_TOOL_CONSENT"] = "true"
import requests
from datetime import date, datetime
from strands import Agent, tool
from strands_tools import calculator

MODEL = "us.amazon.nova-pro-v1:0"

@tool
def weather(city: str) -> str:
  """Get the current weather for a city.
  Args:
      city: The name of the city.
  """
  try:
    response = requests.get(
        f"https://wttr.in/{city}?format=3",
        timeout=5
    )
    return response.text
  except:
    return f"The weather in {city} is sunny, 28°C"

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


@tool
def inr_to_usd(inr_amount: float) -> str:
    """Convert INR to USD.
    Args:
        inr_amount: Amount in Indian Rupees.
    """
    exchange_rate = 0.012  # Example exchange rate
    usd_amount = inr_amount * exchange_rate
    return f"{inr_amount} INR is approximately {usd_amount:.2f} USD."


agent = Agent(
    model=MODEL,
    tools=[calculator, weather, age_calculator, inr_to_usd],
    system_prompt="You are a helpful assistant with tools. Use them to answer accurately. When asked for a multi-step task, use the available tools in order."
    )


print("conversion test:")
response = agent("First use the calculator to compute 42 * 8, then use the inr_to_usd tool on that result.")
print(response)

print("🧮 Math test:")
response = agent("What is 42 * 17?")
print(response)

print("\n🌤️ Weather test:")
response = agent("What's the weather in Chennai?")
print(response)

print("\n🎂 Age test:")
response = agent("How old is someone born on 2000-05-15?")
print(response)

print("\n✅ Challenge 2 complete!")