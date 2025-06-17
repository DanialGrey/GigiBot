# cogs/polls.py

import discord
from discord.ext import commands
import asyncio

class Polls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    print("[Polls] Cog loaded.")

    @commands.command(name="poll")
    @commands.has_any_role("Moderator", "Apex")
    async def create_poll(self, ctx):
        """Creates a multiple-choice poll (up to 10 options)"""

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        # ✅ Delete the original command message
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            print("⚠️ Missing permission to delete messages.")
        except Exception as e:
            print(f"⚠️ Failed to delete command message: {e}")

        # Ask for the poll question
        prompt1 = await ctx.send("🗳 What is the poll question?")
        try:
            question_msg = await self.bot.wait_for("message", check=check, timeout=60)
            question = question_msg.content
        except asyncio.TimeoutError:
            await ctx.send("⏰ Timed out. Try starting the poll again.")
            return
        await prompt1.delete()
        await question_msg.delete()

        # Ask for poll options
        prompt2 = await ctx.send(
            "🔢 Enter the poll options, separated by a `|`. (Max 10 options)\nExample: `Option A | Option B | Option C`")
        try:
            options_msg = await self.bot.wait_for("message", check=check, timeout=60)
            options = [opt.strip() for opt in options_msg.content.split("|") if opt.strip()]
        except asyncio.TimeoutError:
            await ctx.send("⏰ Timed out. Try starting the poll again.")
            return
        await prompt2.delete()
        await options_msg.delete()

        if len(options) == 0:
            options = ["Yes", "No"]

        if len(options) > 10:
            await ctx.send("❌ You can only have up to 10 options.")
            return

        emoji_map = ["🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭", "🇮", "🇯"]
        description = "\n".join(f"{emoji_map[i]} {option}" for i, option in enumerate(options))

        embed = discord.Embed(
            title=f"📊 {question}",
            description=description,
            color=discord.Color.dark_blue()
        )
        embed.set_footer(text=f"Poll started by {ctx.author.display_name}")

        # ✅ Mention @everyone when sending the poll
        poll_msg = await ctx.send(content="@everyone", embed=embed)

        for i in range(len(options)):
            await poll_msg.add_reaction(emoji_map[i])

    @create_poll.error
    async def poll_error(self, ctx, error):
        if isinstance(error, commands.MissingAnyRole):
            await ctx.send("🚫 You need the **Moderator** or **Apex** role to start a poll.")

async def setup(bot):
    await bot.add_cog(Polls(bot))
