from langgraph.graph import StateGraph, START, END
from .graph_state import AgentState
from .ministers import (
    minister_of_classification, 
    minister_of_localization, 
    minister_of_repair, 
    minister_of_validation,
    minister_of_qa,       # 🧪 Added QA Minister
    execution_sandbox
)
from .git_ops import github_push_node # 🛠️ Added Git Operations

# --- 🚦 ROUTING LOGIC (The Brain's Decisions) ---

def check_validation_status(state: AgentState):
    """Routes based on formatting and commit message rules."""
    print("--- ROUTER: Checking Validation Status ---")
    if state.get("run_status") == "FORMATTING_FAILED":
        attempts = state.get("format_attempts", 0)
        if attempts < 3:
            print(f"--- ROUTER: Format invalid. Retrying Repair (Attempt {attempts + 1}/3) ---")
            return "retry_format"
        return "end"
            
    print("--- ROUTER: Format is perfect. Proceeding to Sandbox. ---")
    return "execute"

def check_sandbox_status(state: AgentState):
    """Decides if we fix, generate tests, or push to GitHub."""
    run_status = state.get("run_status")
    
    # 1. SUCCESS: Tests passed! Time to ship it to GitHub.
    if run_status == "TESTS_PASSED":
        print("--- ROUTER: Tests Passed. Sending to Git Operations. ---")
        return "push"
    
    # 2. NO TESTS FOUND: If it's a new repo, hire the Minister of QA!
    error_log = state.get("error_message", "")
    if ("No tests found" in error_log or "collected 0 items" in error_log) and not state.get("test_generated"):
        print("--- ROUTER: No tests detected. Triggering Minister of QA. ---")
        return "generate_tests"

    # 3. FAILURE: Tests failed, try to fix it again (up to 3 times)
    attempts = state.get("retry_count", 0)
    if attempts < 3:
        print(f"--- ROUTER: Logic Error detected. Looping back to Classifier (Attempt {attempts + 1}/3) ---")
        return "retry_logic"
    
    print("--- ROUTER: Max retries reached. Stopping. ---")
    return "end"

# --- 🏗️ BUILD THE GRAPH ---

print("Initializing The Healing Agent Neural Network...")
builder = StateGraph(AgentState)

# Define the Cabinet Nodes
builder.add_node("Classifier", minister_of_classification)
builder.add_node("Localizer", minister_of_localization)
builder.add_node("Repair", minister_of_repair)
builder.add_node("Validator", minister_of_validation)
builder.add_node("Sandbox", execution_sandbox)
builder.add_node("QA", minister_of_qa)          # 🧪 New Node
builder.add_node("GitOps", github_push_node)    # 🛠️ Final Node

# 1. The Startup Sequence
builder.add_edge(START, "Classifier")
builder.add_edge("Classifier", "Localizer")
builder.add_edge("Localizer", "Repair")
builder.add_edge("Repair", "Validator")

# 2. The Validation Loop
builder.add_conditional_edges(
    "Validator",
    check_validation_status,
    {
        "retry_format": "Repair", 
        "execute": "Sandbox", 
        "end": END
    }
)

# 3. The Autonomous Environment Loop (The Heart of the Agent)
builder.add_conditional_edges(
    "Sandbox",
    check_sandbox_status,
    {
        "generate_tests": "QA",      # 🧪 Create tests if none exist
        "retry_logic": "Classifier", # 🔄 Try to fix the code again
        "push": "GitOps",            # 🚀 Ship it to GitHub!
        "end": END
    }
)

# 4. Closing the QA Loop
# Once tests are generated, we go back to the start to find the bugs those tests reveal!
builder.add_edge("QA", "Classifier")

# 5. Ending the Run
builder.add_edge("GitOps", END)

healing_agent = builder.compile()