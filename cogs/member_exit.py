import discord
from discord.ext import commands
import random
import json
import logging
import os
from dotenv import load_dotenv


class MemberExit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("[MemberExit] Cog loaded.")

        # Load environment variables
        load_dotenv()

        # Get the channel ID from the .env file (as an integer)
        self.exit_channel_id = int(os.getenv("EXIT_CHANNEL_ID", "123456789012345678"))

        # Load farewell messages from the "data" folder
        with open("data/farewell_messages.json", "r") as f:
            self.exit_messages = json.load(f)

        # Set up logging
        logging.basicConfig(level=logging.WARNING)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        # Attempt to get the dynamic exit channel by ID
        channel = self.bot.get_channel(self.exit_channel_id)
        if not channel:
            logging.warning(f"Campfire channel with ID '{self.exit_channel_id}' not found for {member.display_name}")
            return

        # Choose a random message and send it
        farewell = random.choice(self.exit_messages).format(member=member.display_name)
        await channel.send(farewell)


async def setup(bot):
    await bot.add_cog(MemberExit(bot))
