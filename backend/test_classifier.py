from agents.graph import healing_agent
from agents.graph_state import AgentState

# The same broken code as before
broken_code = """
def calculate_area(radius):
    # Bug: Cannot multiply a string and an int!
    return "3.14" * radius * radius

print(calculate_area(5))
"""

# 1. Initialize the starting memory of the Agent
initial_state: AgentState = {
    "error_message": """
    Traceback (most recent call last):
      File "main.py", line 5, in <module>
        print(calculate_area(5))
      File "main.py", line 3, in calculate_area
        return "3.14" * radius * radius
    TypeError: can't multiply sequence by non-int of type 'float'
    """,
    "file_content": broken_code,
    "target_file": "main.py",
    
    # Empty defaults
    "repo_url": "", "repo_path": "", "bug_type": "", 
    "target_line": 0, "proposed_fix": "", "format_attempts": 0, 
    "retry_count": 0, "fixes_applied": [], "run_status": ""
}

print("\n🚀 KICKING OFF THE AUTONOMOUS AGENT...\n")

# 2. Run the Graph! 
# We don't have to call the ministers individually anymore. 
# LangGraph handles the routing automatically.
final_state = healing_agent.invoke(initial_state)

print("\n===================================")
print("🏁 AGENT RUN COMPLETE")
print("===================================")
print(f"Bug Classified As : {final_state['bug_type']}")
print(f"Target Location   : {final_state['target_file']} (Line {final_state['target_line']})")
print(f"Final Status      : {final_state['run_status']}")
print("-----------------------------------")
print("PROPOSED FIX:")
print(final_state['proposed_fix'])