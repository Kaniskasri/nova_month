# Challenge 2: AI Placement Assistant — Custom Tools

Extends the placement assistant with 4 custom tools, powered by **Amazon Bedrock Nova Pro** via the Strands SDK.

## What's New vs Challenge 1

| | Challenge 1 | Challenge 2 |
|---|---|---|
| Model | Ollama (local) | Amazon Bedrock Nova Pro |
| Tools | None | 4 custom tools |

## Tools

| Tool | What it does |
|---|---|
| `eligibility_checker_tool` | Checks eligible companies based on CGPA, backlogs, and degree |
| `cgpa_calculator_tool` | Calculates CGPA from grades and credits per subject |
| `placement_stats_tool` | Returns avg/highest package, roles, and hiring season for a company |
| `company_info_tool` | Returns interview rounds, work locations, bond, and prep tips |

## Prerequisites

- Python 3.8+
- AWS account with **Amazon Nova Pro** enabled in Bedrock (us-east-1)
- AWS credentials configured

## Setup

```bash
# Configure AWS credentials
aws configure

# Install dependencies
pip install strands-agents boto3
```

## Run

```bash
python starter.py
```

## Example Queries

```
You: I have 7.8 CGPA, B.Tech degree, 0 backlogs. Am I eligible?
You: Calculate my CGPA — grades [9,8,7,10] credits [4,4,3,3]
You: What are Amazon's placement stats?
You: Tell me about the Infosys interview process
```

Type `exit` to quit.
