<h1 align="center">The Healing Agent</h1>
<p align="center"><strong>An Autonomous, Self-Healing Multi-Agent CI/CD Pipeline</strong></p>

## 🚀 Overview
The Healing Agent is a completely autonomous AI orchestrator designed to identify, localize, and repair software bugs in real-time. Moving beyond traditional static analysis, this system implements **Reverse-Engineered Test Driven Development (RTDD)**. It physically executes code in a secure, ephemeral Docker sandbox to verify its own repairs before autonomously opening a Pull Request with the fix.

Created by Kavya Pratap Singh, this project aims to bridge the gap between AI generation and robust, production-ready software engineering.

## 🧠 The "Cabinet of Ministers" Architecture
Our LangGraph-powered orchestrator utilizes specialized LLM nodes (Ministers) that handle distinct stages of the SDLC using Google's Gemini 3 Flash:

* **🧪 Minister of QA:** If a repository lacks tests, this agent dynamically generates a `unittest` suite to establish a "truth" baseline.
* **🔍 Minister of Classification & Localization:** Categorizes bugs (Logic, Syntax, Linting) and pinpoints the exact file and line number.
* **🔨 Minister of Repair:** Forges precise code fixes and generates professional Git commit messages.
* **🐳 Execution Sandbox:** A dynamic, ephemeral Docker container that safely executes the AI's code to verify the fix.
* **🛠️ GitOps Pipeline:** Autonomously forks the target repository via the GitHub REST API, pushes the validated branch, and opens a Pull Request back to the original codebase.

## 🛠️ Technology Stack
* **AI Orchestration:** LangGraph, Google Gemini 3 Flash
* **Backend:** FastAPI, SSE (Server-Sent Events) for real-time UI telemetry
* **Frontend:** React (Vite), Node 20, Nginx
* **Infrastructure:** Docker, Docker Compose, Cloudflared Tunnels

---

## 💻 Local Development Setup

### Prerequisites
* Docker Desktop installed and running.
* A GitHub Fine-Grained Personal Access Token (with `Contents` and `Pull requests` Read/Write permissions).

### Environment Variables
Create a `.env` file in the `backend/` directory:
```env
GITHUB_TOKEN=github_pat_your_token_here
```

---

## 🌍 Production Deployment (Ubuntu/Debian)
We have provided a fully automated deployment pipeline that builds the Docker containers and exposes the application securely via a Cloudflare Tunnel.

### 1. System & Docker Setup
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install docker.io docker-compose-plugin -y
sudo systemctl enable --now docker
```

### 2. Scaffold the Project Directory
```bash
mkdir -p ~/apache-site/site ~/apache-site/cloudflared
cd ~/apache-site
```

### 3. Build Configuration
The project utilizes a multi-stage Docker build for the React frontend and a lightweight Python 3.11 environment for the FastAPI orchestrator. 

**docker-compose.yml**
```yaml
services:
  backend:
    build: ./backend
    container_name: brutecoders_backend
    ports:
      - "8000:8000"
    restart: unless-stopped

  frontend:
    build: ./frontend
    container_name: brutecoders_frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
    restart: unless-stopped
```

### 4. Cloudflared Tunnel Configuration
Ensure your Cloudflare tunnel credentials are moved to the root directory for the deployment script to access:
```bash
sudo mkdir -p /root/.cloudflared
sudo cp ~/.cloudflared/*.json /root/.cloudflared/ 2>/dev/null
```

### 5. Launch the Application
Run the automated deployment script to spin up the containers and initialize the secure tunnel:
```bash
cat << 'EOF' > deploy.sh
#!/bin/bash
echo "🏗️ Building Containers..."
docker compose up -d --build

echo "☁️ Starting Tunnel..."
sudo cloudflared tunnel --config /root/.cloudflared/config.yml run brutecoders
EOF

chmod +x deploy.sh
./deploy.sh
```

## 🎯 Hackathon Test Case Execution
To evaluate the agent against standard test cases:
1. Navigate to the live URL provided by the Cloudflare tunnel.
2. Enter the target GitHub Repository URL.
3. Input Team Name and Leader Name (e.g., `RIFT ORGANISERS`, `Saiyam Kumar`).
4. Click **Run Agent**.
5. Watch the real-time telemetry as the agent detects bugs, tests them in Docker, and pushes the required `TEAM_NAME_LEADER_NAME_AI_Fix` branch.
