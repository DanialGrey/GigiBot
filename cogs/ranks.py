import discord
from discord.ext import commands
import json
import os
import random
from dotenv import load_dotenv
import asyncio  # Added for async sleep

load_dotenv()  # Load .env variables

LEVEL_UP_CHANNEL = os.getenv("LEVEL_UP_CHANNEL", "ranks")
MOD_LOG_CHANNEL = os.getenv("MOD_LOG_CHANNEL", "mod-log")
DATA_FILE = "data/ranks_data.json"
XP_COOLDOWN_FILE = "data/xp_cooldown.json"
LEVELS_FILE = "data/levels.json"

# Updated LEVELS list based on the new role names
LEVELS = [
    (0, "WorkshopIntern"),
    (150, "JuniorEngineer"),
    (350, "CozyCrafter"),
    (600, "ResourceWrangler"),
    (900, "FactoryForeman"),
    (1300, "ScrapSpecialist"),
    (1800, "BlueprintBuff"),
    (2400, "MechanicMaestro"),
    (3100, "AutomationAlchemist"),
    (3900, "BuildBanshee"),
    (4800, "LootGoblin"),
    (5800, "MythicModuleMaster"),
    (6900, "ArchitectofEfficiency"),
    (8100, "DadcoreOverlord"),
    (9400, "EternalFabricator"),
]

# Load levels from the levels JSON file (if you still want to use a file for flexibility)
def load_levels():
    if os.path.exists(LEVELS_FILE):
        with open(LEVELS_FILE, "r") as f:
            return json.load(f)
    else:
        # Save to a JSON file if it doesn't exist
        with open(LEVELS_FILE, "w") as f:
            json.dump(LEVELS, f, indent=4)
        return LEVELS

class RankCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.xp_cooldown = self.load_xp_cooldown()  # Load cooldown from file
        self.level_up_channel_name = LEVEL_UP_CHANNEL
        print("[Ranks] Cog loaded.")

        # Ensure data directory exists
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        if not os.path.exists(DATA_FILE):
            with open(DATA_FILE, "w") as f:
                json.dump({}, f)

    def load_xp_cooldown(self):
        """Load XP cooldown data from JSON."""
        if os.path.exists(XP_COOLDOWN_FILE):
            with open(XP_COOLDOWN_FILE, "r") as f:
                return json.load(f)
        return {}

    def save_xp_cooldown(self):
        """Save XP cooldown data to JSON."""
        with open(XP_COOLDOWN_FILE, "w") as f:
            json.dump(self.xp_cooldown, f, indent=4)

    def load_data(self):
        """Load the rank data."""
        with open(DATA_FILE, "r") as f:
            return json.load(f)

    def save_data(self, data):
        """Save the rank data."""
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)

    @commands.Cog.listener()
    async def on_ready(self):
        """Check that everyone has the correct role on startup."""
        print("Bot is ready! Checking all members' roles...")

        # Wait for a brief moment to allow all members to load before proceeding
        await asyncio.sleep(5)  # Delay for 5 seconds, you can adjust this as needed

        for guild in self.bot.guilds:
            data = self.load_data()
            guild_id = str(guild.id)
            if guild_id not in data:
                continue

            # Iterate through all members of the server
            for member in guild.members:
                user_id = str(member.id)
                if user_id in data[guild_id]:
                    user_data = data[guild_id][user_id]
                    current_level = user_data["level"]
                    current_level_name = LEVELS[current_level][1]  # Get the role name based on the current level

                    # Check if the user has the correct role
                    role = discord.utils.get(guild.roles, name=current_level_name)
                    if role:
                        if role not in member.roles:
                            # If the user doesn't have the correct role, assign it
                            try:
                                await member.add_roles(role)
                                # Remove the old role corresponding to the previous level
                                old_level_name = LEVELS[user_data["level"]][1]
                                old_role = discord.utils.get(guild.roles, name=old_level_name)
                                if old_role in member.roles:
                                    await member.remove_roles(old_role)
                            except discord.Forbidden:
                                print(f"Missing permissions to modify roles for {member.display_name} in {guild.name}")
                    else:
                        # Role does not exist, create it and assign it
                        try:
                            role = await guild.create_role(name=current_level_name)
                            await member.add_roles(role)
                            old_level_name = LEVELS[user_data["level"]][1]
                            old_role = discord.utils.get(guild.roles, name=old_level_name)
                            if old_role in member.roles:
                                await member.remove_roles(old_role)
                        except discord.Forbidden:
                            print(f"Missing permissions to create or modify roles for {member.display_name} in {guild.name}")

        print("Role verification completed for all members.")

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
        self.save_xp_cooldown()

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

            # Assign new role or create dynamically if not found
            role = discord.utils.get(message.guild.roles, name=new_level_name)
            if role:
                # Remove the old role corresponding to the previous level
                old_level_name = LEVELS[current_level_index][1]
                old_role = discord.utils.get(message.guild.roles, name=old_level_name)
                if old_role in message.author.roles:
                    try:
                        await message.author.remove_roles(old_role)
                    except discord.Forbidden:
                        print(f"Missing permissions to remove role {old_level_name} from {message.author}")

                # Add the new role
                try:
                    await message.author.add_roles(role)
                except discord.Forbidden:
                    print(f"Missing permissions to add role {new_level_name} to {message.author}")
            else:
                try:
                    role = await message.guild.create_role(name=new_level_name)
                    # Remove the old role
                    old_level_name = LEVELS[current_level_index][1]
                    old_role = discord.utils.get(message.guild.roles, name=old_level_name)
                    if old_role in message.author.roles:
                        await message.author.remove_roles(old_role)
                    # Add the new role
                    await message.author.add_roles(role)
                except discord.Forbidden:
                    print(f"Missing permissions to create role {new_level_name} for {message.author}")

            # Send level-up notification to configured channel
            ranks_channel = discord.utils.get(message.guild.text_channels, name=self.level_up_channel_name)
            level_up_message = f"🎉 {message.author.mention} leveled up to **{new_level_name}**!"
            if ranks_channel:
                try:
                    await ranks_channel.send(level_up_message)
                except discord.Forbidden:
                    print(f"Missing permissions to send message to {self.level_up_channel_name}")
                    mod_log_channel = discord.utils.get(message.guild.text_channels, name=MOD_LOG_CHANNEL)
                    if mod_log_channel:
                        await mod_log_channel.send(f"⚠️ Unable to send level-up message to {self.level_up_channel_name} for {message.author.mention}.")
            else:
                print(f"Channel {self.level_up_channel_name} does not exist.")

        self.save_data(data)

    @commands.command(name="rank")
    async def rank(self, ctx, member: discord.Member = None):
        """Shows the rank and XP of a user."""

        # ✅ Delete the original command message
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            print("⚠️ Missing permission to delete messages.")
        except Exception as e:
            print(f"⚠️ Failed to delete command message: {e}")

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
    async def leaderboard(self, ctx, page: int = 1):
        """Shows the XP leaderboard for this server with pagination (interactive buttons)."""

        guild_id = str(ctx.guild.id)
        data = self.load_data()

        if guild_id not in data or not data[guild_id]:
            await ctx.send("No XP data available for this server yet.")
            return

        guild_data = data[guild_id]

        # Sort users by XP descending
        sorted_users = sorted(guild_data.items(), key=lambda item: item[1]["xp"], reverse=True)

        # Pagination (10 entries per page)
        start_index = (page - 1) * 10
        end_index = start_index + 10
        users_to_show = sorted_users[start_index:end_index]

        if not users_to_show:
            await ctx.send(f"No users found on page {page}.")
            return

        embed = discord.Embed(title=f"{ctx.guild.name} XP Leaderboard (Page {page})",
                              color=discord.Color.gold())

        # Show users for the current page
        for rank, (user_id, user_data) in enumerate(users_to_show, start=start_index + 1):
            member = ctx.guild.get_member(int(user_id))
            if member:
                embed.add_field(name=f"#{rank} - {member.display_name}",
                                value=f"Level {user_data['level']} - {LEVELS[user_data['level']][1]} | XP: {user_data['xp']}",
                                inline=False)

        # Buttons for pagination
        class PaginationView(View):
            def __init__(self, page, total_pages):
                super().__init__()
                self.page = page
                self.total_pages = total_pages

            @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary)
            async def previous_button(self, button: discord.ui.Button, interaction: discord.Interaction):
                if self.page > 1:
                    self.page -= 1
                    await self.update_page(interaction)

            @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
            async def next_button(self, button: discord.ui.Button, interaction: discord.Interaction):
                if self.page < self.total_pages:
                    self.page += 1
                    await self.update_page(interaction)

            async def update_page(self, interaction):
                # Update embed message for the new page
                await interaction.response.edit_message(embed=embed, view=self)

        total_pages = (len(sorted_users) // 10) + (1 if len(sorted_users) % 10 else 0)

        view = PaginationView(page, total_pages)

        # Send the embed message with pagination buttons
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(RankCog(bot))
