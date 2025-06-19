import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio

# Load environment variables from .env file
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("DISCORD_PREFIX", "!")
MOD_LOG_CHANNEL = os.getenv("MOD_LOG_CHANNEL")
ANNOUNCEMENT_CHANNEL = os.getenv("ANNOUNCEMENT_CHANNEL")

# Check that the bot token is actually set
if not TOKEN:
    raise ValueError("❌ DISCORD_TOKEN is not set in the .env file.")

# Set up full intents
intents = discord.Intents.all()

# Initialize bot
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

#Print bot status to command line
@bot.event
async def on_ready():
    print(f"{bot.user.name} is online and ready!")

# Load all cogs from the /cogs directory
async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
            except Exception as e:
                print(f"❌ Failed to load {filename}: {e}")

# Main entry point
async def main():
    await load_cogs()
    await bot.start(TOKEN)

asyncio.run(main())
