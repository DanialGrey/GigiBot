# cogs/giveaways.py

import discord
from discord.ext import commands
import asyncio
import random

class Giveaways(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    print("[Giveaways] Cog loaded.")

    @commands.command(name="giveaway")
    @commands.has_role("Giveaways")
    async def start_giveaway(self, ctx):
        if ctx.channel.name != "giveaways":
            await ctx.send("🚫 This command can only be used in the #giveaways channel.")
            return

        # Delete the original !giveaway command
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            print("[Giveaway] Couldn't delete command message.")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        # Ask for prize
        prize_prompt = await ctx.send("🎁 What is the prize?")
        try:
            prize_msg = await self.bot.wait_for("message", check=check, timeout=30)
            prize = prize_msg.content
        except asyncio.TimeoutError:
            await ctx.send("⏰ Timed out. No giveaway today!")
            await prize_prompt.delete()
            return

        # Ask for duration
        duration_prompt = await ctx.send("⏳ How long should the giveaway run? (in **seconds**, for now)")
        try:
            time_msg = await self.bot.wait_for("message", check=check, timeout=30)
            duration = int(time_msg.content)
        except asyncio.TimeoutError:
            await ctx.send("⏰ Timed out. No giveaway today!")
            await prize_prompt.delete()
            await duration_prompt.delete()
            return
        except ValueError:
            await ctx.send("❌ That's not a valid number of seconds.")
            await prize_prompt.delete()
            await duration_prompt.delete()
            return

        # Clean up all setup messages
        try:
            await prize_prompt.delete()
            await prize_msg.delete()
            await duration_prompt.delete()
            await time_msg.delete()
        except discord.Forbidden:
            print("[Giveaway] Failed to delete some setup messages.")

        # Post giveaway embed
        embed = discord.Embed(
            title="🎉 Giveaway Time!",
            description=f"Prize: **{prize}**\nReact with ✅ to enter!\nEnds in {duration} seconds.",
            color=discord.Color.blue()
        )
        giveaway_msg = await ctx.send(embed=embed)
        await giveaway_msg.add_reaction("✅")
        print(f"[Giveaway] Started giveaway for '{prize}' lasting {duration}s.")

        # Wait for the giveaway to end
        await asyncio.sleep(duration)

        updated_msg = await ctx.channel.fetch_message(giveaway_msg.id)
        print(f"[Giveaway] Fetched message after duration.")
        await asyncio.sleep(2)  # Ensure reactions are updated

        reaction = None
        for react in updated_msg.reactions:
            print(f"[Giveaway] Reaction found: {react.emoji} with {react.count} reactions")
            if str(react.emoji) == "✅":
                reaction = react
                break

        if reaction is None:
            await ctx.send("😢 No one entered the giveaway.")
            print("[Giveaway] No ✅ reaction found.")
            return

        users = []
        async for user in reaction.users():
            print(f"[Giveaway] Found user reacting: {user.name}")
            if not user.bot:
                users.append(user)

        if not users:
            await ctx.send("😢 No one entered the giveaway.")
            print("[Giveaway] No users found in reaction list.")
            return

        winner = random.choice(users)
        await ctx.send(f"🥳 Congratulations {winner.mention}! You just won **{prize}** — 100% dad-approved!")
        print(f"[Giveaway] Winner announced: {winner.name}")

        # DM the winner (optional)
        try:
            await winner.send(
                f"🎁 You won the giveaway for **{prize}** in **#{ctx.channel.name}**! Enjoy your prize — 100% dad-approved! 👨‍👧")
            print(f"[Giveaway] DM sent to {winner.name}")
        except discord.Forbidden:
            print(f"[Giveaway] Could not DM {winner.name} — they have DMs disabled.")


    @start_giveaway.error
    async def giveaway_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            await ctx.send("🚫 Sorry, you need the **Giveaways** role to start a giveaway.")

async def setup(bot):
    await bot.add_cog(Giveaways(bot))
