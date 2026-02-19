import asyncio
import json
import uuid
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

# Docker-only imports now!
from sandbox import run_tests_in_docker, clone_repository 
from agents.graph import healing_agent
from agents.graph_state import AgentState

app = FastAPI(title="The Healing Agent Orchestrator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RunRequest(BaseModel):
    repoUrl: str
    teamName: str
    leaderName: str

active_runs = {}

def generate_branch_name(team: str, leader: str) -> str:
    # Rule: All UPPERCASE, Replace spaces with underscores, End with _AI_Fix
    team_clean = team.strip().replace(" ", "_").upper()
    leader_clean = leader.strip().replace(" ", "_").upper()
    return f"{team_clean}_{leader_clean}_AI_Fix"

async def agent_workflow_generator(run_id: str, request: RunRequest):
    """The main bridge between React, Docker Sandbox, and AI."""
    start_time = datetime.now()
    branch_name = generate_branch_name(request.teamName, request.leaderName)

    yield {"event": "status", "data": "RUNNING"}
    
    # --- 1. CLONE THE REPOSITORY ---
    yield {"event": "step", "data": "1"}
    yield {"event": "log", "data": f"Initializing Minister of Intelligence... Cloning {request.repoUrl}"}
    
    repo_path = clone_repository(request.repoUrl)
    if not repo_path:
        yield {"event": "log", "data": "❌ Failed to clone repository. Check URL."}
        yield {"event": "status", "data": "FAILED"}
        return

    # --- 2. RUN INITIAL TESTS (DOCKER ONLY) ---
    yield {"event": "step", "data": "2"}
    yield {"event": "log", "data": "Booting Docker to run initial Sandbox Tests..."}
    
    initial_test = run_tests_in_docker(repo_path)
    
    if initial_test["passed"]:
        yield {"event": "log", "data": "✅ All tests passed! No bugs found."}
        yield {"event": "status", "data": "PASSED"}
        return
        
    yield {"event": "log", "data": "❌ Failures Detected! Capturing logs and waking AI..."}
    await asyncio.sleep(1)

    # --- 3. WAKE UP THE AI CABINET ---
    yield {"event": "step", "data": "3"}
    
    initial_state: AgentState = {
        "error_message": initial_test["error_logs"],
        "repo_url": request.repoUrl,
        "repo_path": repo_path, 
        "branch_name": branch_name, # Pass branch name into the graph state for GitOps!
        "file_content": "", "target_file": "", "bug_type": "", "target_line": 0, 
        "proposed_fix": "", "format_attempts": 0, "retry_count": 0, 
        "fixes_applied": [], "run_status": "", "test_generated": False
    }

    # Stream the graph execution
    for output in healing_agent.stream(initial_state):
        for node_name, state_update in output.items():
            
            if node_name == "Classifier":
                yield {"event": "log", "data": f"🔍 Bug Classified: {state_update.get('bug_type')}"}
                
            elif node_name == "Localizer":
                yield {"event": "log", "data": f"📍 Pinpointed to {state_update.get('target_file')} (Line {state_update.get('target_line')})"}
                
            elif node_name == "Repair":
                yield {"event": "step", "data": "4"}
                yield {"event": "log", "data": "🔨 Forging new code fix..."}
                
            elif node_name == "Validator":
                status = state_update.get('run_status')
                yield {"event": "log", "data": f"⚖️ Validation Status: {status}"}
                    
            elif node_name == "Sandbox":
                sandbox_status = state_update.get('run_status')
                
                if sandbox_status == "TESTS_PASSED":
                    yield {"event": "log", "data": "✅ Execution Environment: Tests Passed!"}
                    
                    # 🟢 UI turns green here!
                    fixes = state_update.get("fixes_applied", [])
                    if fixes:
                        final_fix = fixes[-1]
                        final_fix["status"] = "SUCCESS" 
                        yield {"event": "fix", "data": json.dumps(final_fix)}
                        
                else:
                    yield {"event": "log", "data": "❌ Execution Environment: Tests Failed! Looping back to AI..."}
                    await asyncio.sleep(2) 
                    
            elif node_name == "GitOps":
                git_status = state_update.get('run_status')
                if git_status == "PUSHED_TO_GITHUB":
                    yield {"event": "log", "data": f"🚀 Successfully pushed branch {branch_name} to GitHub!"}
                else:
                    yield {"event": "log", "data": f"⚠️ Git Push Failed: {git_status} (Check repo permissions)"}
        
        # Prevent API Rate Limits
        await asyncio.sleep(2)

    # --- 4. FINISH & SCORE ---
    yield {"event": "step", "data": "5"}
    yield {"event": "log", "data": "Run Complete! Generating final score..."}
    
    time_taken = (datetime.now() - start_time).seconds
    mock_score = {
        "base": 100,
        "speedBonus": 10 if time_taken < 300 else 0, # < 5 mins gets bonus
        "efficiencyPenalty": 0,
        "total": 110 if time_taken < 300 else 100
    }
    
    yield {"event": "score", "data": json.dumps(mock_score)}
    yield {"event": "status", "data": "PASSED"}


@app.post("/api/run-agent")
async def start_agent_run(req: RunRequest):
    run_id = str(uuid.uuid4())
    active_runs[run_id] = req
    return {"run_id": run_id, "branch": generate_branch_name(req.teamName, req.leaderName)}

@app.get("/api/stream/{run_id}")
async def stream_agent_logs(run_id: str):
    if run_id not in active_runs:
        return {"error": "Run ID not found"}
    req = active_runs[run_id]
    return EventSourceResponse(agent_workflow_generator(run_id, req))