import asyncio
import os
import json
from types import SimpleNamespace
from datetime import datetime, timedelta

# Minimal fake Bot implementation to intercept API calls
class FakeBot:
    async def approve_chat_join_request(self, chat_id, user_id):
        print(f"[FakeBot] approve_chat_join_request(chat_id={chat_id}, user_id={user_id})")
        return True

    async def send_message(self, chat_id, text, reply_markup=None):
        print(f"[FakeBot] send_message(to={chat_id}): {text[:80]!r}")
        return True

    async def send_document(self, chat_id, document, caption=None):
        print(f"[FakeBot] send_document(to={chat_id}): {document} caption={caption!r}")
        return True

# Helpers for building fake updates/contexts
def fake_update_for_join(chat_id, user_id, username, first_name, date_iso):
    from_user = SimpleNamespace(id=user_id, username=username, first_name=first_name, last_name=None)
    chat = SimpleNamespace(id=chat_id)
    join_request = SimpleNamespace(chat=chat, from_user=from_user, date=date_iso)
    return SimpleNamespace(chat_join_request=join_request)

class FakeMessage:
    def __init__(self):
        pass
    async def reply_text(self, text):
        print(f"[FakeMessage.reply_text] {text}")

class FakeUpdateForAdmin:
    def __init__(self, admin_id):
        self.effective_user = SimpleNamespace(id=admin_id)
        self.message = FakeMessage()

class FakeContext:
    def __init__(self, args=None):
        self.args = args or []
        self.bot = FakeBot()

async def run_simulation():
    # Ensure working directory is repo root
    repo_root = os.path.dirname(__file__)
    os.chdir(repo_root)

    # Prepare a VipPlay247Bot instance
    from bot_advanced import VipPlay247Bot

    # Use a dummy token; Application is built with job_queue=None inside the bot code
    bot = VipPlay247Bot(token="TEST_TOKEN_FOR_SIM")

    # Make sure admins.json contains our admin
    admin_id = 1399652619
    with open('admins.json', 'w', encoding='utf-8') as f:
        json.dump([admin_id], f)

    # Prepare bot_config if missing
    if not os.path.exists('bot_config.json'):
        try:
            with open('bot_config.json.example', 'r', encoding='utf-8') as s, open('bot_config.json', 'w', encoding='utf-8') as d:
                d.write(s.read())
        except Exception:
            pass

    # Simulate several join requests on different dates
    base_chat_id = -1001234567890
    now = datetime.now()

    simulated = [
        # Old date
        (base_chat_id, 1111, 'user_old', 'OldName', (now - timedelta(days=10)).isoformat()),
        # Today's date
        (base_chat_id, 2222, 'user_today1', 'TodayOne', now.isoformat()),
        (base_chat_id, 3333, 'user_today2', 'TodayTwo', now.isoformat()),
        # Another date
        (base_chat_id, 4444, 'user_mid', 'MidName', (now - timedelta(days=3)).isoformat()),
    ]

    # Feed join requests into bot
    for chat_id, uid, uname, fname, date_iso in simulated:
        upd = fake_update_for_join(chat_id, uid, uname, fname, date_iso)
        ctx = FakeContext()
        # call handler
        await bot.handle_join_request(upd, ctx)

    print('\n== Pending requests after simulation ==')
    for r in bot.pending_requests:
        print(r)

    # Create admin update/context
    admin_update = FakeUpdateForAdmin(admin_id)

    # Test /accept 2
    print('\n== Testing: /accept 2 ==')
    ctx_accept = FakeContext(args=['2'])
    await bot.accept_requests_command(admin_update, ctx_accept)

    print('\n== Pending after /accept 2 ==')
    for r in bot.pending_requests:
        print(r)

    # Test /accept date <today>
    target_date = now.date().isoformat()
    print(f"\n== Testing: /accept date {target_date} ==")
    ctx_accept_date = FakeContext(args=['date', target_date])
    await bot.accept_requests_command(admin_update, ctx_accept_date)

    print('\n== Pending after /accept date ==')
    for r in bot.pending_requests:
        print(r)

    # Test /accept range (include old and mid)
    start = (now - timedelta(days=11)).date().isoformat()
    end = (now - timedelta(days=2)).date().isoformat()
    print(f"\n== Testing: /accept range {start} {end} ==")
    ctx_accept_range = FakeContext(args=['range', start, end])
    await bot.accept_requests_command(admin_update, ctx_accept_range)

    print('\n== Pending after /accept range ==')
    for r in bot.pending_requests:
        print(r)

    # Test /accept all to clear remaining
    print('\n== Testing: /accept all ==')
    ctx_accept_all = FakeContext(args=['all'])
    await bot.accept_requests_command(admin_update, ctx_accept_all)

    print('\n== Final users.json preview ==')
    if os.path.exists('users.json'):
        with open('users.json', 'r', encoding='utf-8') as f:
            users = json.load(f)
        # print a compact summary
        for uid, data in users.items():
            print(uid, data.get('status'), data.get('join_date')[:19] if data.get('join_date') else None)
    else:
        print('users.json not found')

if __name__ == '__main__':
    asyncio.run(run_simulation())
