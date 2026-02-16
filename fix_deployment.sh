#!/bin/bash
# Fix Deployment Issues

APP_DIR="/home/universe"

echo "🔧 Fixing deployment issues..."

# 1. Create missing __init__.py files
touch $APP_DIR/api/__init__.py
touch $APP_DIR/content/__init__.py
touch $APP_DIR/core/__init__.py
touch $APP_DIR/simulation/__init__.py

# 2. Create data directories
mkdir -p $APP_DIR/data/public
mkdir -p $APP_DIR/data/snapshots

# 3. Create placeholder JSON files
echo '{"status": "initializing"}' > $APP_DIR/data/public/public_news.json
echo '{"status": "initializing"}' > $APP_DIR/data/public/public_social.json
echo '{"status": "initializing"}' > $APP_DIR/data/public/public_metrics.json
echo '{"status": "initializing"}' > $APP_DIR/data/public/public_snapshot.json

# 4. Update systemd services with PYTHONUNBUFFERED
cat <<'EOF' > /etc/systemd/system/universe-api.service
[Unit]
Description=Universe 2200 API Server
After=network.target

[Service]
User=root
WorkingDirectory=/home/universe
Environment="PYTHONUNBUFFERED=1"
ExecStart=/home/universe/venv/bin/python -m uvicorn server:app --host 0.0.0.0 --port 8000
Restart=always
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

cat <<'EOF' > /etc/systemd/system/universe-sim.service
[Unit]
Description=Universe 2200 Simulation Engine
After=network.target

[Service]
User=root
WorkingDirectory=/home/universe
Environment="PYTHONUNBUFFERED=1"
ExecStart=/home/universe/venv/bin/python run_simulation.py
Restart=always
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# 5. Reload & Restart
systemctl daemon-reload
systemctl restart universe-api
systemctl restart universe-sim

echo "✅ Fix applied!"
echo ""
echo "Check status:"
echo "  systemctl status universe-api"
echo "  systemctl status universe-sim"
echo ""
echo "View logs:"
echo "  journalctl -u universe-api -f"
echo "  journalctl -u universe-sim -f"
