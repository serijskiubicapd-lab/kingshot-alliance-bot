import os
import discord
from discord.ext import tasks
from datetime import datetime, timezone

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
ROLE_ID = int(os.getenv("ROLE_ID"))
R2_ID = int(os.getenv("R2_ID"))
R3_ID = int(os.getenv("R3_ID"))
R4_ID = int(os.getenv("R4_ID"))

intents = discord.Intents.default()
bot = discord.Client(intents=intents)

last_sent = {}

async def send_message(message_key, message_text):
    global last_sent
    now = datetime.now(timezone.utc)
    minute_key = now.strftime("%Y-%m-%d %H:%M")

    if last_sent.get(message_key) != minute_key:
    channel = bot.get_channel(CHANNEL_ID)

    await channel.send(
        f"🐻 <@&{R2_ID}> <@&{R3_ID}> <@&{R4_ID}> {message_text}"
    )

    last_sent[message_key] = minute_key

@tasks.loop(seconds=30)
async def scheduler():
    now = datetime.now(timezone.utc)
    hour = now.hour
    minute = now.minute
    
    # Bear Hunt 1 (20:15 UTC)
    if hour == 20 and minute == 0:
        await send_message("bear1_15", "Bear Hunt 1 starts in 15 minutes (20:15 UTC)!")
    if hour == 20 and minute == 10:
        await send_message("bear1_5", "Bear Hunt 1 starts in 5 minutes (20:15 UTC)!")

    # Bear Hunt 2 (04:00 UTC)
    if hour == 3 and minute == 45:
        await send_message("bear2_15", "Bear Hunt 2 starts in 15 minutes (04:00 UTC)!")
    if hour == 3 and minute == 55:
        await send_message("bear2_5", "Bear Hunt 2 starts in 5 minutes (04:00 UTC)!")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    scheduler.start()

bot.run(TOKEN)
