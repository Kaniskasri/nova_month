# Challenge 4: AI Placement Assistant — Full Agent

The complete placement assistant combining **Tools + Memory + Streaming** from all previous challenges into one production-style agent.

## What's Combined

| Feature | Source |
|---|---|
| 4 placement tools | Challenge 2 |
| Persistent memory (FAISS) | Challenge 3 |
| Token-by-token streaming | New in Challenge 4 |
| Skill gap analyzer tool | New in Challenge 4 |

## Tools (6 total)

| Tool | What it does |
|---|---|
| `mem0_memory` | Store and recall student profile across sessions |
| `eligibility_checker_tool` | Check eligible companies by CGPA, backlogs, degree |
| `cgpa_calculator_tool` | Calculate CGPA from grades and credits |
| `placement_stats_tool` | Package, roles, hiring season per company |
| `company_info_tool` | Interview rounds, bond, locations per company |
| `skill_gap_analyzer_tool` | Missing skills + prioritized learning roadmap |

## Prerequisites

- Python 3.8+
- AWS account with **Amazon Nova Pro** enabled in Bedrock (us-east-1)
- AWS credentials configured

## Setup

```bash
# Configure AWS credentials
aws configure

# Install dependencies
pip install faiss-cpu mem0ai opensearch-py strands-agents strands-agents-tools boto3
```

## Run

```bash
python starter.py
```

## Sample Interaction

```
You: My name is Arjun, CGPA 7.8, CSE, I know Python and SQL
Agent: Got it Arjun! I've saved your profile. 🎓

You: What should I learn to get into Amazon?
Agent: Hi Arjun! Based on your profile, here's your skill gap for Amazon:
  ✅ You have: Python, SQL
  ❌ Missing: DSA (LeetCode level), System Design, Java or C++

  🗺️ Learning Roadmap:
  1. DSA (LeetCode Medium/Hard)
  2. System Design
  3. Java or C++
  ...

# Quit and restart — agent still remembers Arjun's profile!
```

Type `exit` to quit.
