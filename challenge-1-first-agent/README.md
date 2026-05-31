# Challenge 1: AI Placement Assistant — First Agent

A simple AI-powered campus placement mentor built with **Strands SDK** and **Ollama** running locally.

## What It Does

Chat with an AI mentor that helps college students with:
- Checking company eligibility based on CGPA and backlogs
- Interview preparation tips
- Skills required for specific companies
- Aptitude and technical round guidance

## Prerequisites

- Python 3.8+
- [Ollama](https://ollama.com) installed and running
- `llama3.2:3b` model pulled

## Setup

```bash
# Pull the model
ollama pull llama3.2:3b

# Install dependencies
pip install strands-agents
```

## Run

```bash
# Terminal 1 — start Ollama
ollama serve

# Terminal 2 — run the agent
python starter.py
```

## Company Eligibility Rules

| Company | Min CGPA | Requirements |
|---|---|---|
| TCS | 6.0 | No active backlogs |
| Infosys | 6.5 | No active backlogs |
| Wipro | 6.0 | — |
| Cognizant | 6.0 | No active backlogs |
| Amazon | 8.0 | CS/IT degree, no backlogs |
| Accenture | 6.5 | — |

## Usage

```
You: I have 7.5 CGPA, CSE degree, no backlogs. Which companies can I apply to?
🤖 Agent: You're eligible for TCS, Infosys, Wipro, Cognizant, and Accenture...
```

Type `exit` to quit.
