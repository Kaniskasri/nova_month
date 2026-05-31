"""
Challenge 5: AI Placement Assistant — MCP Agent
Extends Challenge 4 by connecting to an MCP server for real company/career data.

WHAT'S NEW IN CHALLENGE 5 vs CHALLENGE 4:
  - MCPClient connects to awslabs.aws-documentation-mcp-server
  - Agent gets MCP tools alongside all Challenge 4 tools
  - Agent auto-decides: use tool / use memory / use MCP
  - Streaming still works end-to-end

Architecture:
  User question
      ↓
  Agent thinks:
      ├── Need eligibility / CGPA / skill gap?  → use local tools
      ├── Need student profile?                 → recall_memory
      └── Need real company/career docs?        → call MCP server

Prerequisites:
  pip install strands-agents strands-agents-tools faiss-cpu numpy boto3 mcp

  aws configure
    AWS Access Key ID     : <your key>
    AWS Secret Access Key : <your secret>
    Default region name   : us-east-1
    Default output format : json

  Node.js required for MCP server (https://nodejs.org)

Run:
  python challenge_5_mcp_placement_agent.py
"""

import os
import json
import asyncio
from pathlib import Path

os.environ["BYPASS_TOOL_CONSENT"] = "true"

# ============================================================
# TODO 1: Import everything you need
# ============================================================
from strands import Agent, tool
from strands.models.bedrock import BedrockModel
from strands_tools import calculator
from strands.tools.mcp import MCPClient

# ============================================================
# TODO 2: Create streaming callback handler
# ============================================================
def stream_callback(**kwargs):
    if "data" in kwargs:
        print(kwargs["data"], end="", flush=True)
    elif "current_tool_use" in kwargs and kwargs["current_tool_use"].get("name"):
        tool_name = kwargs["current_tool_use"].get("name", "")
        if tool_name.startswith("mcp_") or "search" in tool_name or "read" in tool_name:
            print(f"\n🌐 [MCP] Fetching real data: {tool_name}", flush=True)
        else:
            print(f"\n🔧 [Tool] Using: {tool_name}", flush=True)

# ============================================================
# TODO 3: JSON File Memory (no OpenAI key — same as Challenge 4)
# ============================================================
MEMORY_FILE = "placement_memory.json"

def _load_mem() -> dict:
    if Path(MEMORY_FILE).exists():
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {}

def _save_mem(data: dict):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ============================================================
# TODO 4: Memory Tools (same as Challenge 4)
# ============================================================

@tool
def store_memory(key: str, value: str) -> str:
    """
    Save a piece of student information into persistent memory.
    Call this whenever student shares name, CGPA, branch, skills, backlogs.

    Args:
        key:   What to remember (e.g. name, cgpa, branch, skills, backlogs, degree)
        value: The value to store (e.g. Arjun, 7.8, CSE, Python SQL, 0, B.Tech)

    Returns:
        Confirmation that information is stored
    """
    data = _load_mem()
    data[key.lower()] = value
    _save_mem(data)
    return f"✅ Remembered: {key} = {value}"


@tool
def recall_memory(key: str = "all") -> str:
    """
    Recall stored student information from persistent memory.
    Always call this first to personalise responses.

    Args:
        key: 'all' to get full profile, or specific key like name / cgpa / skills

    Returns:
        Stored information for the requested key
    """
    data = _load_mem()
    if not data:
        return "No profile stored yet. Ask the student to share their details."
    if key == "all":
        lines = ["Student Profile (from memory):"]
        for k, v in data.items():
            lines.append(f"  {k}: {v}")
        return "\n".join(lines)
    val = data.get(key.lower())
    return f"{key}: {val}" if val else f"'{key}' not stored. Keys: {list(data.keys())}"

# ============================================================
# TODO 5: Local Placement Tools (same as Challenge 4)
# ============================================================

@tool
def eligibility_checker_tool(cgpa: float, backlogs: int, degree: str) -> str:
    """
    Check which companies a student is eligible for based on CGPA, backlogs, degree.

    Args:
        cgpa:     Student CGPA (e.g. 7.8)
        backlogs: Number of active backlogs (e.g. 0)
        degree:   Student degree (e.g. B.Tech, B.E, MCA)

    Returns:
        List of eligible and not-eligible companies with reasons
    """
    companies = {
        "TCS":       {"min_cgpa": 6.0, "max_backlogs": 0},
        "Infosys":   {"min_cgpa": 6.5, "max_backlogs": 0},
        "Wipro":     {"min_cgpa": 6.0, "max_backlogs": 0},
        "Cognizant": {"min_cgpa": 6.0, "max_backlogs": 0},
        "Accenture": {"min_cgpa": 6.5, "max_backlogs": 0},
        "HCL":       {"min_cgpa": 6.0, "max_backlogs": 0},
        "Capgemini": {"min_cgpa": 6.0, "max_backlogs": 0},
        "Amazon":    {"min_cgpa": 8.0, "max_backlogs": 0},
    }
    eligible, not_eligible = [], []
    for company, rules in companies.items():
        if cgpa >= rules["min_cgpa"] and backlogs <= rules["max_backlogs"]:
            eligible.append(f"✅ {company}")
        else:
            reasons = []
            if cgpa < rules["min_cgpa"]:
                reasons.append(f"CGPA {cgpa} < {rules['min_cgpa']}")
            if backlogs > rules["max_backlogs"]:
                reasons.append(f"{backlogs} backlog(s)")
            not_eligible.append(f"❌ {company} ({', '.join(reasons)})")

    result  = "=== ELIGIBILITY RESULTS ===\n\n"
    result += "ELIGIBLE:\n"     + "\n".join(eligible)     + "\n\n"
    result += "NOT ELIGIBLE:\n" + "\n".join(not_eligible)
    return result


@tool
def cgpa_calculator_tool(grades: list, credits: list) -> str:
    """
    Calculate CGPA from grades and credits for each subject.

    Args:
        grades:  List of grade points (e.g. [9, 8, 7])
        credits: List of credits      (e.g. [4, 4, 3])

    Returns:
        Calculated CGPA with full breakdown
    """
    if len(grades) != len(credits):
        return "Error: grades and credits lists must have equal length."
    total_points  = sum(g * c for g, c in zip(grades, credits))
    total_credits = sum(credits)
    cgpa = round(total_points / total_credits, 2)

    result = "=== CGPA CALCULATION ===\n"
    for i, (g, c) in enumerate(zip(grades, credits)):
        result += f"  Subject {i+1}: {g} × {c} = {g*c}\n"
    result += f"\nTotal Points  : {total_points}"
    result += f"\nTotal Credits : {total_credits}"
    result += f"\n\n🎓 Your CGPA : {cgpa}"
    if   cgpa >= 8.0: result += "\n💡 Excellent! Eligible for Amazon and top companies."
    elif cgpa >= 6.5: result += "\n💡 Good! Eligible for Infosys, Accenture and more."
    else:             result += "\n💡 Eligible for TCS, Wipro, HCL and Capgemini."
    return result


@tool
def placement_stats_tool(company_name: str) -> str:
    """
    Get placement statistics for a company — average package, top roles.

    Args:
        company_name: Name of company (e.g. TCS, Amazon, Infosys)

    Returns:
        Package and role statistics
    """
    stats = {
        "Tcs":       {"avg": "3.5 LPA",  "highest": "7 LPA",   "roles": ["System Engineer", "ASE"]},
        "Infosys":   {"avg": "3.6 LPA",  "highest": "8 LPA",   "roles": ["Systems Engineer", "Analyst"]},
        "Wipro":     {"avg": "3.5 LPA",  "highest": "6.5 LPA", "roles": ["Project Engineer", "SE"]},
        "Amazon":    {"avg": "26 LPA",   "highest": "45 LPA",  "roles": ["SDE-1", "Data Engineer"]},
        "Accenture": {"avg": "4.5 LPA",  "highest": "9 LPA",   "roles": ["ASE", "Analyst"]},
        "Cognizant": {"avg": "4 LPA",    "highest": "8 LPA",   "roles": ["Programmer Analyst"]},
        "Hcl":       {"avg": "3.5 LPA",  "highest": "6 LPA",   "roles": ["Graduate Engineer Trainee"]},
        "Capgemini": {"avg": "4 LPA",    "highest": "7.5 LPA", "roles": ["Analyst", "Associate Consultant"]},
    }
    company = company_name.strip().title()
    if company not in stats:
        return f"Stats not available for '{company_name}'. Try: TCS, Infosys, Wipro, Amazon, Accenture"
    d = stats[company]
    return (f"=== {company.upper()} PLACEMENT STATS ===\n"
            f"💰 Average Package  : {d['avg']}\n"
            f"🏆 Highest Package  : {d['highest']}\n"
            f"📋 Top Roles        : {', '.join(d['roles'])}")


@tool
def company_info_tool(company_name: str) -> str:
    """
    Get interview rounds, bond period and preparation tips for a company.

    Args:
        company_name: Company name (e.g. TCS, Amazon, Wipro, Infosys)

    Returns:
        Interview process details and preparation tips
    """
    info = {
        "Tcs": {
            "rounds": [
                "1. Online Test (Aptitude + Verbal + Coding)",
                "2. Technical Interview",
                "3. HR Interview"
            ],
            "bond": "2 years service agreement",
            "tips": [
                "Practice TCS NQT pattern seriously",
                "Verbal ability is scored heavily — don't skip it",
                "Know at least one language (Java / C / Python) well",
                "Be confident and clear in HR round"
            ]
        },
        "Infosys": {
            "rounds": [
                "1. Online Assessment (Aptitude + Logical + Verbal + Coding)",
                "2. Technical Interview (OOP, DBMS, OS)",
                "3. HR Interview"
            ],
            "bond": "1 year service agreement",
            "tips": [
                "OOP concepts are must — Inheritance, Polymorphism, Abstraction",
                "Practice SQL queries on HackerRank",
                "Communication skills matter a lot at Infosys",
                "Revise OS and DBMS basics"
            ]
        },
        "Amazon": {
            "rounds": [
                "1. Online Assessment — 2 DSA coding problems (90 min)",
                "2. Technical Round 1 — DSA + Problem Solving",
                "3. Technical Round 2 — System Design",
                "4. Bar Raiser Round — Behavioural + Leadership Principles"
            ],
            "bond": "No bond",
            "tips": [
                "LeetCode Medium and Hard level DSA is mandatory",
                "Study all 16 Amazon Leadership Principles",
                "Use STAR format for all behavioural questions",
                "Practice System Design concepts for SDE-1 level"
            ]
        },
        "Wipro": {
            "rounds": [
                "1. Online Test (Aptitude + English + Coding)",
                "2. Technical Interview",
                "3. HR Interview"
            ],
            "bond": "2 years service agreement",
            "tips": [
                "Wipro Elite NTH track gives higher package — prepare coding well",
                "Core CS subjects: DBMS, OS, Computer Networks",
                "Basic coding in C / C++ / Java / Python",
                "Good communication is key for HR round"
            ]
        },
        "Accenture": {
            "rounds": [
                "1. Cognitive + Technical Assessment",
                "2. Coding Round",
                "3. Communication Assessment",
                "4. HR Interview"
            ],
            "bond": "1 year",
            "tips": [
                "Communication skills are heavily evaluated",
                "Basic OOP and SQL questions in technical",
                "Logical reasoning practice on IndiaBix",
                "Be articulate and confident throughout"
            ]
        },
        "Cognizant": {
            "rounds": [
                "1. GenC / GenC Elevate Online Assessment",
                "2. Technical Interview",
                "3. HR Interview"
            ],
            "bond": "1 year",
            "tips": [
                "Choose GenC Elevate for higher package — needs stronger coding",
                "Java and SQL are most commonly asked",
                "Aptitude and reasoning on IndiaBix",
                "Be clear about your project in technical round"
            ]
        },
    }
    company = company_name.strip().title()
    if company not in info:
        return f"Info not available for '{company_name}'. Try: TCS, Infosys, Amazon, Wipro, Accenture, Cognizant"
    d = info[company]
    result  = f"=== {company.upper()} INTERVIEW PROCESS ===\n\n"
    result += "📋 INTERVIEW ROUNDS:\n"
    result += "\n".join(f"  {r}" for r in d["rounds"]) + "\n\n"
    result += f"📜 BOND: {d['bond']}\n\n"
    result += "💡 PREPARATION TIPS:\n"
    result += "\n".join(f"  • {t}" for t in d["tips"])
    return result


@tool
def skill_gap_analyzer_tool(student_skills: list, target_company: str) -> str:
    """
    Analyse the skill gap between what a student knows and what a company needs.

    Args:
        student_skills: Skills the student has (e.g. ['Python', 'SQL'])
        target_company: Target company (e.g. 'Amazon', 'TCS')

    Returns:
        Missing skills and a personalised learning roadmap
    """
    requirements = {
        "Amazon":    ["DSA", "System Design", "Java or C++", "OS", "DBMS", "Problem Solving"],
        "Tcs":       ["C or Java", "Aptitude", "Verbal Ability", "Basic SQL"],
        "Infosys":   ["OOP", "DBMS", "OS", "SQL", "Java or Python"],
        "Wipro":     ["C or C++", "DBMS", "OS", "Networking Basics"],
        "Accenture": ["Communication", "OOP", "SQL", "Logical Reasoning"],
        "Cognizant": ["Java", "SQL", "Aptitude", "Communication"],
    }
    roadmap = {
        "DSA":             "LeetCode: Easy → Medium → Hard (start with Arrays, Strings, HashMap)",
        "System Design":   "YouTube: Gaurav Sen System Design playlist — start with URL Shortener",
        "Java or C++":     "Pick one language — complete one full course (4–6 weeks)",
        "OOP":             "Master 4 pillars: Encapsulation, Inheritance, Polymorphism, Abstraction",
        "SQL":             "HackerRank SQL section — complete all Easy + Medium problems",
        "OS":              "Gate Smashers OS playlist on YouTube — focus on scheduling + memory",
        "DBMS":            "Gate Smashers DBMS playlist — ER diagrams + normalization + SQL",
        "Aptitude":        "IndiaBix — 30 min daily practice, all sections",
        "Verbal Ability":  "IndiaBix Verbal + GRE Barron's word list",
        "Communication":   "Record yourself answering mock HR questions daily",
        "Logical Reasoning":"IndiaBix Logical Reasoning — puzzles + seating arrangement",
        "Problem Solving": "LeetCode contests weekly to build problem-solving speed",
    }
    company = target_company.strip().title()
    if company not in requirements:
        return f"Requirements not found for '{target_company}'. Try: Amazon, TCS, Infosys, Wipro, Accenture, Cognizant"

    required      = requirements[company]
    student_upper = [s.strip().upper() for s in student_skills]
    have    = [r for r in required if r.upper() in student_upper]
    missing = [r for r in required if r.upper() not in student_upper]

    result  = f"=== SKILL GAP ANALYSIS — {company.upper()} ===\n\n"
    result += "✅ YOU ALREADY HAVE:\n"
    result += ("\n".join(f"  • {s}" for s in have) if have else "  • None matched yet") + "\n\n"
    result += "❌ SKILLS YOU NEED TO BUILD:\n"
    result += ("\n".join(f"  • {s}" for s in missing) if missing else "  • None! You are ready! 🎉") + "\n"
    if missing:
        result += "\n📚 YOUR PERSONALISED LEARNING ROADMAP:\n"
        for skill in missing:
            tip = roadmap.get(skill, "Search for a good online course or YouTube playlist")
            result += f"  • {skill}:\n      → {tip}\n"
        result += f"\n⏱️  Estimated prep time: {len(missing) * 2}–{len(missing) * 3} weeks"
    return result


# ============================================================
# TODO 6: Connect to MCP Server
# ============================================================
# awslabs.aws-documentation-mcp-server runs via npx (Node.js required).
# It gives the agent access to real AWS documentation — useful for
# fetching real job descriptions, role requirements, and career paths.

def create_mcp_client():
    """
    Create MCPClient connected to AWS Documentation MCP server.
    Returns None gracefully if Node.js / npx is not available.
    """
    # Check if npx is available before attempting to connect
    import shutil
    if not shutil.which("npx"):
        print("⚠️  npx not found — Node.js is required for MCP server.")
        print("   Install Node.js from https://nodejs.org and restart.")
        print("   Continuing without MCP — all local tools still work.\n")
        return None

    try:
        from mcp import StdioServerParameters, stdio_client
        server_params = StdioServerParameters(
            command="npx",
            args=["-y", "@awslabs/aws-documentation-mcp-server@latest"],
            env={
                **os.environ,
                "FASTMCP_LOG_LEVEL": "ERROR",   # suppress noisy MCP logs
            }
        )
        client = MCPClient(lambda: stdio_client(server_params))
        return client
    except Exception as e:
        print(f"⚠️  MCP server could not start: {e}")
        print("   Continuing without MCP — all local tools still work.\n")
        return None


# ============================================================
# TODO 7: Build the full MCP Agent
# ============================================================

def build_agent(mcp_tools: list = None):
    """
    Build the Placement Agent combining:
      - All local tools from Challenge 4
      - MCP tools from AWS Documentation server (if available)
      - Nova Pro via Bedrock
      - Streaming via callback_handler
    """
    bedrock_model = BedrockModel(
        model_id="amazon.nova-pro-v1:0",
        region_name="us-east-1"
    )

    local_tools = [
        calculator,
        store_memory,
        recall_memory,
        eligibility_checker_tool,
        cgpa_calculator_tool,
        placement_stats_tool,
        company_info_tool,
        skill_gap_analyzer_tool,
    ]

    all_tools = local_tools + (mcp_tools or [])

    mcp_section = ""
    if mcp_tools:
        mcp_section = f"""
MCP SERVER TOOLS (AWS Docs — {len(mcp_tools)} tools):
  Use these when student asks about:
    • Real AWS job roles and descriptions (SDE, Cloud Engineer, Data Engineer)
    • AWS services used at Amazon / cloud companies
    • Official tech documentation, SDKs, or service details
    • Any question needing verified, live company/tech information
  These fetch LIVE data — prefer them over hardcoded knowledge for
  real company documentation questions.
"""

    system_prompt = f"""You are a complete AI Placement Assistant — smart, memory-powered, and MCP-connected! 🎓

DECISION FRAMEWORK — follow this order for EVERY question:

  Step 1: Call recall_memory(key='all') to check stored student profile.
  Step 2: Pick the right source:

LOCAL TOOLS (instant, offline):
  1. store_memory             — save name, CGPA, branch, skills, backlogs, degree
  2. recall_memory            — recall full student profile
  3. calculator               — any arithmetic
  4. eligibility_checker_tool — eligible companies by CGPA + backlogs + degree
  5. cgpa_calculator_tool     — calculate CGPA from grades and credits
  6. placement_stats_tool     — average package, highest package, top roles
  7. company_info_tool        — interview rounds, bond period, preparation tips
  8. skill_gap_analyzer_tool  — missing skills + learning roadmap
{mcp_section}
STRICT RULES:
  - Student shares name / CGPA / branch / skills → call store_memory immediately for each field
  - Student asks about themselves → call recall_memory(key='all') FIRST
  - Eligibility / CGPA questions → always use the dedicated tools, never guess
  - Company interview process / real docs → use MCP tools first, then local tools
  - Always greet by name if found in memory
  - Stream naturally — be encouraging and mentor-like 🎉

SAMPLE FLOW for "What is the interview process at Amazon and what should I prepare?":
  1. recall_memory('all')                          → get Arjun's skills
  2. MCP: search AWS docs for Amazon SDE role      → real job data
  3. company_info_tool('Amazon')                   → 4 interview rounds
  4. skill_gap_analyzer_tool(['Python','SQL'], 'Amazon') → missing skills
  5. Stream: "Amazon has 4 rounds... Based on your profile Arjun, focus on DSA first..."
"""

    return Agent(
        model=bedrock_model,
        tools=all_tools,
        callback_handler=stream_callback,
        system_prompt=system_prompt,
    )


# ============================================================
# TODO 8: Main — connect MCP, build agent, run chat loop
# ============================================================

def _run_chat_loop(agent: Agent):
    print("\nSample questions:")
    print("  'I am Arjun, CSE, CGPA 7.8, I know Python and SQL, 0 backlogs, B.Tech'")
    print("  'What is the interview process at Amazon and what should I prepare?'")
    print("  'Am I eligible for Infosys?'")
    print("  'What skills am I missing for Amazon?'")
    print("  'Calculate my CGPA: grades [9,8,7,10,8] credits [4,4,3,3,2]'")
    print("  'Who am I?'  ← restart the script, memory still works ✅")
    print("\nType 'quit' to exit.")
    print("-" * 60)

    while True:
        try:
            user_input = input("\nYou: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("quit", "exit", "q", "bye"):
                print("\n🎓 All the best for your placements! You've got this! 🚀")
                break

            print("\nAgent: ", end="")
            agent(user_input)
            print()

        except KeyboardInterrupt:
            print("\n\n🎓 Bye! All the best! 👋")
            break
        except Exception as e:
            print(f"\n⚠️  Error: {e}")
            print("   Try rephrasing your question.\n")

    print("\n✅ Challenge 5 complete! 🏆")


def main():
    print("=" * 60)
    print("🤖 AI Placement Assistant — Challenge 5 (MCP Agent)")
    print("=" * 60)
    print("🔌 Connecting to AWS Documentation MCP server...")

    mcp_client = create_mcp_client()

    if mcp_client:
        try:
            with mcp_client:
                try:
                    mcp_tools = mcp_client.list_tools_sync()
                    print(f"✅ MCP connected! {len(mcp_tools)} extra tools available.\n")
                except Exception as e:
                    print(f"⚠️  MCP connected but tool listing failed: {e}")
                    mcp_tools = []
                agent = build_agent(mcp_tools)
                _run_chat_loop(agent)
        except Exception as e:
            print(f"⚠️  MCP failed to initialize: {e}")
            print("🔧 Falling back to local tools only (all Challenge 4 features intact).\n")
            agent = build_agent()
            _run_chat_loop(agent)
    else:
        print("🔧 Running with local tools only (all Challenge 4 features intact).\n")
        agent = build_agent()
        _run_chat_loop(agent)


if __name__ == "__main__":
    main()