"""
Challenge 1: AI Placement Assistant — First Agent
Build a simple Placement Assistant using Strands SDK + Ollama (runs locally!)

Instructions:
  1. Fill in the TODO sections below
  2. Run: python starter.py
  3. Make sure 'ollama serve' is running in another terminal
"""

# TODO 1: Import Agent from strands
from strands import Agent

# TODO 2: Import OllamaModel from strands
from strands.models.ollama import OllamaModel

# TODO 3: Create an OllamaModel instance
# Using host="http://localhost:11434" and model_id="llama3.2:3b"
ollama_model = OllamaModel(
    host="http://localhost:11434",
    model_id="llama3.2:3b"
)

# TODO 4: Create an Agent with the ollama_model
# System prompt makes it act as a Placement Mentor
agent = Agent(
    model=ollama_model,
    tools=[],
    system_prompt="""You are an AI Placement Assistant — a helpful and friendly campus recruitment mentor.

Your job is to help final-year college students with:
- Checking eligibility for companies based on CGPA, degree, and backlogs
- Explaining what skills are required for specific companies
- Giving interview preparation tips
- Suggesting what to study for aptitude and technical rounds

Company eligibility rules you know:
- TCS: CGPA >= 6.0, no active backlogs
- Infosys: CGPA >= 6.5, no active backlogs
- Wipro: CGPA >= 6.0
- Cognizant: CGPA >= 6.0, no active backlogs
- Amazon: CGPA >= 8.0, CS/IT degree, no backlogs
- Accenture: CGPA >= 6.5

Always be encouraging, clear, and mentor-like in your responses.
If a student shares their CGPA and skills, use that to give personalized advice.
Keep responses short, structured, and helpful."""
)

# TODO 5: Start the placement assistant chat loop
print("=" * 50)
print("🎓 AI Placement Assistant")
print("=" * 50)
print("Hello! I am your AI Placement Mentor.")
print("Ask me anything about placements, eligibility, or interview prep.")
print("Type 'exit' to quit.\n")

# Chat loop — keeps the conversation going
while True:
    user_input = input("You: ").strip()

    if user_input.lower() in ["exit", "quit", "bye"]:
        print("🤖 Agent: Good luck with your placements! You've got this! 🚀")
        break

    if not user_input:
        continue

    print("🤖 Agent: ", end="")
    response = agent(user_input)
    print(response)
    print()

print("\n✅ Challenge 1 complete!")