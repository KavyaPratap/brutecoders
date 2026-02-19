import subprocess
import os
import time
import requests

def github_push_node(state: dict):
    """
    The True Open-Source Flow:
    1. Forks the target repo.
    2. Pushes the branch to the fork.
    3. Opens a Pull Request to the original repo.
    """
    print("--- GIT OPERATIONS: Initiating Fork & Pull Request Pipeline ---")
    
    repo_path = state.get("repo_path")
    repo_url = state.get("repo_url")
    branch_name = state.get("branch_name") 
    fixes = state.get("fixes_applied", [])
    token = os.getenv("GITHUB_TOKEN")
    
    if not fixes:
        print("⚠️ GIT: No valid fixes found in the ledger. Skipping push.")
        return {"run_status": "NO_FIXES_TO_PUSH"}

    if not token:
        print("❌ GIT ERROR: GITHUB_TOKEN not found in environment variables.")
        return {"run_status": "GIT_AUTH_FAILED"}

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    try:
        # 1. Parse Original Owner and Repo Name
        # E.g., https://github.com/HackathonJudges/TestRepo -> HackathonJudges, TestRepo
        clean_url = repo_url.rstrip("/").replace(".git", "")
        parts = clean_url.split("/")
        original_owner = parts[-2]
        repo_name = parts[-1]

        # 2. Get Your Authenticated Username
        user_res = requests.get("https://api.github.com/user", headers=headers)
        user_res.raise_for_status()
        my_username = user_res.json()["login"]

        # 3. Get Original Repo Info (to find their default branch, usually 'main' or 'master')
        repo_res = requests.get(f"https://api.github.com/repos/{original_owner}/{repo_name}", headers=headers)
        repo_res.raise_for_status()
        default_branch = repo_res.json().get("default_branch", "main")

        # 4. Fork the Repository via API
        print(f"--- GIT: Forking {original_owner}/{repo_name} into your account... ---")
        fork_res = requests.post(f"https://api.github.com/repos/{original_owner}/{repo_name}/forks", headers=headers)
        fork_res.raise_for_status()
        
        # GitHub takes a few seconds to build a fork asynchronously. We must pause here.
        print("⏳ Waiting 5 seconds for GitHub to provision the fork...")
        time.sleep(5) 

        # 5. Swap Local Git Remote to point to YOUR FORK, not the original
        fork_url = f"https://x-access-token:{token}@github.com/{my_username}/{repo_name}.git"
        
        # Remove the old origin and add the new fork origin
        subprocess.run(["git", "remote", "remove", "origin"], cwd=repo_path, capture_output=True)
        subprocess.run(["git", "remote", "add", "origin", fork_url], cwd=repo_path, check=True)

        # 6. Branch, Add, Commit, Push (to YOUR fork)
        print(f"--- GIT: Pushing fixed code to your fork (branch: {branch_name}) ---")
        subprocess.run(["git", "checkout", "-b", branch_name], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True, capture_output=True)
        
        commit_msg = fixes[-1].get("commitMsg", "[AI-AGENT] Automated Repair")
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(["git", "push", "-u", "origin", branch_name], cwd=repo_path, check=True, capture_output=True)

        # 7. Open the Pull Request back to the Judges!
        print("--- GIT: Opening Pull Request to original repository ---")
        pr_payload = {
            "title": f"The Healing Agent: Automated Bug Fixes",
            "body": f"## Autonomous Repair Report\nOur agent identified and resolved bugs in this repository.\n\n**Fix Applied:** {commit_msg}",
            "head": f"{my_username}:{branch_name}", # Cross-repository PR format
            "base": default_branch
        }
        
        pr_res = requests.post(
            f"https://api.github.com/repos/{original_owner}/{repo_name}/pulls", 
            json=pr_payload, 
            headers=headers
        )
        
        if pr_res.status_code == 201:
            pr_url = pr_res.json().get("html_url")
            print(f"✅ GIT: Pull Request Successfully Created! -> {pr_url}")
            return {"run_status": "PUSHED_TO_GITHUB"}
        elif pr_res.status_code == 422:
            print("⚠️ GIT: A Pull Request with this branch might already exist, or there are no differences.")
            return {"run_status": "PUSHED_TO_GITHUB"} # Still treat as success for UI
        else:
            pr_res.raise_for_status()

    except requests.exceptions.RequestException as e:
        print(f"❌ GIT API ERROR: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"API Response: {e.response.text}")
        return {"run_status": "GIT_PUSH_FAILED"}
    except Exception as e:
        print(f"❌ GIT SUBPROCESS ERROR: {str(e)}")
        return {"run_status": "GIT_PUSH_FAILED"}