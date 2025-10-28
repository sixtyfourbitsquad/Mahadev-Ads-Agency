Quick server deploy steps (run on the target server as root or a user with sudo):

1) SSH to server

   ssh root@206.189.134.0

2) Run deploy script bundled in this repo (recommended)

   # as root in the repo directory (if you pushed the repo to server)
   bash deploy.sh

   # OR clone and run directly
   git clone https://github.com/sixtyfourbitsquad/Mahadev-Ads-Agency.git /home/vipplay247/vipplay247-bot
   cd /home/vipplay247/vipplay247-bot
   bash deploy.sh

3) After deploy, edit /home/vipplay247/vipplay247-bot/.env and set TELEGRAM_BOT_TOKEN and any other settings. Also edit admins.json to include your admin id(s).

4) Manage service

   systemctl status vipplay247-bot
   journalctl -u vipplay247-bot -f
   systemctl restart vipplay247-bot

Notes & security
- The deploy script creates a dedicated user `vipplay247` and runs the bot as that user.
- Keep your .env out of version control. Do not commit your bot token.
- If you prefer a different user or path, edit `deploy.sh` accordingly.
