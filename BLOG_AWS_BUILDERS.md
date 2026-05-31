# How I Built an AI Placement Assistant in 5 Challenges Using Amazon Bedrock and Strands SDK

## Introduction

Campus placements are stressful. Students juggle CGPA calculations, company eligibility rules, interview prep, and skill gaps — all at once. I decided to build an AI-powered placement mentor that could handle all of this intelligently.

Over 5 progressive challenges, I built a full-featured AI Placement Assistant using **Amazon Bedrock Nova Pro**, **Strands SDK**, **FAISS**, and **MCP (Model Context Protocol)**. Each challenge added a new capability, and by the end I had a production-style agent that remembers students across sessions, uses tools intelligently, streams responses in real time, and fetches live AWS documentation.

Here's how I built it — step by step.

---

## The Problem

Every year, thousands of final-year engineering students face the same questions:
- "Am I eligible for TCS with a 6.8 CGPA?"
- "What skills do I need for Amazon?"
- "What is my CGPA if I got these grades?"

These questions have clear, structured answers — but students waste hours searching across websites, asking seniors, and second-guessing themselves. A well-designed AI agent can answer all of this instantly, and even remember the student's profile for next time.

---

## Challenge 1: The First Agent

**Tech:** Strands SDK + Ollama (local LLM — llama3.2:3b)

The first challenge was simple: get an agent running locally with zero cloud dependency.

I used **Ollama** to run `llama3.2:3b` on my machine and connected it to a Strands `Agent` with a carefully crafted system prompt containing company eligibility rules.

```python
from strands import Agent
from strands.models.ollama import OllamaModel

ollama_model = OllamaModel(
    host="http://localhost:11434",
    model_id="llama3.2:3b"
)

agent = Agent(
    model=ollama_model,
    tools=[],
    system_prompt="You are an AI Placement Assistant..."
)
```

**What I learned:** A well-written system prompt alone can handle a surprising amount of placement Q&A. But hardcoded knowledge in prompts doesn't scale — you need tools for accuracy.

---

## Challenge 2: Adding Custom Tools

**Tech:** Strands SDK + Amazon Bedrock Nova Pro + 4 custom tools

I switched to **Amazon Bedrock Nova Pro** for a more capable model and added 4 structured tools using the `@tool` decorator from Strands.

### Tools Built

| Tool | Purpose |
|---|---|
| `eligibility_checker_tool` | Checks eligible companies by CGPA, backlogs, degree |
| `cgpa_calculator_tool` | Calculates CGPA from grades and credits |
| `placement_stats_tool` | Returns avg/highest package and top roles |
| `company_info_tool` | Returns interview rounds, bond, and prep tips |

```python
@tool
def eligibility_checker_tool(cgpa: float, backlogs: int, degree: str) -> str:
    """Check which companies a student is eligible for."""
    companies = {
        "TCS":    {"min_cgpa": 6.0, "max_backlogs": 0},
        "Amazon": {"min_cgpa": 8.0, "max_backlogs": 0},
        # ...
    }
    # logic here
```

The agent now automatically decides when to call a tool vs answer directly. Ask "Am I eligible for Infosys?" and it calls `eligibility_checker_tool`. Ask "What is OOP?" and it answers from its own knowledge.

**What I learned:** The `@tool` decorator in Strands makes it trivially easy to give agents structured, reliable capabilities. The agent's tool-use decisions are surprisingly accurate with a clear system prompt.

---

## Challenge 3: Persistent Memory with FAISS

**Tech:** Strands SDK + Bedrock Nova Pro + mem0 + FAISS

The biggest limitation of Challenge 2 was that the agent forgot everything on restart. A student would have to re-introduce themselves every session.

I added **persistent memory** using `mem0` backed by **FAISS** (a local vector store) via `strands_tools`.

```python
from strands_tools import mem0_memory

agent = Agent(
    model=bedrock_model,
    tools=[mem0_memory],
    system_prompt="""...
    MEMORY RULES:
    - When a student shares their profile, ALWAYS store it immediately.
    - Always recall memory at session start to check stored profile.
    - Always greet student by name if remembered.
    """
)
```

Now a student can say "My name is Arjun, CGPA 7.8, CSE, I know Python and SQL" — quit the program — restart — and the agent still knows who Arjun is.

**What I learned:** Memory transforms an agent from a stateless chatbot into a genuine mentor. The combination of FAISS for local vector storage and mem0 for the memory abstraction layer works seamlessly with Strands.

---

## Challenge 4: Full Agent — Tools + Memory + Streaming

**Tech:** Strands SDK + Bedrock Nova Pro + FAISS + 5 tools + streaming

Challenge 4 combined everything and added two new capabilities:

1. **A new tool** — `skill_gap_analyzer_tool` that takes a student's skills and a target company, then returns missing skills with a prioritized learning roadmap.

2. **Streaming** — responses stream token by token instead of waiting for the full response.

```python
def stream_callback(chunk):
    if isinstance(chunk, dict):
        delta = chunk.get("contentBlockDelta", {}).get("delta", {})
        text = delta.get("text", "")
        if text:
            print(text, end="", flush=True)

agent(user_input, callback_handler=stream_callback)
```

### Sample Interaction

```
You: What should I learn to get into Amazon?

Agent: Hi Arjun! Based on your profile (CGPA 7.8, Python + SQL):

  ✅ You have: Python, SQL
  ❌ Missing: DSA (LeetCode level), System Design, Java or C++

  🗺️ Learning Roadmap:
  1. DSA — LeetCode Medium/Hard (Arrays, Strings, HashMap first)
  2. System Design — Gaurav Sen YouTube playlist
  3. Java or C++ — pick one, complete a full course (4–6 weeks)
```

The agent automatically:
- Recalled Arjun's profile from memory
- Called `skill_gap_analyzer_tool` with his skills and target company
- Streamed the response token by token

**What I learned:** The `callback_handler` pattern in Strands is the correct way to stream. The agent's decision-making — when to use memory, when to call a tool, when to answer directly — is handled entirely by the model given a well-structured system prompt.

---

## Challenge 5: MCP Integration — Live AWS Documentation

**Tech:** Strands SDK + Bedrock Nova Pro + FAISS + MCP (AWS Documentation server)

The final challenge introduced **MCP (Model Context Protocol)** — a standard for connecting agents to external data sources and tools at runtime.

I connected the agent to `@awslabs/aws-documentation-mcp-server`, which gives the agent access to live AWS documentation. This means the agent can now fetch real job descriptions, AWS service details, and career path information on demand.

```python
from strands.tools.mcp import MCPClient
from mcp import StdioServerParameters, stdio_client

server_params = StdioServerParameters(
    command="npx",
    args=["-y", "@awslabs/aws-documentation-mcp-server@latest"],
    env={**os.environ, "FASTMCP_LOG_LEVEL": "ERROR"}
)

mcp_client = MCPClient(lambda: stdio_client(server_params))

with mcp_client:
    mcp_tools = mcp_client.list_tools_sync()
    agent = build_agent(mcp_tools)  # local tools + MCP tools combined
```

### Decision Framework

The agent now has three layers of intelligence:

```
User question
    ↓
Agent decides:
    ├── Eligibility / CGPA / skill gap?  → local tools (instant)
    ├── Student profile?                 → memory tools
    └── Real AWS docs / job roles?       → MCP server (live data)
```

I also added a graceful fallback — if Node.js isn't installed, the agent detects this upfront and runs with local tools only, no crash.

**What I learned:** MCP is a powerful pattern for giving agents access to live, authoritative data without hardcoding it. The Strands SDK makes combining local tools and MCP tools seamless — the agent treats them identically.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│              AI Placement Assistant              │
│                  (Challenge 5)                   │
├─────────────────────────────────────────────────┤
│  Model: Amazon Bedrock Nova Pro (us-east-1)      │
├──────────────────────┬──────────────────────────┤
│   Local Tools        │   MCP Tools              │
│  ─────────────────   │  ──────────────────────  │
│  eligibility_checker │  AWS Documentation       │
│  cgpa_calculator     │  (live job data,         │
│  placement_stats     │   service docs,          │
│  company_info        │   career paths)          │
│  skill_gap_analyzer  │                          │
│  store_memory        │                          │
│  recall_memory       │                          │
├──────────────────────┴──────────────────────────┤
│  Memory: FAISS (local vector store via mem0)     │
│  Streaming: callback_handler (token by token)    │
└─────────────────────────────────────────────────┘
```

---

## Key Takeaways

**1. Strands SDK makes agent development fast.** The `@tool` decorator, `Agent` class, and `callback_handler` pattern cover 90% of what you need to build a production agent.

**2. Amazon Bedrock Nova Pro is excellent for agentic tasks.** Its tool-use accuracy and instruction-following made the agent's decision-making reliable without complex prompt engineering.

**3. Memory changes everything.** Adding FAISS-backed persistence transformed the agent from a stateless Q&A bot into a genuine mentor that builds context over time.

**4. MCP is the right abstraction for live data.** Rather than hardcoding company data or calling APIs manually, MCP lets the agent fetch authoritative information on demand through a standard protocol.

**5. Build incrementally.** Each challenge added exactly one new capability. This made debugging easy and the architecture clean.

---

## What's Next

- Add a web UI with Streamlit or Gradio
- Connect to real placement portals via MCP
- Add multi-student support with user IDs
- Deploy on AWS Lambda for serverless access

---

## Resources

- [Strands SDK](https://github.com/strands-agents/sdk-python)
- [Amazon Bedrock Nova Pro](https://aws.amazon.com/bedrock/)
- [mem0 Memory Library](https://github.com/mem0ai/mem0)
- [MCP Protocol](https://modelcontextprotocol.io)
- [AWS Documentation MCP Server](https://github.com/awslabs/mcp)

---

*Built as part of the Nova Month challenge series. All code is available on GitHub.*
