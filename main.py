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


intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user.name} is online and ready!")

async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
            except Exception as e:
                print(f"❌ Failed to load {filename}: {e}")

async def main():
    await load_cogs()
    await bot.start(TOKEN)

asyncio.run(main())
