
import discord
from discord.ext import commands, tasks
import aiohttp
import asyncio
import random
import os
from dotenv import load_dotenv
from datetime import datetime
import pytz

load_dotenv()

JOKE_API_URL = "https://official-joke-api.appspot.com/jokes/random"
DAILY_JOKE_CHANNEL_ID = int(os.getenv("DAILY_TIP_CHANNEL_ID", 0))  # For daily jokes (e.g., general-chat)
DAD_JOKES_COMMAND_CHANNEL = os.getenv("DAD_JOKES_COMMAND_CHANNEL", "dad-jokes")

class DadJokes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.daily_joke_task.start()
        print("[DadJokes] Cog loaded.")

    @commands.command(name="dadjoke")
    @commands.cooldown(rate=1, per=900, type=commands.BucketType.user)  # 15-minute cooldown
    async def dadjoke(self, ctx):
        """Fetches a random dad joke and shows a button for the punchline."""

        if ctx.channel.name != DAD_JOKES_COMMAND_CHANNEL:
            await ctx.send(f"🚫 This command can only be used in the **#{DAD_JOKES_COMMAND_CHANNEL}** channel.", delete_after=8)
            try:
                await ctx.message.delete()
            except:
                pass
            return

        try:
            await ctx.message.delete()
        except (discord.Forbidden, discord.HTTPException):
            pass

        async with aiohttp.ClientSession() as session:
            async with session.get(JOKE_API_URL) as resp:
                if resp.status != 200:
                    await ctx.send("😔 Dad doesn't feel like being funny right now. Try again later.")
                    return
                joke = await resp.json()

        setup = joke.get("setup")
        punchline = joke.get("punchline")

        if not setup or not punchline:
            await ctx.send("😔 Dad doesn't feel like being funny right now. Try again later.")
            return

        button_label = self._select_button_label(setup)
        view = self.PunchlineButton(ctx.author, setup, punchline, label=button_label)
        message = await ctx.send(content=f"**{setup}**", view=view)
        view.message = message
        await view.start_auto_reveal()

    def _select_button_label(self, setup):
        setup = setup.lower()
        if "why" in setup:
            return "Why?"
        elif "who" in setup:
            return "Who?"
        elif "what" in setup:
            return "What?"
        return "Tell me!"

    class PunchlineButton(discord.ui.View):
        def __init__(self, user, setup, punchline, label="Why?"):
            super().__init__(timeout=90)
            self.user = user
            self.setup = setup
            self.punchline = punchline
            self.punchline_shown = False
            self.message = None

            self.reveal_button = discord.ui.Button(label=label, style=discord.ButtonStyle.primary)
            self.reveal_button.callback = self.show_punchline
            self.add_item(self.reveal_button)

        async def show_punchline(self, interaction: discord.Interaction):
            if interaction.user != self.user:
                await interaction.response.send_message("Only the joke teller can reveal the punchline! 🤫", ephemeral=True)
                return
            if self.punchline_shown:
                await interaction.response.send_message("Punchline already revealed! ✅", ephemeral=True)
                return

            self.punchline_shown = True
            self.reveal_button.disabled = True
            self.reveal_button.label = "Punchline Shown ✅"
            await interaction.response.edit_message(content=f"**{self.setup}**\n\n||{self.punchline}||", view=self)

        async def start_auto_reveal(self):
            await asyncio.sleep(90)
            if not self.punchline_shown and self.message:
                self.punchline_shown = True
                self.reveal_button.disabled = True
                self.reveal_button.label = "Punchline Shown ✅"
                await self.message.edit(content=f"**{self.setup}**\n\n||{self.punchline}||", view=self)

    @dadjoke.error
    async def dadjoke_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            minutes = int(error.retry_after // 60)
            seconds = int(error.retry_after % 60)
            await ctx.send(f"⏳ Whoa! Cool your dad joke jets! Try again in {minutes}m {seconds}s.", delete_after=30)
            try:
                await ctx.message.delete()
            except:
                pass


    @tasks.loop(minutes=1)
    async def daily_joke_task(self):
        now = datetime.now(pytz.timezone("US/Pacific"))
        if now.hour == 17 and now.minute == 0:
            channel = self.bot.get_channel(DAILY_JOKE_CHANNEL_ID)
            if channel:
                async with aiohttp.ClientSession() as session:
                    async with session.get(JOKE_API_URL) as resp:
                        if resp.status != 200:
                            return
                        joke = await resp.json()
                setup = joke.get("setup")
                punchline = joke.get("punchline")
                if setup and punchline:
                    await channel.send(f"🧔‍♂️ **Dad Joke of the Day**\n**{setup}**\n\n||{punchline}||")

    @daily_joke_task.before_loop
    async def before_daily_joke(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(DadJokes(bot))
