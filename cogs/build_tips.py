import discord
from discord.ext import commands, tasks
import random
import re
import json
import os
import asyncio
from datetime import datetime, timedelta
import pytz

class BuildTips(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("[BuildTips] Cog loaded.")

        self.tips = self.load_tips()

        self.theme_emojis = {
            "automation": "⚙️",
            "base_building": "🏗️",
            "storage": "📦",
            "aesthetics": "🎨",
            "motivation": "💪"
        }

        self.daily_tip_channel_id = int(os.getenv("DAILY_TIP_CHANNEL_ID", 0))
        self.daily_tip_task.start()

    def normalize_theme(self, theme):
        return re.sub(r'[^a-z]', '', theme.lower())

    def load_tips(self):
        try:
            path = os.path.join("data", "build_tips.json")
            with open(path, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            print(f"❌ Failed to load build tips: {e}")
            return {}

    @commands.command(name="buildtip")
    async def build_tip(self, ctx, theme: str = None):
        """Get a random building or motivational tip. Optionally specify a theme: automation, base_building, storage, aesthetics, motivation"""
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            print("⚠️ Missing permission to delete messages.")
        except Exception as e:
            print(f"⚠️ Failed to delete command message: {e}")

        normalized_themes = {self.normalize_theme(k): k for k in self.tips.keys()}

        if theme:
            key = self.normalize_theme(theme)
            if key in normalized_themes:
                real_theme = normalized_themes[key]
                tip = random.choice(self.tips[real_theme])
                emoji = self.theme_emojis.get(real_theme, "💡")
                await ctx.send(f"{emoji} **{real_theme.title()} Tip:** {tip}")
                return

        random_theme = random.choice(list(self.tips.keys()))
        tip = random.choice(self.tips[random_theme])
        emoji = self.theme_emojis.get(random_theme, "💡")
        await ctx.send(f"{emoji} **{random_theme.title()} Tip:** {tip}")

    @tasks.loop(hours=24)
    async def daily_tip_task(self):
        # Wait until 10 AM PST before sending
        now = datetime.now(pytz.timezone("US/Pacific"))
        target = now.replace(hour=10, minute=0, second=0, microsecond=0)
        if now > target:
            target += timedelta(days=1)
        wait_time = (target - now).total_seconds()
        print(f"[BuildTips] Waiting {wait_time / 60:.2f} minutes to post daily tip.")
        await asyncio.sleep(wait_time)

        channel = self.bot.get_channel(self.daily_tip_channel_id)
        if not channel:
            print(f"⚠️ Could not find daily tip channel with ID {self.daily_tip_channel_id}")
            return

        theme = random.choice(list(self.tips.keys()))
        tip = random.choice(self.tips[theme])
        emoji = self.theme_emojis.get(theme, "💡")

        await channel.send(f"{emoji} **Dad’s {theme.title()} Tip of the Day:**\n> {tip}")

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.daily_tip_task.is_running():
            self.daily_tip_task.start()


async def setup(bot):
    await bot.add_cog(BuildTips(bot))
