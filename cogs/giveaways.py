# cogs/giveaways.py

import discord
from discord.ext import commands
import asyncio
import random

class Giveaways(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="giveaway")
    @commands.has_role("Giveaways")
    async def start_giveaway(self, ctx):
        """Starts a giveaway if user has the Giveaways role"""
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        await ctx.send("🎁 What is the prize?")
        try:
            prize_msg = await self.bot.wait_for("message", check=check, timeout=30)
            prize = prize_msg.content
        except asyncio.TimeoutError:
            await ctx.send("⏰ Timed out. No giveaway today!")
            return

        await ctx.send("⏳ How long should the giveaway run? (in **seconds**, for now)")
        try:
            time_msg = await self.bot.wait_for("message", check=check, timeout=30)
            duration = int(time_msg.content)
        except asyncio.TimeoutError:
            await ctx.send("⏰ Timed out. No giveaway today!")
            return
        except ValueError:
            await ctx.send("❌ That's not a valid number of seconds.")
            return

        embed = discord.Embed(
            title="🎉 Giveaway Time!",
            description=f"Prize: **{prize}**\nReact with ✅ to enter!\nEnds in {duration} seconds.",
            color=discord.Color.blue()
        )
        giveaway_msg = await ctx.send(embed=embed)
        await giveaway_msg.add_reaction("✅")

        await asyncio.sleep(duration)

        updated_msg = await ctx.channel.fetch_message(giveaway_msg.id)
        users = await updated_msg.reactions[0].users().flatten()
        users = [u for u in users if not u.bot]

        if not users:
            await ctx.send("😢 No one entered the giveaway.")
            return

        winner = random.choice(users)
        await ctx.send(f"🥳 Congratulations {winner.mention}! You just won **{prize}** — 100% dad-approved!")

    @start_giveaway.error
    async def giveaway_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            await ctx.send("🚫 Sorry, you need the **Giveaways** role to start a giveaway.")

async def setup(bot):
    await bot.add_cog(Giveaways(bot))
