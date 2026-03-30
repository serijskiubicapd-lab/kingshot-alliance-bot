import os
import discord
from discord.ext import tasks
from datetime import datetime, timezone, timedelta

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
R2_ID = int(os.getenv("R2_ID"))
R3_ID = int(os.getenv("R3_ID"))
R4_ID = int(os.getenv("R4_ID"))

# 48-hour rotation anchor date (UTC)
START_DATE = datetime(2026, 2, 24, tzinfo=timezone.utc)
# Bear times (UTC)
BEAR1_TIME = (19, 50)
BEAR2_TIME = (3, 0)

intents = discord.Intents.default()
bot = discord.Client(intents=intents)

last_sent = {}

async def send_message(message_key, message_text):
    global last_sent
    now = datetime.now(timezone.utc)
    minute_key = now.strftime("%Y-%m-%d %H:%M")

    if last_sent.get(message_key) != minute_key:
        channel = bot.get_channel(CHANNEL_ID)

        if not channel:
            print("Channel not found!")
            return

        await channel.send(
            f"🐻 <@&{R2_ID}> <@&{R3_ID}> <@&{R4_ID}> {message_text}"
        )

        last_sent[message_key] = minute_key

@tasks.loop(seconds=30)
async def scheduler():
    now = datetime.now(timezone.utc)
    hour = now.hour
    minute = now.minute

    # Calculate 48h rotation
    days_since = (now.date() - START_DATE.date()).days

    # Only run on valid Bear days (every 2 days)
    if days_since % 2 != 0:
        return

    # Bear Hunt 1
    b1_time = now.replace(hour=BEAR1_TIME[0], minute=BEAR1_TIME[1], second=0, microsecond=0)

    b1_target_15 = b1_time - timedelta(minutes=15)
    b1_target_5 = b1_time - timedelta(minutes=5)

    if abs((now - b1_target_15).total_seconds()) < 60:
        await send_message("bear1_15", f"Bear Hunt 1 starts in 15 minutes ({BEAR1_TIME[0]:02d}:{BEAR1_TIME[1]:02d} UTC)!")

    if abs((now - b1_target_5).total_seconds()) < 60:
        await send_message("bear1_5", f"Bear Hunt 1 starts in 5 minutes ({BEAR1_TIME[0]:02d}:{BEAR1_TIME[1]:02d} UTC)!")

    # Bear Hunt 2
    b2_time = now.replace(hour=BEAR2_TIME[0], minute=BEAR2_TIME[1], second=0, microsecond=0)

    b2_target_15 = b2_time - timedelta(minutes=15)
    b2_target_5 = b2_time - timedelta(minutes=5)

    if abs((now - b2_target_15).total_seconds()) < 60:
        await send_message("bear2_15", f"Bear Hunt 2 starts in 15 minutes ({BEAR2_TIME[0]:02d}:{BEAR2_TIME[1]:02d} UTC)!")

    if abs((now - b2_target_5).total_seconds()) < 60:
        await send_message("bear2_5", f"Bear Hunt 2 starts in 5 minutes ({BEAR2_TIME[0]:02d}:{BEAR2_TIME[1]:02d} UTC)!")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    scheduler.start()
bot.run(TOKEN)
