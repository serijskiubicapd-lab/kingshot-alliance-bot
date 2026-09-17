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


# ============================================================
# 48-HOUR ROTATION
# ============================================================

# Every second day is a Bear Hunt day.
START_DATE = datetime(2026, 2, 24, tzinfo=timezone.utc)


# ============================================================
# BEAR TRAP TIMES (UTC)
# ============================================================

TRAP3_TIME = (2, 30)     # 02:30 UTC
TRAP2_TIME = (13, 0)     # 13:00 UTC
TRAP1_TIME = (20, 30)    # 20:30 UTC


BEARS = [
    ("trap3", TRAP3_TIME, "Bear Trap 3"),
    ("trap2", TRAP2_TIME, "Bear Trap 2"),
    ("trap1", TRAP1_TIME, "Bear Trap 1"),
]


# ============================================================
# DISCORD
# ============================================================

intents = discord.Intents.default()
bot = discord.Client(intents=intents)

last_sent = load_state()


# ============================================================
# SEND MESSAGE
# ============================================================

async def send_message(message_key, message_text):
    channel = bot.get_channel(CHANNEL_ID)

    if not channel:
        print("Channel not found!")
        return

    await channel.send(
        f"🐻 <@&{R2_ID}> <@&{R3_ID}> <@&{R4_ID}> {message_text}"
    )

# ============================================================
# ONE-TIME NEW BEAR TIMES ANNOUNCEMENT
# ============================================================

async def send_new_bear_times_announcement():
    message_key = "new_bear_times_announcement"

    # Don't send it again if it was already sent
    if last_sent.get(message_key):
        return

    message_text = (
        "**NEW BEAR TRAP TIMES**\n\n"
        "Starting with the next Bear Hunt, we have a new schedule:\n\n"
        "🥉 **Trap 3 — 02:30 UTC**\n"
        "📍 Takes place at the **\"KvK\" alliance**\n\n"
        "🥈 **Trap 2 — 13:00 UTC**\n\n"
        "🥇 **Trap 1 — 20:30 UTC**\n\n"
        "⚠️ **All three traps are on the same Bear day.**\n"
        "The usual **15-minute and 5-minute reminders** will continue.\n\n"
        "Please take note of the new times!"
    )

    await send_message(message_key, message_text)

    last_sent[message_key] = True
    save_state()
    
# ============================================================
# ALLIANCE CHAMPIONSHIP REGISTRATION
# ============================================================

async def check_weekly_registration(now):
    try:
        # Monday = 0, Tuesday = 1
        if now.weekday() not in [0, 1]:
            return

        # Check 00:00 window
        if not (now.hour == 0 and now.minute == 0):
            return

        event_id = now.strftime("%Y-%m-%d")

        message_key = "alliance_championship"

        if last_sent.get(message_key) == event_id:
            return

        message_text = (
            "**Alliance Championship - Registration**\n\n"
            "• Use your best 3 heroes (these should really be golds by now hopefully)\n"
            "• Register to the middle lane\n"
            "• Activate pet skills before registering\n"
            "• 50/20/30 formation"
        )

        await send_message(message_key, message_text)

        last_sent[message_key] = event_id
        save_state()

    except Exception as e:
        print(f"Weekly event error: {e}")


# ============================================================
# BEAR HUNT SCHEDULER
# ============================================================

@tasks.loop(seconds=30)
async def scheduler():

    try:
        now = datetime.now(timezone.utc)

        # Check weekly Alliance Championship registration
        await check_weekly_registration(now)


        # ----------------------------------------------------
        # DETERMINE IF TODAY IS A BEAR DAY
        # ----------------------------------------------------

        days_since = (now.date() - START_DATE.date()).days

        # Only run Bears every 2 days
        if days_since % 2 != 0:
            return


        # ----------------------------------------------------
        # CREATE ALL THREE TRAPS FOR TODAY
        # ----------------------------------------------------

        for key, time_tuple, label in BEARS:

            event_time = now.replace(
                hour=time_tuple[0],
                minute=time_tuple[1],
                second=0,
                microsecond=0
            )


            # ------------------------------------------------
            # 15 MINUTE REMINDER
            # ------------------------------------------------

            target_15 = event_time - timedelta(minutes=15)

            event_id = event_time.strftime("%Y-%m-%d %H:%M")

            message_key_15 = f"{key}_15"

            if target_15 <= now < target_15 + timedelta(minutes=5):

                if last_sent.get(message_key_15) != event_id:

                    await send_message(
                        message_key_15,
                        f"{label} starts in 15 minutes "
                        f"({time_tuple[0]:02d}:{time_tuple[1]:02d} UTC)!"
                    )

                    last_sent[message_key_15] = event_id
                    save_state()


            # ------------------------------------------------
            # 5 MINUTE REMINDER
            # ------------------------------------------------

            target_5 = event_time - timedelta(minutes=5)

            message_key_5 = f"{key}_5"

            if target_5 <= now < target_5 + timedelta(minutes=5):

                if last_sent.get(message_key_5) != event_id:

                    await send_message(
                        message_key_5,
                        f"{label} starts in 5 minutes "
                        f"({time_tuple[0]:02d}:{time_tuple[1]:02d} UTC)!"
                    )

                    last_sent[message_key_5] = event_id
                    save_state()


    except Exception as e:
        print(f"Scheduler error: {e}")


# ============================================================
# BOT READY
# ============================================================

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    await send_new_bear_times_announcement()

    if not scheduler.is_running():
        scheduler.start()


# ============================================================
# START BOT
# ============================================================

bot.run(TOKEN)
