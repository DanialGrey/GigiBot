import discord
from discord.ext import commands
import aiohttp

class DadJokes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="dadjoke")
    async def dadjoke(self, ctx):
        """Fetches a random dad joke from the Official Joke API and shows a button for the punchline."""

        url = "https://official-joke-api.appspot.com/jokes/random"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await ctx.send("Oops! Dad doesn't feel like being funny right now. Try again later.")
                    return
                joke = await resp.json()

        setup = joke.get("setup")
        punchline = joke.get("punchline")

        if not setup or not punchline:
            await ctx.send("Oops! Dad doesn't feel like being funny right now. Try again later.")
            return

        # Create a button to reveal the punchline
        class PunchlineButton(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=90)  # Button will be active for 90 seconds
                self.punchline_shown = False

            @discord.ui.button(label="Why?", style=discord.ButtonStyle.primary)
            async def show_punchline(self, interaction: discord.Interaction, button: discord.ui.Button):
                if self.punchline_shown:
                    await interaction.response.send_message("Punchline already revealed!", ephemeral=True)
                    return

                self.punchline_shown = True
                button.disabled = True
                await interaction.response.edit_message(content=f"**{setup}**\n\n||{punchline}||", view=self)

        view = PunchlineButton()
        await ctx.send(content=f"**{setup}**", view=view)


async def setup(bot):
    await bot.add_cog(DadJokes(bot))
