# Challenge 3: AI Placement Assistant — Persistent Memory

Adds persistent memory to the placement assistant using **mem0** + **FAISS**, so the agent remembers your profile even after restarts.

## What's New vs Challenge 2

| | Challenge 2 | Challenge 3 |
|---|---|---|
| Memory | None (stateless) | Persistent via mem0 + FAISS |
| Tools | 4 custom tools | `mem0_memory` from strands-tools |
| Profile recall | Re-enter every session | Remembered across restarts |

## How Memory Works

1. You share your profile (name, CGPA, branch, skills)
2. Agent stores it using `mem0_memory` tool backed by FAISS locally
3. On next session, agent recalls your profile automatically and personalizes responses

## Prerequisites

- Python 3.8+
- AWS account with **Amazon Nova Pro** enabled in Bedrock (us-east-1)
- AWS credentials configured

## Setup

```bash
# Configure AWS credentials
aws configure

# Install dependencies
pip install faiss-cpu mem0ai opensearch-py strands-agents strands-agents-tools
```

## Run

```bash
python starter.py
```

## Try It Out

```
# Session 1
You: Remember that my name is Alex, CGPA 7.8, CSE branch, I know Python and SQL
Agent: Got it Alex! I've saved your profile.

# Quit and restart...

# Session 2
You: Am I eligible for Infosys?
Agent: Hi Alex! Based on your CGPA of 7.8 and CSE background, yes you're eligible for Infosys!
```

Type `quit` to exit.
