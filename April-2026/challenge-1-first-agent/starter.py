from strands import Agent
from strands.models.ollama import OllamaModel

ollama_model = OllamaModel(host="http://localhost:11434", model_id="llama3.2:3b") 

agent = Agent(model=ollama_model, tools=[], system_prompt="You are a helpful assistant. Be brief.")  
response = agent("You are a pirate. Answer the following questions:\n1. What is your name?\n2. What is your favorite treasure?\n3. What is your favorite sea creature?")

print("🤖 Agent: ", end="")
print(response)
print("\n✅ Challenge 1 complete!")
