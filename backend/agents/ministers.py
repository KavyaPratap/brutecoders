import json
import re
from langchain_core.messages import SystemMessage, HumanMessage
from .llm_config import llm
from .graph_state import AgentState

# ==========================================
# 🏛️ PROMPTS
# ==========================================

CLASSIFIER_PROMPT = """
You are the "Minister of Classification" in an autonomous code-repair system.
Your ONLY job is to analyze error logs and categorize the bug into exactly one of the following categories:
- LINTING
- SYNTAX
- LOGIC
- TYPE_ERROR
- IMPORT
- INDENTATION

Rules:
1. You must respond with ONLY the category name. Nothing else. No explanation.
2. If the error log contains multiple issues, prioritize the most fundamental one that is likely causing the others.
3. If the logs indicate a test failure without a clear error message, classify it as LOGIC.
4. Do not hallucinate a category not in the list.

Examples:
Input: "IndentationError: expected an indented block" -> Output: INDENTATION
Input: "NameError: name 'pd' is not defined" -> Output: IMPORT
Input: "TypeError: unsupported operand type(s) for +: 'int' and 'str'" -> Output: TYPE_ERROR
"""

LOCALIZER_PROMPT = """
You are the "Minister of Localization" in an autonomous code-repair system.
Your ONLY job is to analyze the provided error log and extract the EXACT file path and line number where the crash originated.

Rules:
1. Respond ONLY with a valid JSON object. Do NOT include markdown code blocks (like ```json). Just the raw JSON string.
2. The JSON must have exactly two keys: "file" and "line".
3. "file" must be a string representing the relative path.
4. "line" must be an integer. If no line number is found, return 0.

Example Output:
{"file": "src/calculator.py", "line": 10}
"""

REPAIR_PROMPT = """
You are the "Minister of Repair" in an autonomous code-repair system.
You will be provided with the Bug Type, Location, Error Log, and Current Code.

Your ONLY job is to fix the bug and return the complete, corrected code.

Rules:
1. Do NOT use JSON.
2. You MUST respond in this EXACT format:

COMMIT: [AI-AGENT] <short description of fix>
```python
<your complete fixed file code here>

"""


def minister_of_classification(state: AgentState) -> AgentState:
    """Analyzes the error logs and determines the bug type."""
    print("--- MINISTER OF CLASSIFICATION: Analyzing Errors ---")
    error_logs = state.get("error_message", "")

    messages = [
        SystemMessage(content=CLASSIFIER_PROMPT),
        HumanMessage(content=f"Here are the error logs from the sandbox:\n\n{error_logs}")
    ]

    response = llm.invoke(messages)
    bug_type = response.content.strip().upper()

    ALLOWED_TYPES = {"LINTING", "SYNTAX", "LOGIC", "TYPE_ERROR", "IMPORT", "INDENTATION"}
    if bug_type not in ALLOWED_TYPES:
        print(f"WARNING: LLM returned invalid bug type '{bug_type}'. Defaulting to LOGIC.")
        bug_type = "LOGIC"

    print(f"--- Bug Classified as: {bug_type} ---")
    return {"bug_type": bug_type}
def minister_of_localization(state: AgentState) -> AgentState:
    """Analyzes the error logs to pinpoint the exact file and line number."""
    print("--- MINISTER OF LOCALIZATION: Pinpointing Error Location ---")
    error_logs = state.get("error_message", "")

    messages = [
        SystemMessage(content=LOCALIZER_PROMPT),
        HumanMessage(content=f"Error Logs:\n\n{error_logs}")
    ]

    response = llm.invoke(messages)
    raw_output = response.content.strip()

    if raw_output.startswith("```json"):
        raw_output = raw_output.replace("```json", "").replace("```", "").strip()
        
    try:
        location_data = json.loads(raw_output)
        target_file = location_data.get("file", "unknown")
        target_line = int(location_data.get("line", 0))
        
        print(f"--- Location Found -> File: {target_file} | Line: {target_line} ---")
        return {"target_file": target_file, "target_line": target_line}
        
    except json.JSONDecodeError:
        print(f"WARNING: Minister of Localization hallucinated invalid JSON: {raw_output}")
        return {"target_file": "unknown", "target_line": 0}
def minister_of_repair(state: AgentState) -> AgentState:
    """Generates the actual code fix and the strict commit message."""
    print("--- MINISTER OF REPAIR: Forging the Fix ---")

    context = f"""
    Bug Type: {state.get('bug_type', 'UNKNOWN')}
    Location: {state.get('target_file', 'unknown')} (Line {state.get('target_line', 0)})
    Error Log: {state.get('error_message', '')}
    Current File Content:
    {state.get('file_content', '')}
    """

    messages = [
        SystemMessage(content=REPAIR_PROMPT),
        HumanMessage(content=context)
    ]

    response = llm.invoke(messages)
    raw_output = response.content.strip()

    # 1. Extract the Commit Message using Regex
    commit_match = re.search(r'COMMIT:\s*(.+)', raw_output)
    commit_msg = commit_match.group(1).strip() if commit_match else "[AI-AGENT] Attempted automated fix"

    # 2. Extract the Python Code using Regex
    code_match = re.search(r'```python\n(.*?)\n```', raw_output, re.DOTALL)
    fixed_code = code_match.group(1) if code_match else state.get("file_content", "")

    print(f"--- Fix Generated! Commit: {commit_msg} ---")

    # Create the new fix record
    new_fix = {
        "file": state.get("target_file", "unknown"),
        "type": state.get("bug_type", "LOGIC"),
        "line": state.get("target_line", 0),
        "commitMsg": commit_msg,
        "status": "PENDING_VALIDATION"
    }

    # Return the updated state
    return {
        "proposed_fix": fixed_code, 
        # We append to the existing list of fixes, or create a new one if it's empty
        "fixes_applied": state.get("fixes_applied", []) + [new_fix]
    }
def minister_of_validation(state: AgentState) -> AgentState:
    """
    Checks if the generated fix matches the required formatting rules.
    This is the core of the Agent's self-reflection loop.
    """
    print("--- MINISTER OF VALIDATION: Inspecting the Fix ---")

    # Check if there are any fixes to validate
    fixes = state.get("fixes_applied", [])
    if not fixes:
        print("--- Validation FAILED: No fix found. ---")
        return {"run_status": "FORMATTING_FAILED", "format_attempts": state.get("format_attempts", 0) + 1}
        
    latest_fix = fixes[-1]
    commit_msg = latest_fix.get("commitMsg", "")
    proposed_code = state.get("proposed_fix", "")

    # Rule 1: Commit message must start with [AI-AGENT]
    # Rule 2: Code must actually exist
    if commit_msg.startswith("[AI-AGENT]") and len(proposed_code.strip()) > 0:
        print("--- Validation PASSED: Format is pristine. ---")
        # We update the status of the specific fix object
        latest_fix["status"] = "VALIDATED"
        # Since we modified the dictionary inside the list, we just return the list back
        return {"run_status": "FORMAT_VALID", "fixes_applied": fixes}
    else:
      print(f"--- Validation FAILED: Commit message '{commit_msg}' violates rules. ---")
      latest_fix["status"] = "FAILED"
      return {"run_status": "FORMATTING_FAILED", "format_attempts": state.get("format_attempts", 0) + 1, "fixes_applied": fixes}