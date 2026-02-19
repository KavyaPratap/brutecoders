from langgraph.graph import StateGraph, START, END
from .graph_state import AgentState
from .ministers import (
    minister_of_classification, 
    minister_of_localization, 
    minister_of_repair, 
    minister_of_validation
)

# --- DECISION LOGIC (The Agentic "Thinking" Part) ---

def check_validation_status(state: AgentState):
    """
    This is the router. It looks at the state after the Validation Minister runs.
    If the format is bad, it routes back to Repair (up to 3 times).
    If it's good, it ends the cycle.
    """
    print("--- ROUTER: Checking Validation Status ---")
    
    if state.get("run_status") == "FORMATTING_FAILED":
        attempts = state.get("format_attempts", 0)
        if attempts < 3:
            print(f"--- ROUTER: Format invalid. Looping back to Repair (Attempt {attempts}/3) ---")
            return "retry"
        else:
            print("--- ROUTER: Max format attempts reached. Aborting format loop. ---")
            return "end"
            
    print("--- ROUTER: Fix looks good. Proceeding. ---")
    return "end"


# --- BUILD THE GRAPH ---

print("Initializing The Healing Agent Neural Network...")
builder = StateGraph(AgentState)

# 1. Add the Nodes (The Ministers)
builder.add_node("Classifier", minister_of_classification)
builder.add_node("Localizer", minister_of_localization)
builder.add_node("Repair", minister_of_repair)
builder.add_node("Validator", minister_of_validation)

# 2. Define the Linear Flow
builder.add_edge(START, "Classifier")
builder.add_edge("Classifier", "Localizer")
builder.add_edge("Localizer", "Repair")
builder.add_edge("Repair", "Validator")

# 3. Define the Agentic Loop (The Conditional Edge)
builder.add_conditional_edges(
    "Validator",             # From the Validator node...
    check_validation_status, # ...run this decision function...
    {
        "retry": "Repair",   # ...if it says 'retry', go back to Repair...
        "end": END           # ...if it says 'end', finish the graph.
    }
)

# Compile it into a living agent!
healing_agent = builder.compile()