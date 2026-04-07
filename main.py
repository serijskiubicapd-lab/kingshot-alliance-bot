import os
import discord
from discord.ext import tasks
from datetime import datetime, timezone, timedelta
import json

STATE_FILE = "state.json"

def load_state():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_state():
    with open(STATE_FILE, "w") as f:
        json.dump(last_sent, f, indent=4)

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
R2_ID = int(os.getenv("R2_ID"))
R3_ID = int(os.getenv("R3_ID"))
R4_ID = int(os.getenv("R4_ID"))

# 48-hour rotation anchor date (UTC)
START_DATE = datetime(2026, 2, 24, tzinfo=timezone.utc)
# Bear times (UTC)
BEAR1_TIME = (20, 15)
BEAR2_TIME = (3, 0)
BEARS = [
    ("bear1", BEAR1_TIME, "Bear Hunt 1"),
    ("bear2", BEAR2_TIME, "Bear Hunt 2"),
]

intents = discord.Intents.default()
bot = discord.Client(intents=intents)

last_sent = load_state()

async def send_message(message_key, message_text):
    channel = bot.get_channel(CHANNEL_ID)

    if not channel:
        print("Channel not found!")
        return

    await channel.send(
        f"🐻 <@&{R2_ID}> <@&{R3_ID}> <@&{R4_ID}> {message_text}"
    )

@tasks.loop(seconds=30)
async def scheduler():
    try:
        now = datetime.now(timezone.utc)
       
        # Calculate 48h rotation
        days_since = (now.date() - START_DATE.date()).days

        # Only run on valid Bear days (every 2 days)
        if days_since % 2 != 0:
            return
       
        # Process all bears
        for key, time_tuple, label in BEARS:

            event_time = now.replace(
                hour=time_tuple[0],
                minute=time_tuple[1],
                second=0,
                microsecond=0
            )
            
            if event_time < now:
                event_time += timedelta(days=2)

            target_15 = event_time - timedelta(minutes=15)
            target_5 = event_time - timedelta(minutes=5)

            event_id = event_time.strftime("%Y-%m-%d %H:%M")
            message_key_15 = f"{key}_15"

            if target_15 <= now < target_5:
                if last_sent.get(message_key_15) != event_id:
                    await send_message(
                        message_key_15,
                        f"{label} starts in 15 minutes ({time_tuple[0]:02d}:{time_tuple[1]:02d} UTC)!"
                    )
                    last_sent[message_key_15] = event_id
                    save_state()

            message_key_5 = f"{key}_5"

            if target_5 <= now < event_time:
                if last_sent.get(message_key_5) != event_id:
                    await send_message(
                        message_key_5,
                        f"{label} starts in 5 minutes ({time_tuple[0]:02d}:{time_tuple[1]:02d} UTC)!"
                    )
                    last_sent[message_key_5] = event_id
                    save_state()

    except Exception as e:
        print(f"Scheduler error: {e}") 
        
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    channel = bot.get_channel(CHANNEL_ID)

    if channel:
        await channel.send(
            "🐻 **Bear Hunt 1 Update**\n\n"
            "New time: **20:15 UTC**\n\n"
            "Bot reminders will adjust automatically — see you there!"
        )

    scheduler.start()
bot.run(TOKEN)
