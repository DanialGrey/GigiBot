# cogs/giveaways.py

import discord
from discord.ext import commands
import asyncio
import random
import os
from dotenv import load_dotenv
import datetime
import time

load_dotenv()

GIVEAWAY_CHANNEL_ID = int(os.getenv("GIVEAWAY_CHANNEL_ID", 0))
GIVEAWAY_LOG_CHANNEL_ID = int(os.getenv("GIVEAWAY_LOG_CHANNEL_ID", 0))

def parse_duration(input_str):
    """Parses a time string like '10s', '5m', '2h', or '1d' into seconds."""
    try:
        return int(input_str)
    except ValueError:
        units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        unit = input_str[-1]
        num = input_str[:-1]
        if unit in units and num.isdigit():
            return int(num) * units[unit]
    return None

class Giveaways(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("[Giveaways] Cog loaded.")

    @commands.command(name="giveaway")
    @commands.has_role("Giveaways")
    async def start_giveaway(self, ctx):
        if ctx.channel.id != GIVEAWAY_CHANNEL_ID:
            await ctx.send("🚫 This command can only be used in the designated **#giveaways** channel.")
            return

        try:
            await ctx.message.delete()
        except discord.Forbidden:
            print("[Giveaway] Couldn't delete command message.")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        # Ask for prize
        prize_prompt = await ctx.send("🎁 What is the prize? *(Type `cancel` to stop)*")
        try:
            prize_msg = await self.bot.wait_for("message", check=check, timeout=30)
            prize = prize_msg.content.strip()
            if prize.lower() == "cancel":
                await ctx.send("❌ Giveaway cancelled.")
                await prize_prompt.delete()
                await prize_msg.delete()
                return
        except asyncio.TimeoutError:
            await ctx.send("⏰ Timed out. No giveaway today!")
            await prize_prompt.delete()
            return

        # Ask for duration
        duration_prompt = await ctx.send("⏳ How long should the giveaway run? *(e.g. 30s, 5m, 1h — or `cancel`)*")
        try:
            time_msg = await self.bot.wait_for("message", check=check, timeout=30)
            time_input = time_msg.content.strip()
            if time_input.lower() == "cancel":
                await ctx.send("❌ Giveaway cancelled.")
                await prize_prompt.delete()
                await prize_msg.delete()
                await duration_prompt.delete()
                await time_msg.delete()
                return

            duration = parse_duration(time_input)
            if duration is None:
                await ctx.send("❌ Invalid time format. Use `10s`, `5m`, `1h`, etc.")
                await prize_prompt.delete()
                await prize_msg.delete()
                await duration_prompt.delete()
                await time_msg.delete()
                return
        except asyncio.TimeoutError:
            await ctx.send("⏰ Timed out. No giveaway today!")
            await prize_prompt.delete()
            await prize_msg.delete()
            await duration_prompt.delete()
            return

        # Clean up setup messages
        try:
            await prize_prompt.delete()
            await prize_msg.delete()
            await duration_prompt.delete()
            await time_msg.delete()
        except discord.Forbidden:
            print("[Giveaway] Failed to delete some setup messages.")

        # Create giveaway embed
        end_timestamp = int(time.time()) + duration
        embed = discord.Embed(
            title="🎉 Giveaway Time!",
            description=(
                f"**Prize:** {prize}\n"
                f"React with ✅ to enter!\n"
                f"Ends <t:{end_timestamp}:R>."
            ),
            color=discord.Color.from_str("#f57ef3")
        )

        giveaway_msg = await ctx.send(embed=embed)
        await giveaway_msg.add_reaction("✅")
        print(f"[Giveaway] Started giveaway for '{prize}' lasting {duration}s.")

        # Log to mod channel
        log_channel = self.bot.get_channel(GIVEAWAY_LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(f"📢 Giveaway started in <#{ctx.channel.id}> for **{prize}**, ends <t:{end_timestamp}:R>.")

        await asyncio.sleep(duration)

        updated_msg = await ctx.channel.fetch_message(giveaway_msg.id)
        await asyncio.sleep(2)

        reaction = discord.utils.get(updated_msg.reactions, emoji="✅")
        if not reaction:
            await ctx.send("😢 No one entered the giveaway.")
            return

        users = [user async for user in reaction.users() if not user.bot]

        if not users:
            await ctx.send("😢 No one entered the giveaway.")
            return

        winner = random.choice(users)
        await ctx.send(f"🥳 Congratulations {winner.mention}! You just won **{prize}** — 100% dad-approved!")
        print(f"[Giveaway] Winner: {winner.name}")

        try:
            await winner.send(
                f"🎁 You won the giveaway for **{prize}** in **#{ctx.channel.name}**! Enjoy your prize — 100% dad-approved! 👨‍👧"
            )
        except discord.Forbidden:
            print(f"[Giveaway] Could not DM {winner.name} — they have DMs disabled.")

        if log_channel:
            await log_channel.send(f"✅ Giveaway ended! Winner: **{winner.name}** for **{prize}**")

    @start_giveaway.error
    async def giveaway_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            await ctx.send("🚫 Sorry, you need the **Giveaways** role to start a giveaway.")

async def setup(bot):
    await bot.add_cog(Giveaways(bot))
