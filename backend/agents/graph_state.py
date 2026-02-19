from typing import TypedDict, List, Optional
from pydantic import BaseModel

# This defines the exact structure of a Fix, matching your React frontend!
class FixRecord(BaseModel):
    file: str
    type: str
    line: int
    commitMsg: str
    status: str

# This is the "Memory" that gets passed between your Ministers
class AgentState(TypedDict):
    repo_url: str
    repo_path: str          # Where it's cloned locally
    error_message: str      # The raw error from the sandbox
    bug_type: str           # LINTING, SYNTAX, LOGIC, etc.
    target_file: str        # Which file has the bug
    target_line: int        # Which line has the bug
    file_content: str       # The actual code
    proposed_fix: str       # The code Gemini writes
    format_attempts: int    # To prevent infinite loops (max 3)
    retry_count: int        # Total iteration loops (max 5)
    fixes_applied: List[FixRecord]
    run_status: str         # PASSED or FAILED
    test_generated: bool