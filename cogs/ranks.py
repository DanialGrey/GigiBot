import discord
from discord.ext import commands
import json
import os
import random
from dotenv import load_dotenv

load_dotenv()  # Load .env variables

LEVEL_UP_CHANNEL = os.getenv("LEVEL_UP_CHANNEL", "ranks")

DATA_FILE = "data/ranks_data.json"

# Define XP thresholds and roles (level index: (XP needed, role name))
LEVELS = [
    (0, "Newbie Builder"),
    (150, "Junior Engineer"),
    (350, "Craftsman"),
    (600, "Cozy Crafter"),
    (900, "Assembly Apprentice"),
    (1300, "Factory Foreman"),
    (1800, "Production Prodigy"),
    (2400, "Automation Ace"),
    (3100, "Master Machinist"),
    (3900, "Industrial Innovator"),
    (4800, "Engineer Extraordinaire"),
    (5800, "Logistics Legend"),
    (6900, "Build Baroness"),
    (8100, "Conveyor Commander"),
    (9400, "Overclocking Overlord"),
]

class RankCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.xp_cooldown = {}  # Tracks last XP gain timestamp per user per guild
        self.level_up_channel_name = LEVEL_UP_CHANNEL

        # Ensure data directory exists
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        if not os.path.exists(DATA_FILE):
            with open(DATA_FILE, "w") as f:
                json.dump({}, f)

    def load_data(self):
        with open(DATA_FILE, "r") as f:
            return json.load(f)

    def save_data(self, data):
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        # Ignore messages shorter than 10 chars and commands (starting with prefix)
        prefix = os.getenv("PREFIX", "!")
        if len(message.content) < 10 or message.content.startswith(prefix):
            return

        user_id = str(message.author.id)
        guild_id = str(message.guild.id)
        key = f"{guild_id}-{user_id}"

        now = message.created_at.timestamp()
        last_xp_time = self.xp_cooldown.get(key, 0)

        # Only grant XP if 5 minutes have passed since last XP
        if now - last_xp_time < 300:
            return

        self.xp_cooldown[key] = now

        # Load data
        data = self.load_data()
        if guild_id not in data:
            data[guild_id] = {}
        if user_id not in data[guild_id]:
            data[guild_id][user_id] = {"xp": 0, "level": 0}

        user_data = data[guild_id][user_id]

        # Grant random XP between 5 and 15
        xp_gain = random.randint(5, 15)
        user_data["xp"] += xp_gain

        # Check for level up
        current_level_index = user_data["level"]
        new_level_index = current_level_index

        for i, (xp_req, role_name) in enumerate(LEVELS):
            if user_data["xp"] >= xp_req:
                new_level_index = i
            else:
                break

        if new_level_index > current_level_index:
            user_data["level"] = new_level_index
            new_level_name = LEVELS[new_level_index][1]

            # Assign new role
            role = discord.utils.get(message.guild.roles, name=new_level_name)
            if role and role not in message.author.roles:
                try:
                    await message.author.add_roles(role)
                except discord.Forbidden:
                    print(f"Missing permissions to add role {new_level_name} to {message.author}")

            # Send level-up notification to configured channel
            ranks_channel = discord.utils.get(message.guild.text_channels, name=self.level_up_channel_name)
            level_up_message = f"🎉 {message.author.mention} leveled up to **{new_level_name}**!"
            if ranks_channel:
                await ranks_channel.send(level_up_message)
            else:
                await message.channel.send(level_up_message)

        self.save_data(data)

    @commands.command(name="rank")
    async def rank(self, ctx, member: discord.Member = None):
        """Shows the rank and XP of a user."""

        if not member:
            member = ctx.author

        guild_id = str(ctx.guild.id)
        user_id = str(member.id)

        data = self.load_data()
        if guild_id not in data or user_id not in data[guild_id]:
            await ctx.send(f"{member.display_name} has no XP recorded yet.")
            return

        user_data = data[guild_id][user_id]
        xp = user_data["xp"]
        level_index = user_data["level"]
        level_name = LEVELS[level_index][1]

        # Compute leaderboard rank
        guild_data = data[guild_id]
        sorted_users = sorted(guild_data.items(), key=lambda item: item[1]["xp"], reverse=True)
        rank_position = next((idx for idx, item in enumerate(sorted_users, start=1) if item[0] == user_id), None)

        embed = discord.Embed(title=f"{member.display_name}'s Rank",
                              color=discord.Color.blue())
        embed.add_field(name="Level", value=f"{level_index} - {level_name}", inline=False)
        embed.add_field(name="XP", value=str(xp), inline=False)
        if rank_position:
            embed.add_field(name="Leaderboard Position", value=f"#{rank_position}", inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="leaderboard")
    async def leaderboard(self, ctx):
        """Shows the XP leaderboard for this server."""

        guild_id = str(ctx.guild.id)
        data = self.load_data()

        if guild_id not in data or not data[guild_id]:
            await ctx.send("No XP data available for this server yet.")
            return

        guild_data = data[guild_id]

        # Sort users by XP descending
        sorted_users = sorted(guild_data.items(), key=lambda item: item[1]["xp"], reverse=True)

        embed = discord.Embed(title=f"{ctx.guild.name} XP Leaderboard",
                              color=discord.Color.gold())

        # Show top 10 users
        for rank, (user_id, user_data) in enumerate(sorted_users[:10], start=1):
            member = ctx.guild.get_member(int(user_id))
            if member:
                embed.add_field(name=f"#{rank} - {member.display_name}",
                                value=f"Level {user_data['level']} - {LEVELS[user_data['level']][1]} | XP: {user_data['xp']}",
                                inline=False)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(RankCog(bot))
