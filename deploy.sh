#!/usr/bin/env bash
# Deploy script for VipPlay247 Bot
# Intended to be run as root on the target server.

set -euo pipefail
BOT_USER=${BOT_USER:-vipplay247}
BOT_HOME=/home/${BOT_USER}
REPO_URL="https://github.com/sixtyfourbitsquad/Mahadev-Ads-Agency.git"
APP_DIR="${BOT_HOME}/vipplay247-bot"
SERVICE_NAME=vipplay247-bot

if [ "$(id -u)" -ne 0 ]; then
  echo "This script must be run as root. Use: sudo bash deploy.sh"
  exit 1
fi

# Create bot user if missing
if ! id -u "${BOT_USER}" >/dev/null 2>&1; then
  echo "Creating user ${BOT_USER}..."
  useradd -m -s /bin/bash "${BOT_USER}"
fi

# Install system packages
export DEBIAN_FRONTEND=noninteractive
apt update
apt install -y git python3 python3-venv python3-pip

# Create application directory and clone or pull
if [ ! -d "${APP_DIR}" ]; then
  echo "Cloning repository into ${APP_DIR}"
  sudo -u "${BOT_USER}" git clone "${REPO_URL}" "${APP_DIR}"
else
  echo "Repository exists, pulling latest changes"
  cd "${APP_DIR}"
  sudo -u "${BOT_USER}" git pull --ff-only || true
fi

cd "${APP_DIR}"

# Create virtualenv and install requirements
if [ ! -d "venv" ]; then
  sudo -u "${BOT_USER}" python3 -m venv venv
fi

# Install Python packages inside venv
. venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Copy example config files if needed
if [ ! -f bot_config.json ]; then
  cp bot_config.json.example bot_config.json
  chown ${BOT_USER}:${BOT_USER} bot_config.json
fi

if [ ! -f admins.json ]; then
  cp admins.json.example admins.json
  chown ${BOT_USER}:${BOT_USER} admins.json
fi

# Create .env from example if not present
if [ ! -f .env ]; then
  cat > .env <<'ENV'
# Copy your real Telegram bot token below
TELEGRAM_BOT_TOKEN=
# Optional: configure other env vars here
ENV
  chown ${BOT_USER}:${BOT_USER} .env
  chmod 600 .env
fi

# Ensure ownership
chown -R ${BOT_USER}:${BOT_USER} "${APP_DIR}"

# Create systemd service
SERVICE_FILE=/etc/systemd/system/${SERVICE_NAME}.service
cat > "${SERVICE_FILE}" <<SERVICE
[Unit]
Description=VipPlay247 Telegram Bot
After=network.target

[Service]
Type=simple
User=${BOT_USER}
WorkingDirectory=${APP_DIR}
EnvironmentFile=${APP_DIR}/.env
ExecStart=${APP_DIR}/venv/bin/python ${APP_DIR}/bot_advanced.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE

# Reload systemd and enable service
systemctl daemon-reload
systemctl enable ${SERVICE_NAME}
systemctl restart ${SERVICE_NAME}

echo "Deployment complete. Use: systemctl status ${SERVICE_NAME} and journalctl -u ${SERVICE_NAME} -f"
