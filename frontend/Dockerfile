# ==========================================
# STAGE 1: Build the React Application
# ==========================================
FROM node:18-alpine AS builder

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and install dependencies first (caches them so rebuilds are faster)
COPY package*.json ./
RUN npm install

# Copy your actual frontend code into the container
COPY . .

# Build the app for production
RUN npm run build

# ==========================================
# STAGE 2: Serve the App with Nginx
# ==========================================
FROM nginx:alpine

# Copy the built static files from Stage 1 into the Nginx server directory
# NOTE: If you used Vite, the folder is usually /app/dist. 
# If you used Create React App, change "dist" to "build" on the line below!
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port 80 for the web traffic
EXPOSE 80

# Start the Nginx server
CMD ["nginx", "-g", "daemon off;"]
