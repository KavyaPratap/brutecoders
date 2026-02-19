import subprocess
import os

def get_docker_config(repo_path: str):
    """Dynamically detects the repository's language and testing framework."""
    
    # 1. Node.js Detection
    if os.path.exists(os.path.join(repo_path, "package.json")):
        return "node:18-alpine", "npm install && npm test"
    
    # 2. Python Detection (Default fallback)
    test_cmd = ""
    # Check if we need to install dependencies first
    if os.path.exists(os.path.join(repo_path, "requirements.txt")):
        test_cmd += "pip install -r requirements.txt -q && "
        
    # Dynamically chain test runners (if pytest fails/is missing, fallback to unittest)
    test_cmd += "pytest || python -m unittest discover"
    
    # Using 'slim' instead of 'alpine' for Python to avoid C-extension build errors
    return "python:3.11-slim", test_cmd

def run_tests_in_docker(repo_path: str) -> dict:
    """Executes the test suite inside a dynamically assigned, ephemeral Docker container."""
    print("🐳 SPINNING UP DYNAMIC DOCKER CONTAINER...")
    
    abs_path = os.path.abspath(repo_path)
    image, test_cmd = get_docker_config(repo_path)
    
    print(f"--- DOCKER CONFIG: Using image '{image}' ---")
    
    # The command dynamically uses the right image and right execution shell (sh is universal)
    docker_cmd = [
        "docker", "run", "--rm",
        "-v", f"{abs_path}:/app",
        "-w", "/app",
        image,
        "/bin/sh", "-c", test_cmd
    ]
    
    try:
        # 60-second timeout prevents infinite loop attacks from bad AI code
        result = subprocess.run(docker_cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            return {"passed": True, "error_logs": ""}
        else:
            return {"passed": False, "error_logs": result.stdout + "\n" + result.stderr}
            
    except subprocess.TimeoutExpired:
        print("⏳ DOCKER TIMEOUT: AI code caused an infinite loop. Container destroyed.")
        return {"passed": False, "error_logs": "Execution Timeout: Code took too long to execute (possible infinite loop)."}
    except Exception as e:
        print(f"❌ DOCKER ENGINE ERROR: {str(e)}")
        return {"passed": False, "error_logs": f"Docker Engine Error: {str(e)}"}