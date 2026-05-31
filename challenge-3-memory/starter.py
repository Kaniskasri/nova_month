"""
Challenge 3: AI Placement Assistant — Persistent Memory
Give your placement assistant memory that survives restarts using FAISS.
Model: Amazon Nova Pro via Bedrock

Instructions:
  1. pip install faiss-cpu mem0ai opensearch-py strands-agents strands-agents-tools
  2. Run: python starter.py
  3. Tell the agent your profile, quit, restart — agent will still remember you!
"""

import os
os.environ["BYPASS_TOOL_CONSENT"] = "true"

# TODO 1: Import Agent and BedrockModel
from strands import Agent
from strands.models.bedrock import BedrockModel

# TODO 2: Import mem0_memory from strands_tools
from strands_tools import mem0_memory

# TODO 3: Create BedrockModel with explicit region
bedrock_model = BedrockModel(
    model_id="amazon.nova-pro-v1:0",
    region_name="us-east-1"
)

# TODO 4: Create agent with mem0_memory tool
agent = Agent(
    model=bedrock_model,
    tools=[mem0_memory],
    system_prompt="""You are an AI Placement Assistant with persistent memory.

You help college students prepare for campus placements.

MEMORY RULES:
- When a student shares their profile (name, CGPA, branch, skills),
  ALWAYS store it using your memory tool immediately.
- Always recall memory at start to check stored profile.
- Always personalize responses using remembered profile.

PLACEMENT KNOWLEDGE:
- TCS      : CGPA >= 6.0, no backlogs
- Infosys  : CGPA >= 6.5, no backlogs
- Wipro    : CGPA >= 6.0, no backlogs
- Amazon   : CGPA >= 8.0, CS/IT degree, no backlogs
- Accenture: CGPA >= 6.5, no backlogs
- Cognizant: CGPA >= 6.0, no backlogs

Always greet student by name if remembered.
Be encouraging and mentor-like in every response."""
)

# TODO 5: Interactive chat loop
print("=" * 50)
print("🧠 Placement Memory Agent Ready!")
print("=" * 50)
print("Try: 'Remember that my name is kaniska, CGPA 7.8, CSE branch, I know Python and SQL'")
print("Then: 'Am I eligible for Infosys?'")
print("Quit and restart — agent will still remember your profile!")
print("Type 'quit' to exit.\n")

while True:
    try:
        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "q"):
            print("Agent: Good luck with your placements! See you next time! 🚀")
            break

        # TODO: Send user_input to the agent and print the response
        response = agent(user_input)
        print(f"Agent: {response}\n")

    except KeyboardInterrupt:
        print("\nAgent: Bye! All the best! 👋")
        break

print("\n✅ Challenge 3 complete!")