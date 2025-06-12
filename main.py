import discord
from discord.ext import commands
import json
import os

# Load config
with open("config.json") as f:
    config = json.load(f)


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=config["prefix"], intents=intents)


# Load all cogs from the cogs folder
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")


@bot.event
async def on_ready():
    print(f"GigiBot is online as {bot.user}!")

@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong! GigiBot reporting for dad duty.")

bot.run(config["token"])
