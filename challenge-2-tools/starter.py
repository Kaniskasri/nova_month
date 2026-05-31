"""
Challenge 2: AI Placement Assistant — Custom Tools
Adding 4 tools to the Placement Assistant using Strands SDK + Amazon Bedrock Nova Pro

Instructions:
  1. Make sure AWS credentials are configured (aws configure)
  2. Make sure Amazon Nova Pro is enabled in Bedrock console
  3. Run: python starter.py
"""

# ─────────────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────────────

from strands import Agent, tool
from strands.models.bedrock import BedrockModel

# ─────────────────────────────────────────────
# TODO 1: Create BedrockModel with Nova Pro
# ─────────────────────────────────────────────

bedrock_model = BedrockModel(
    model_id="amazon.nova-pro-v1:0",
    region_name="us-east-1"
)

# ─────────────────────────────────────────────
# TODO 2: Build Tool 1 — Eligibility Checker
# ─────────────────────────────────────────────

@tool
def eligibility_checker_tool(cgpa: float, backlogs: int, degree: str) -> str:
    """
    Check which companies a student is eligible for
    based on their CGPA, number of backlogs, and degree.

    Args:
        cgpa: Student's CGPA (e.g. 7.8)
        backlogs: Number of active backlogs (e.g. 0)
        degree: Student's degree (e.g. B.E, B.Tech, BCA)

    Returns:
        List of eligible and non-eligible companies with reasons
    """

    # Company eligibility rules
    companies = {
        "TCS": {
            "min_cgpa": 6.0,
            "max_backlogs": 0,
            "allowed_degrees": ["B.E", "B.Tech", "M.E", "M.Tech", "MCA", "BCA"]
        },
        "Infosys": {
            "min_cgpa": 6.5,
            "max_backlogs": 0,
            "allowed_degrees": ["B.E", "B.Tech", "M.E", "M.Tech", "MCA", "BCA"]
        },
        "Wipro": {
            "min_cgpa": 6.0,
            "max_backlogs": 0,
            "allowed_degrees": ["B.E", "B.Tech", "M.E", "M.Tech", "MCA", "BCA"]
        },
        "Cognizant": {
            "min_cgpa": 6.0,
            "max_backlogs": 0,
            "allowed_degrees": ["B.E", "B.Tech", "M.E", "M.Tech", "MCA", "BCA"]
        },
        "Accenture": {
            "min_cgpa": 6.5,
            "max_backlogs": 0,
            "allowed_degrees": ["B.E", "B.Tech", "M.E", "M.Tech", "MCA", "BCA"]
        },
        "Amazon": {
            "min_cgpa": 8.0,
            "max_backlogs": 0,
            "allowed_degrees": ["B.E", "B.Tech", "M.E", "M.Tech"]
        },
        "HCL": {
            "min_cgpa": 6.0,
            "max_backlogs": 0,
            "allowed_degrees": ["B.E", "B.Tech", "M.E", "M.Tech", "MCA", "BCA"]
        },
        "Capgemini": {
            "min_cgpa": 6.0,
            "max_backlogs": 0,
            "allowed_degrees": ["B.E", "B.Tech", "M.E", "M.Tech", "MCA", "BCA"]
        }
    }

    eligible = []
    not_eligible = []

    for company, rules in companies.items():
        reasons = []
        is_eligible = True

        if cgpa < rules["min_cgpa"]:
            is_eligible = False
            reasons.append(f"CGPA {cgpa} is below minimum {rules['min_cgpa']}")

        if backlogs > rules["max_backlogs"]:
            is_eligible = False
            reasons.append(f"Has {backlogs} backlog(s), company requires 0")

        if degree not in rules["allowed_degrees"]:
            is_eligible = False
            reasons.append(f"Degree {degree} not in allowed list")

        if is_eligible:
            eligible.append(f"✅ {company} — Eligible (CGPA: {cgpa}, Backlogs: {backlogs})")
        else:
            not_eligible.append(f"❌ {company} — Not Eligible ({', '.join(reasons)})")

    result = "=== ELIGIBILITY RESULTS ===\n\n"
    result += "ELIGIBLE COMPANIES:\n" + "\n".join(eligible) + "\n\n"
    result += "NOT ELIGIBLE:\n" + "\n".join(not_eligible)
    return result


# ─────────────────────────────────────────────
# TODO 3: Build Tool 2 — CGPA Calculator
# ─────────────────────────────────────────────

@tool
def cgpa_calculator_tool(grades: list, credits: list) -> str:
    """
    Calculate CGPA from grades and credits for each subject.

    Args:
        grades: List of grade points for each subject (e.g. [9, 8, 7, 10, 8])
        credits: List of credits for each subject  (e.g. [4, 4, 3, 3, 2])

    Returns:
        Calculated CGPA value
    """

    if len(grades) != len(credits):
        return "Error: Number of grades and credits must be equal"

    if len(grades) == 0:
        return "Error: Please provide at least one subject"

    total_points = sum(g * c for g, c in zip(grades, credits))
    total_credits = sum(credits)

    if total_credits == 0:
        return "Error: Total credits cannot be zero"

    cgpa = round(total_points / total_credits, 2)

    result = "=== CGPA CALCULATION ===\n\n"
    for i, (g, c) in enumerate(zip(grades, credits)):
        result += f"Subject {i+1}: Grade {g} × Credit {c} = {g*c} points\n"

    result += f"\nTotal Points : {total_points}"
    result += f"\nTotal Credits: {total_credits}"
    result += f"\n\n🎓 Your CGPA is: {cgpa}"

    if cgpa >= 8.0:
        result += "\n💡 Excellent! You are eligible for top companies like Amazon."
    elif cgpa >= 6.5:
        result += "\n💡 Good! You are eligible for Infosys, Accenture, and more."
    elif cgpa >= 6.0:
        result += "\n💡 You are eligible for TCS, Wipro, HCL, and Capgemini."
    else:
        result += "\n💡 Work on improving your CGPA for better placement opportunities."

    return result


# ─────────────────────────────────────────────
# TODO 4: Build Tool 3 — Placement Stats
# ─────────────────────────────────────────────

@tool
def placement_stats_tool(company_name: str) -> str:
    """
    Get placement statistics for a specific company
    including average package, total hires, and top roles.

    Args:
        company_name: Name of the company (e.g. TCS, Infosys, Amazon)

    Returns:
        Placement statistics for the company
    """

    stats = {
        "TCS": {
            "avg_package": "3.5 LPA",
            "highest_package": "7 LPA",
            "total_hires": "40,000+ per year",
            "top_roles": ["System Engineer", "Assistant System Engineer", "Developer"],
            "bond": "2 years",
            "hiring_months": "August - December"
        },
        "Infosys": {
            "avg_package": "3.6 LPA",
            "highest_package": "8 LPA",
            "total_hires": "25,000+ per year",
            "top_roles": ["Systems Engineer", "Technology Analyst", "Associate"],
            "bond": "1 year",
            "hiring_months": "September - January"
        },
        "Wipro": {
            "avg_package": "3.5 LPA",
            "highest_package": "6.5 LPA",
            "total_hires": "15,000+ per year",
            "top_roles": ["Project Engineer", "Software Engineer", "Analyst"],
            "bond": "2 years",
            "hiring_months": "August - November"
        },
        "Amazon": {
            "avg_package": "26 LPA",
            "highest_package": "45 LPA",
            "total_hires": "500-800 campus hires/year",
            "top_roles": ["SDE-1", "Data Engineer", "Cloud Support Engineer"],
            "bond": "None",
            "hiring_months": "July - October"
        },
        "Accenture": {
            "avg_package": "4.5 LPA",
            "highest_package": "9 LPA",
            "total_hires": "20,000+ per year",
            "top_roles": ["Associate Software Engineer", "Analyst", "Consultant"],
            "bond": "1 year",
            "hiring_months": "October - February"
        },
        "Cognizant": {
            "avg_package": "4 LPA",
            "highest_package": "8 LPA",
            "total_hires": "18,000+ per year",
            "top_roles": ["Programmer Analyst", "Associate", "Developer"],
            "bond": "1 year",
            "hiring_months": "September - December"
        }
    }

    company = company_name.strip().title()
    if company not in stats:
        return f"Sorry, stats for {company_name} are not available. Try: TCS, Infosys, Wipro, Amazon, Accenture, Cognizant"

    data = stats[company]
    result = f"=== {company.upper()} PLACEMENT STATS ===\n\n"
    result += f"💰 Average Package  : {data['avg_package']}\n"
    result += f"🏆 Highest Package  : {data['highest_package']}\n"
    result += f"👥 Total Hires/Year : {data['total_hires']}\n"
    result += f"📋 Top Roles        : {', '.join(data['top_roles'])}\n"
    result += f"📜 Bond Period      : {data['bond']}\n"
    result += f"📅 Hiring Season    : {data['hiring_months']}\n"
    return result


# ─────────────────────────────────────────────
# TODO 5: Build Tool 4 — Company Info
# ─────────────────────────────────────────────

@tool
def company_info_tool(company_name: str) -> str:
    """
    Get detailed company information including interview rounds,
    work locations, bond details, and preparation tips.

    Args:
        company_name: Name of the company (e.g. TCS, Infosys, Amazon)

    Returns:
        Detailed company information and interview process
    """

    info = {
        "TCS": {
            "interview_rounds": [
                "1. Online Test (Aptitude + English + Coding)",
                "2. Technical Interview (C, Java, Python basics)",
                "3. HR Interview (Communication, attitude)"
            ],
            "work_locations": ["Chennai", "Pune", "Hyderabad", "Bangalore", "Mumbai"],
            "bond": "2 years service agreement",
            "tips": [
                "Focus on TCS NQT pattern",
                "Practice verbal ability seriously",
                "Know at least one programming language well",
                "Be confident in HR round"
            ]
        },
        "Infosys": {
            "interview_rounds": [
                "1. Online Assessment (Aptitude + Logical + Verbal + Coding)",
                "2. Technical Interview (OOP, DBMS, OS)",
                "3. HR Interview"
            ],
            "work_locations": ["Bangalore", "Pune", "Hyderabad", "Chennai", "Mysore"],
            "bond": "1 year service agreement",
            "tips": [
                "Strong OOP concepts required",
                "Practice SQL queries",
                "Infosys focuses heavily on communication skills",
                "Study OS and DBMS basics"
            ]
        },
        "Amazon": {
            "interview_rounds": [
                "1. Online Assessment (DSA — 2 coding problems in 90 min)",
                "2. Technical Round 1 (DSA + Problem Solving)",
                "3. Technical Round 2 (System Design)",
                "4. Bar Raiser Round (Behavioural + Leadership Principles)"
            ],
            "work_locations": ["Bangalore", "Hyderabad", "Chennai"],
            "bond": "No bond",
            "tips": [
                "LeetCode Medium/Hard level DSA is must",
                "Learn Amazon Leadership Principles (16 principles)",
                "Practice System Design for SDE-1",
                "STAR format for behavioural questions"
            ]
        },
        "Wipro": {
            "interview_rounds": [
                "1. Online Test (Aptitude + English + Coding)",
                "2. Technical Interview",
                "3. HR Interview"
            ],
            "work_locations": ["Bangalore", "Hyderabad", "Pune", "Chennai", "Kolkata"],
            "bond": "2 years service agreement",
            "tips": [
                "Wipro Elite NTH pattern for top package",
                "Core CS subjects: DBMS, OS, Networks",
                "Basic coding in C/C++/Java/Python",
                "Good communication for HR"
            ]
        }
    }

    company = company_name.strip().title()
    if company not in info:
        return f"Sorry, info for {company_name} not available. Try: TCS, Infosys, Amazon, Wipro"

    data = info[company]
    result = f"=== {company.upper()} COMPANY INFO ===\n\n"
    result += "📋 INTERVIEW ROUNDS:\n"
    result += "\n".join(data["interview_rounds"]) + "\n\n"
    result += f"📍 WORK LOCATIONS: {', '.join(data['work_locations'])}\n\n"
    result += f"📜 BOND: {data['bond']}\n\n"
    result += "💡 PREPARATION TIPS:\n"
    result += "\n".join(f"  • {tip}" for tip in data["tips"])
    return result


# ─────────────────────────────────────────────
# TODO 6: Create Agent with all 4 tools
# ─────────────────────────────────────────────

agent = Agent(
    model=bedrock_model,
    tools=[
        eligibility_checker_tool,
        cgpa_calculator_tool,
        placement_stats_tool,
        company_info_tool
    ],
    system_prompt="""You are an AI Placement Assistant — a smart campus recruitment mentor.

You have access to 4 tools:
1. eligibility_checker_tool — checks which companies a student can apply to
2. cgpa_calculator_tool     — calculates CGPA from grades and credits
3. placement_stats_tool     — gives package, roles, hiring stats for a company
4. company_info_tool        — gives interview rounds, bond, locations for a company

RULES:
- Always use the correct tool when the student asks about eligibility, CGPA, stats, or company info
- Never guess — use tools to give accurate answers
- Be encouraging and mentor-like
- After giving tool results, add 1-2 lines of personalized advice"""
)

# ─────────────────────────────────────────────
# TODO 7: Run the chat loop
# ─────────────────────────────────────────────

print("=" * 50)
print("🎓 AI Placement Assistant — Challenge 2")
print("Powered by Amazon Bedrock Nova Pro + Tools")
print("=" * 50)
print("Ask me about eligibility, CGPA, company info!")
print("Type 'exit' to quit.\n")

while True:
    user_input = input("You: ").strip()

    if user_input.lower() in ["exit", "quit", "bye"]:
        print("🤖 Agent: All the best for your placements! 🚀")
        break

    if not user_input:
        continue

    print("🤖 Agent: ", end="", flush=True)
    response = agent(user_input)
    print(response)
    print()

print("\n✅ Challenge 2 complete!")