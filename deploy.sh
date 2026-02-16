#!/bin/bash

# Deployment Script for Universe 2200 on CyberPanel/Ubuntu
# Run as root

APP_DIR="/home/universe"
VENV_DIR="$APP_DIR/venv"
USER="root"

echo "🚀 Starting Deployment..."

# 1. Update System & Install Python3 venv
echo "📦 Installing Dependencies..."
apt-get update
apt-get install -y python3-venv python3-pip

# 2. Setup Virtual Environment
echo "🐍 Setting up Python Virtual Environment..."
cd $APP_DIR
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv $VENV_DIR
fi

# 3. Install Requirements
echo "📥 Installing Python Packages..."
$VENV_DIR/bin/pip install -r requirements.txt

# 4. Create Systemd Service for API (Process B)
echo "⚙️ Creating API Service (universe-api.service)..."
cat <<EOF > /etc/systemd/system/universe-api.service
[Unit]
Description=Universe 2200 API Server
After=network.target

[Service]
User=$USER
WorkingDirectory=$APP_DIR
ExecStart=$VENV_DIR/bin/uvicorn server:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 5. Create Systemd Service for Simulation (Process A)
echo "⚙️ Creating Simulation Service (universe-sim.service)..."
cat <<EOF > /etc/systemd/system/universe-sim.service
[Unit]
Description=Universe 2200 Simulation Engine
After=network.target

[Service]
User=$USER
WorkingDirectory=$APP_DIR
ExecStart=$VENV_DIR/bin/python run_simulation.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 6. Enable & Start Services
echo "🔥 Starting Services..."
systemctl daemon-reload
systemctl enable universe-api
systemctl enable universe-sim
systemctl restart universe-api
systemctl restart universe-sim

echo "✅ Deployment Complete!"
echo "   - API: http://178.18.246.141:8000"
echo "   - Simulation: Running in background"
