import asyncio
import json
import uuid
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

app = FastAPI(title="The Healing Agent Orchestrator")

# Allow React to talk to FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DATA MODELS ---
# This ensures the data coming from React is perfectly formatted
class RunRequest(BaseModel):
    repoUrl: str
    teamName: str
    leaderName: str

# In-memory database to store active runs
active_runs = {}

# --- UTILITY LOGIC (From Flowchart) ---
def generate_branch_name(team: str, leader: str) -> str:
    """Branch Name Generator Module"""
    team_clean = team.replace(" ", "_").upper()
    leader_clean = leader.replace(" ", "_").upper()
    return f"{team_clean}_{leader_clean}_AI_FIX"

# --- MOCK AI WORKFLOW (The "Fake" Agent) ---
async def agent_workflow_generator(run_id: str, request: RunRequest):
    """
    This simulates the LangGraph + Docker process.
    It yields server-sent events (SSE) to update the React UI in real-time.
    Later, we will replace the asyncio.sleep() with actual LangGraph calls!
    """
    start_time = datetime.now()
    branch_name = generate_branch_name(request.teamName, request.leaderName)

    # Step 1: Start
    yield {"event": "status", "data": "RUNNING"}
    yield {"event": "step", "data": "1"}
    yield {"event": "log", "data": f"Initializing Minister of Intelligence... Cloning {request.repoUrl}"}
    await asyncio.sleep(2)

    # Step 2: Test Discovery
    yield {"event": "step", "data": "2"}
    yield {"event": "log", "data": "Running Initial Test Suite... Failures Detected!"}
    await asyncio.sleep(2)

    # Step 3: AI Cabinet
    yield {"event": "step", "data": "3"}
    yield {"event": "log", "data": "Minister of Classification routing errors... LINTING bug localized."}
    await asyncio.sleep(2)

    # Step 4: Docker Sandbox & Fix Application
    yield {"event": "step", "data": "4"}
    yield {"event": "log", "data": "Minister of Repair generated fix. Preparing Docker Sandbox..."}
    await asyncio.sleep(1.5)
    
    # Send a mock fix to the React Table
    mock_fix = {
        "file": "src/utils.py",
        "type": "LINTING",
        "line": 15,
        "commitMsg": "[AI-AGENT] Remove unused import",
        "status": "FIXED"
    }
    yield {"event": "fix", "data": json.dumps(mock_fix)}
    await asyncio.sleep(1)

    # Step 5: Git Ops
    yield {"event": "step", "data": "5"}
    yield {"event": "log", "data": f"Tests Passed! Pushing to branch: {branch_name}"}
    await asyncio.sleep(2)

    # Final Step: Scoring & Finish
    time_taken = (datetime.now() - start_time).seconds
    
    # Mock Scoring Engine Logic
    mock_score = {
        "base": 100,
        "speedBonus": 10 if time_taken < 300 else 0, # +10 if under 5 mins
        "efficiencyPenalty": 0,
        "total": 110 if time_taken < 300 else 100
    }
    yield {"event": "score", "data": json.dumps(mock_score)}
    yield {"event": "status", "data": "PASSED"}


# --- API ENDPOINTS ---

@app.post("/api/run-agent")
async def start_agent_run(req: RunRequest):
    """Endpoint 1: React calls this when you click 'Run Agent'"""
    run_id = str(uuid.uuid4())
    active_runs[run_id] = req
    return {
        "run_id": run_id, 
        "branch": generate_branch_name(req.teamName, req.leaderName),
        "message": "Agent initialized successfully"
    }

@app.get("/api/stream/{run_id}")
async def stream_agent_logs(run_id: str):
    """Endpoint 2: React connects to this to listen for real-time updates"""
    if run_id not in active_runs:
        return {"error": "Run ID not found"}
    
    req = active_runs[run_id]
    return EventSourceResponse(agent_workflow_generator(run_id, req))