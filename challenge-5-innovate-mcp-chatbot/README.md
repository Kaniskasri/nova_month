# Challenge 5: AI Placement Assistant — MCP Agent

Extends Challenge 4 by connecting to a live **MCP (Model Context Protocol) server** for real AWS documentation data, on top of all existing tools and memory.

## What's New vs Challenge 4

| Feature | Challenge 4 | Challenge 5 |
|---|---|---|
| Local placement tools | ✅ 5 tools | ✅ Same |
| Persistent memory | ✅ JSON file | ✅ Same |
| Streaming | ✅ | ✅ Same |
| MCP server | ❌ | ✅ AWS Docs MCP |
| Real company/AWS docs | ❌ | ✅ Live via MCP |

## Architecture

```
User question
    ↓
Agent decides:
    ├── Eligibility / CGPA / skill gap?  → local tools
    ├── Student profile?                 → recall_memory / store_memory
    └── Real AWS docs / job roles?       → MCP server (live data)
```

## Tools (8 local + MCP)

| Tool | Type |
|---|---|
| `store_memory` | Local — save student profile |
| `recall_memory` | Local — recall profile across sessions |
| `calculator` | Local — arithmetic |
| `eligibility_checker_tool` | Local — company eligibility |
| `cgpa_calculator_tool` | Local — CGPA calculation |
| `placement_stats_tool` | Local — package and roles |
| `company_info_tool` | Local — interview rounds and tips |
| `skill_gap_analyzer_tool` | Local — missing skills + roadmap |
| AWS Documentation tools | MCP — live AWS docs and job data |

## Prerequisites

- Python 3.8+
- AWS account with **Amazon Nova Pro** enabled in Bedrock (us-east-1)
- AWS credentials configured
- **Node.js** (required for MCP server) — [nodejs.org](https://nodejs.org)

## Setup

```bash
# Configure AWS credentials
aws configure

# Install Python dependencies
pip install strands-agents strands-agents-tools faiss-cpu numpy boto3 mcp

# Install Node.js from https://nodejs.org (for MCP server)
```

## Run

```bash
python starter.py
```

The agent will try to connect to the MCP server automatically. If Node.js is not installed, it falls back gracefully to local tools — no crash.

```
✅ MCP connected! 12 extra tools available.   ← with Node.js
🔧 Running with local tools only              ← without Node.js
```

## Sample Interaction

```
You: I am Arjun, CSE, CGPA 7.8, I know Python and SQL, 0 backlogs, B.Tech
Agent: Got it Arjun! Profile saved. 🎓

You: What is the interview process at Amazon and what should I prepare?
Agent: 🌐 [MCP] Fetching real data: aws_documentation_search
       🔧 [Tool] Using: company_info_tool
       🔧 [Tool] Using: skill_gap_analyzer_tool

       Hi Arjun! Amazon has 4 rounds...
       Based on your skills (Python, SQL), you're missing:
         ❌ DSA (LeetCode level)
         ❌ System Design
       Here's your roadmap...
```

Type `quit` to exit.
