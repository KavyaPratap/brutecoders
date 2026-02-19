# 1. System & Docker Setup
sudo apt update && sudo apt upgrade -y <br>
sudo apt install docker.io docker-compose-plugin -y<br>
sudo systemctl enable --now docker<br>

# 2. Create Project Structure
mkdir -p ~/apache-site/site ~/apache-site/cloudflared<br>
cd ~/apache-site<br>

# 3. Create Frontend Dockerfile (Fixes Node 18 Syntax Error)
mkdir -p frontend<br>
cat << 'EOF' > frontend/Dockerfile<br>
FROM node:20-alpine AS builder<br>
WORKDIR /app<br>
COPY package*.json ./<br>
RUN npm install<br>
COPY . .<br>
RUN npm run build<br>

FROM nginx:alpine<br>
COPY --from=builder /app/dist /usr/share/nginx/html<br>
EXPOSE 80<br>
CMD ["nginx", "-g", "daemon off;"]<br>
EOF<br>

# 4. Create Backend Dockerfile
mkdir -p backend<br>
cat << 'EOF' > backend/Dockerfile<br>
FROM python:3.11-slim<br>
WORKDIR /app<br>
COPY . .<br>
RUN pip install --no-cache-dir fastapi uvicorn sse-starlette pydantic<br>
EXPOSE 8000<br>
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]<br>
EOF<br>

# 5. Create Docker Compose File
cat << 'EOF' > docker-compose.yml<br>
services:<br>
  backend:<br>
    build: ./backend<br>
    container_name: brutecoders_backend<br>
    ports:<br>
      - "8000:8000"<br>
    restart: unless-stopped<br>

  frontend:<br>
    build: ./frontend<br>
    container_name: brutecoders_frontend<br>
    ports:<br>
      - "3000:80"<br>
    depends_on:<br>
      - backend<br>
    restart: unless-stopped<br>
EOF<br>

# 6. Setup Cloudflared Pathing Fix
sudo mkdir -p /root/.cloudflared<br>
sudo cp ~/.cloudflared/*.json /root/.cloudflared/ 2>/dev/null<br>

# 7. Create the Final Deploy Script
cat << 'EOF' > deploy.sh<br>
#!/bin/bash<br>
echo "🏗️ Building Containers..."<br>
docker compose up -d --build<br>
echo "☁️ Starting Tunnel..."<br>
sudo cloudflared tunnel --config /root/.cloudflared/config.yml run brutecoders<br>
EOF<br>
chmod +x deploy.sh<br>

echo "✅ All files created in ~/apache-site"
echo "👉 Run './deploy.sh' to start the project!"




