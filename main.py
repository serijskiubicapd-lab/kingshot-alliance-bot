import os
import discord
from discord.ext import tasks
from datetime import datetime, timedelta, timezone

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
ROLE_ID = int(os.getenv("ROLE_ID"))

BEAR_INTERVAL_HOURS = 36

# Set the LAST time Bear Hunt happened (UTC time!)
# Example: 2026-02-21 18:00 UTC
last_bear = datetime(2026, 2, 21, 18, 0, tzinfo=timezone.utc)

intents = discord.Intents.default()
bot = discord.Client(intents=intents)

@tasks.loop(minutes=5)
async def bear_check():
    global last_bear
    now = datetime.now(timezone.utc)
    next_bear = last_bear + timedelta(hours=BEAR_INTERVAL_HOURS)

    if now >= next_bear:
        channel = bot.get_channel(CHANNEL_ID)
        role = channel.guild.get_role(ROLE_ID)

        await channel.send(f"🐻 {role.mention} Bear Hunt is starting now!")

        last_bear = next_bear

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    bear_check.start()

bot.run(TOKEN)
