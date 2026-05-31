"""
Challenge 4: AI Placement Assistant — Full Agent (Tools + Memory + Streaming)
Combine everything into one powerful placement assistant.
Model: Amazon Nova Pro via Bedrock

Instructions:
  1. pip install faiss-cpu mem0ai opensearch-py strands-agents strands-agents-tools boto3
  2. Fill in ALL the TODO sections
  3. Run: python starter.py
  4. Have a full conversation using all tools + memory + streaming!
"""

import os
os.environ["BYPASS_TOOL_CONSENT"] = "true"

# ============================================================
# TODO 1: Import everything you need
# ============================================================
# Hint: You need Agent, tool from strands
#       mem0_memory from strands_tools
#       BedrockModel from strands.models.bedrock
from strands import Agent, tool
from strands.models.bedrock import BedrockModel
from strands_tools import mem0_memory

# ============================================================
# TODO 2: Create a streaming callback handler
# ============================================================
# This function gets called for every chunk of text the agent generates
# Hint:
# def stream_callback(**kwargs):
#     if "data" in kwargs:
#         print(kwargs["data"], end="", flush=True)
#     elif "current_tool_use" in kwargs and kwargs["current_tool_use"].get("name"):
#         print(f"\n🔧 Using tool: {kwargs['current_tool_use']['name']}")

def stream_callback(**kwargs):
    if "data" in kwargs:
        print(kwargs["data"], end="", flush=True)
    elif "current_tool_use" in kwargs and kwargs["current_tool_use"].get("name"):
        print(f"\n🔧 Using tool: {kwargs['current_tool_use']['name']}")

# ============================================================
# TODO 3: Create all 5 custom placement tools
# ============================================================
# Reuse your tools from Challenge 2 + add skill_gap_analyzer_tool!

@tool
def eligibility_checker_tool(cgpa: float, backlogs: int, degree: str) -> str:
    """
    Check which companies a student is eligible for
    based on their CGPA, number of backlogs, and degree.

    Args:
        cgpa: Student CGPA (e.g. 7.8)
        backlogs: Number of active backlogs (e.g. 0)
        degree: Student degree (e.g. B.Tech, B.E, MCA)

    Returns:
        List of eligible and not eligible companies with reasons
    """
    companies = {
        "TCS":        {"min_cgpa": 6.0, "max_backlogs": 0},
        "Infosys":    {"min_cgpa": 6.5, "max_backlogs": 0},
        "Wipro":      {"min_cgpa": 6.0, "max_backlogs": 0},
        "Cognizant":  {"min_cgpa": 6.0, "max_backlogs": 0},
        "Accenture":  {"min_cgpa": 6.5, "max_backlogs": 0},
        "HCL":        {"min_cgpa": 6.0, "max_backlogs": 0},
        "Capgemini":  {"min_cgpa": 6.0, "max_backlogs": 0},
        "Amazon":     {"min_cgpa": 8.0, "max_backlogs": 0},
    }

    eligible = []
    not_eligible = []

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
    result += "ELIGIBLE:\n" + "\n".join(eligible) + "\n\n"
    result += "NOT ELIGIBLE:\n" + "\n".join(not_eligible)
    return result


@tool
def cgpa_calculator_tool(grades: list, credits: list) -> str:
    """
    Calculate CGPA from grades and credits for each subject.

    Args:
        grades: List of grade points for each subject (e.g. [9, 8, 7])
        credits: List of credits for each subject (e.g. [4, 4, 3])

    Returns:
        Calculated CGPA value with breakdown
    """
    if len(grades) != len(credits):
        return "Error: grades and credits count must match"

    total_points  = sum(g * c for g, c in zip(grades, credits))
    total_credits = sum(credits)
    cgpa = round(total_points / total_credits, 2)

    result  = "=== CGPA CALCULATION ===\n"
    for i, (g, c) in enumerate(zip(grades, credits)):
        result += f"Subject {i+1}: {g} x {c} = {g*c}\n"
    result += f"\nTotal Points : {total_points}"
    result += f"\nTotal Credits: {total_credits}"
    result += f"\n\n🎓 Your CGPA: {cgpa}"

    if cgpa >= 8.0:
        result += "\n💡 Excellent! Eligible for Amazon and top companies."
    elif cgpa >= 6.5:
        result += "\n💡 Good! Eligible for Infosys, Accenture and more."
    else:
        result += "\n💡 Eligible for TCS, Wipro, HCL and Capgemini."
    return result


@tool
def placement_stats_tool(company_name: str) -> str:
    """
    Get placement statistics for a company including package and roles.

    Args:
        company_name: Name of the company (e.g. TCS, Amazon, Infosys)

    Returns:
        Placement stats including average package and top roles
    """
    stats = {
        "Tcs":      {"avg": "3.5 LPA", "highest": "7 LPA",  "roles": ["System Engineer", "ASE"]},
        "Infosys":  {"avg": "3.6 LPA", "highest": "8 LPA",  "roles": ["Systems Engineer", "Analyst"]},
        "Wipro":    {"avg": "3.5 LPA", "highest": "6.5 LPA","roles": ["Project Engineer", "SE"]},
        "Amazon":   {"avg": "26 LPA",  "highest": "45 LPA", "roles": ["SDE-1", "Data Engineer"]},
        "Accenture":{"avg": "4.5 LPA", "highest": "9 LPA",  "roles": ["ASE", "Analyst"]},
    }

    company = company_name.strip().title()
    if company not in stats:
        return f"Stats not available for {company_name}. Try: TCS, Infosys, Wipro, Amazon, Accenture"

    d = stats[company]
    result  = f"=== {company.upper()} STATS ===\n"
    result += f"💰 Average Package : {d['avg']}\n"
    result += f"🏆 Highest Package : {d['highest']}\n"
    result += f"📋 Top Roles       : {', '.join(d['roles'])}"
    return result


@tool
def company_info_tool(company_name: str) -> str:
    """
    Get interview rounds, bond details and preparation tips for a company.

    Args:
        company_name: Name of the company (e.g. TCS, Amazon, Wipro)

    Returns:
        Interview process and preparation tips
    """
    info = {
        "Tcs": {
            "rounds": ["1. Online Test (Aptitude + Coding)", "2. Technical Interview", "3. HR Interview"],
            "bond": "2 years",
            "tips": ["Focus on TCS NQT pattern", "Practice verbal ability", "Know one language well"]
        },
        "Infosys": {
            "rounds": ["1. Online Assessment", "2. Technical Interview (OOP, DBMS)", "3. HR Interview"],
            "bond": "1 year",
            "tips": ["Strong OOP concepts", "Practice SQL", "Good communication skills"]
        },
        "Amazon": {
            "rounds": ["1. OA (2 DSA problems)", "2. Technical Round 1", "3. System Design", "4. Bar Raiser"],
            "bond": "No bond",
            "tips": ["LeetCode Medium/Hard DSA", "Learn 16 Leadership Principles", "STAR format answers"]
        },
        "Wipro": {
            "rounds": ["1. Online Test", "2. Technical Interview", "3. HR Interview"],
            "bond": "2 years",
            "tips": ["Core CS subjects", "Basic coding", "Good communication"]
        },
    }

    company = company_name.strip().title()
    if company not in info:
        return f"Info not available for {company_name}. Try: TCS, Infosys, Amazon, Wipro"

    d = info[company]
    result  = f"=== {company.upper()} INTERVIEW PROCESS ===\n\n"
    result += "📋 ROUNDS:\n" + "\n".join(d["rounds"]) + "\n\n"
    result += f"📜 BOND: {d['bond']}\n\n"
    result += "💡 TIPS:\n" + "\n".join(f"  • {t}" for t in d["tips"])
    return result


@tool
def skill_gap_analyzer_tool(student_skills: list, target_company: str) -> str:
    """
    Analyze skill gap between student skills and company requirements.

    Args:
        student_skills: List of skills the student knows (e.g. ['Python', 'SQL'])
        target_company: Company the student is targeting (e.g. Amazon, TCS)

    Returns:
        Missing skills and learning roadmap
    """
    requirements = {
        "Amazon":    ["DSA", "System Design", "Java or C++", "OS", "DBMS", "Problem Solving"],
        "Tcs":       ["C or Java", "Aptitude", "Verbal Ability", "Basic SQL"],
        "Infosys":   ["OOP", "DBMS", "OS", "SQL", "Java or Python"],
        "Wipro":     ["C or C++", "DBMS", "OS", "Networking Basics"],
        "Accenture": ["Communication", "OOP", "SQL", "Logical Reasoning"],
        "Cognizant": ["Java", "SQL", "Aptitude", "Communication"],
    }

    company = target_company.strip().title()
    if company not in requirements:
        return f"Requirements not available for {target_company}. Try: Amazon, TCS, Infosys, Wipro"

    required       = requirements[company]
    student_upper  = [s.strip().upper() for s in student_skills]
    required_upper = [r.strip().upper() for r in required]

    have    = [r for r in required if r.upper() in student_upper]
    missing = [r for r in required if r.upper() not in student_upper]

    result  = f"=== SKILL GAP ANALYSIS FOR {company.upper()} ===\n\n"
    result += "✅ YOU HAVE:\n"
    result += "\n".join(f"  • {s}" for s in have) if have else "  • None matched\n"
    result += "\n\n❌ MISSING SKILLS:\n"
    result += "\n".join(f"  • {s}" for s in missing) if missing else "  • None! You are fully ready!\n"

    if missing:
        result += "\n\n📚 LEARNING ROADMAP:\n"
        roadmap = {
            "DSA":            "LeetCode — start Easy → Medium → Hard",
            "System Design":  "Watch Gaurav Sen on YouTube",
            "Java or C++":    "Complete one language from scratch — 4 weeks",
            "OOP":            "Learn 4 pillars — Encapsulation, Inheritance, Polymorphism, Abstraction",
            "SQL":            "Practice on HackerRank SQL section",
            "OS":             "Gate Smashers OS playlist on YouTube",
            "DBMS":           "Gate Smashers DBMS playlist on YouTube",
            "Aptitude":       "IndiaBix daily practice — 30 mins/day",
            "Communication":  "Practice mock HR interviews daily",
        }
        for skill in missing:
            if skill in roadmap:
                result += f"  • {skill}: {roadmap[skill]}\n"
    return result


# ============================================================
# TODO 4: Create the full agent with ALL tools + memory + streaming
# ============================================================
# Combining: eligibility + cgpa + stats + company info + skill gap + memory + streaming

bedrock_model = BedrockModel(
    model_id="amazon.nova-pro-v1:0",
    region_name="us-east-1"
)

agent = Agent(
    model=bedrock_model,
    tools=[
        eligibility_checker_tool,
        cgpa_calculator_tool,
        placement_stats_tool,
        company_info_tool,
        skill_gap_analyzer_tool,
        mem0_memory
    ],
    callback_handler=stream_callback,
    system_prompt="""You are a complete AI Placement Assistant — smart, memory-enabled, and tool-powered.

TOOLS YOU HAVE:
1. eligibility_checker_tool  — check eligible companies by CGPA, backlogs, degree
2. cgpa_calculator_tool      — calculate CGPA from grades and credits
3. placement_stats_tool      — get package and role stats for a company
4. company_info_tool         — get interview rounds, bond, tips for a company
5. skill_gap_analyzer_tool   — find missing skills for a target company
6. mem0_memory               — store and recall student profile across sessions

RULES:
- Always recall memory first to check if student profile exists
- Store student profile as soon as they share it
- Use the correct tool for every question — never guess
- Stream responses naturally
- Be encouraging, mentor-like, and personalized

Always greet student by name if remembered."""
)

# ============================================================
# TODO 5: Interactive chat loop with streaming
# ============================================================
print("=" * 55)
print("🤖 AI Placement Assistant — Full Agent Ready!")
print("=" * 55)
print("Try: 'I am Arjun, CSE, CGPA 7.8, I know Python and SQL'")
print("Try: 'What should I learn to get into Amazon?'")
print("Try: 'Am I eligible for Infosys?'")
print("Try: 'What is Amazon's average package?'")
print("Type 'quit' to exit.\n")

while True:
    try:
        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "q"):
            print("Bye! All the best for your placements! 🚀")
            break

        print("\nAgent: ", end="")

        # TODO: Call the agent with user_input
        agent(user_input)
        print()

    except KeyboardInterrupt:
        print("\nBye! 👋")
        break

print("\n✅ Challenge 4 complete! 🏆")