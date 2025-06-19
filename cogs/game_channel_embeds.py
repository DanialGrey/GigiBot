import discord
from discord.ext import commands

class GameChannelEmbeds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("[ChannelEmbed] Cog loaded.")

    async def send_game_embed(self, ctx, title, description, thumb_url=None):
        await ctx.message.delete()

        embed = discord.Embed(
            title=f"🎮 {title}",
            description=description,
            color=discord.Color(0xf57ef3)
        )

        embed.add_field(
            name="💬 What's this channel for?",
            value=(
                "Feel free to share screenshots, start discussions, post updates, tips, theories, or even coordinate co-op play!"
            ),
            inline=False
        )

        embed.set_footer(text="Stay respectful, avoid spoilers (or tag them), and have fun!")

        if thumb_url:
            embed.set_image(url=thumb_url)

        message = await ctx.send(embed=embed)
        await message.pin()

        async for msg in ctx.channel.history(limit=10):
            if msg.type == discord.MessageType.pins_add and msg.author == ctx.guild.me:
                try:
                    await msg.delete()
                    break
                except Exception as e:
                    print(f"[Error] Could not delete pin system message: {e}")

    # === Add one command per game ===

    @commands.command(name="enshrouded_embed")
    async def enshrouded_embed(self, ctx):
        description = (
            "**Enshrouded** is an open-world survival action RPG where players battle corruption, craft powerful gear, and uncover lost technology in a world hidden in fog."
        )
        await self.send_game_embed(ctx, "Enshrouded", description, "https://cdn.cloudflare.steamstatic.com/steam/apps/1203620/header.jpg")

    @commands.command(name="satisfactory_embed")
    async def satisfactory_embed(self, ctx):
        description = (
            "**Satisfactory** is a factory-building sim where you explore an alien planet, automate everything, and create complex conveyor systems in first-person."
        )
        await self.send_game_embed(ctx, "Satisfactory", description, "https://cdn.cloudflare.steamstatic.com/steam/apps/526870/header.jpg")

    @commands.command(name="valheim_embed")
    async def valheim_embed(self, ctx):
        description = (
            "**Valheim** is a Viking-themed survival sandbox where you build, explore, and conquer mythical beasts across procedurally generated realms."
        )
        await self.send_game_embed(ctx, "Valheim", description, "https://cdn.cloudflare.steamstatic.com/steam/apps/892970/header.jpg")

    @commands.command(name="ark_embed")
    async def ark_embed(self, ctx):
        description = (
            "**ARK: Survival Evolved** & **Survival Ascended** are survival games set on islands filled with dinosaurs, where players tame creatures, build bases, and survive hostile elements."
        )
        await self.send_game_embed(ctx, "ARK: Survival Evolved & Ascended", description, "https://cdn.cloudflare.steamstatic.com/steam/apps/2399830/header.jpg")

    @commands.command(name="palworld_embed")
    async def palworld_embed(self, ctx):
        description = (
            "**Palworld** is a monster-collecting open-world survival game where you farm, craft, and fight alongside strange creatures called Pals."
        )
        await self.send_game_embed(ctx, "Palworld", description, "https://cdn.cloudflare.steamstatic.com/steam/apps/1623730/header.jpg")

    @commands.command(name="nightingale_embed")
    async def nightingale_embed(self, ctx):
        description = (
            "**Nightingale** is a shared-world survival-crafting game set in a gaslamp fantasy universe, where players portal between realms and build grand estates."
        )
        await self.send_game_embed(ctx, "Nightingale", description, "https://cdn.cloudflare.steamstatic.com/steam/apps/1928980/header.jpg")

    @commands.command(name="techtonica_embed")
    async def techtonica_embed(self, ctx):
        description = (
            "**Techtonica** is a factory automation game set underground on an alien planet. Build and optimize machines as you uncover a mysterious narrative."
        )
        await self.send_game_embed(ctx, "Techtonica", description, "https://cdn.cloudflare.steamstatic.com/steam/apps/1457320/header.jpg")

    @commands.command(name="hogwarts_embed")
    async def hogwarts_embed(self, ctx):
        description = (
            "**Hogwarts Legacy** is an immersive open-world RPG set in the 1800s wizarding world. Attend Hogwarts, learn spells, and explore magical secrets."
        )
        await self.send_game_embed(ctx, "Hogwarts Legacy", description, "https://cdn.cloudflare.steamstatic.com/steam/apps/990080/header.jpg")

    @commands.command(name="infected_embed")
    async def infected_embed(self, ctx):
        description = (
            "**The Infected** is a survival crafting game where players battle mutant creatures, manage hunger/thirst, and fortify shelters in a harsh world."
        )
        await self.send_game_embed(ctx, "The Infected", description, "https://cdn.cloudflare.steamstatic.com/steam/apps/1360000/header.jpg")

    @commands.command(name="farmingsim_embed")
    async def farmingsim_embed(self, ctx):
        description = (
            "**Farming Simulator 22 & 25** let you manage a modern farm, harvest crops, raise animals, and expand operations with realistic equipment."
        )
        await self.send_game_embed(ctx, "Farming Simulator 22 & 25", description, "https://steamcdn-a.akamaihd.net/steam/apps/2300320/header.jpg")

    @commands.command(name="conan_embed")
    async def conan_embed(self, ctx):
        description = (
            "**Conan: Exiles** is a brutal open-world survival game set in the lands of Conan the Barbarian. Survive, build, dominate."
        )
        await self.send_game_embed(ctx, "Conan: Exiles", description, "https://cdn.cloudflare.steamstatic.com/steam/apps/440900/header.jpg")

    @commands.command(name="frostpunk_embed")
    async def frostpunk_embed(self, ctx):
        description = (
            "**Frostpunk & Frostpunk 2** are society survival games where you manage a frozen city, make tough moral decisions, and lead humanity’s last hope."
        )
        await self.send_game_embed(ctx, "Frostpunk & Frostpunk 2", description, "https://i.ytimg.com/vi/oPe_zsYBPgs/maxresdefault.jpg")

    @commands.command(name="wwe2k_embed")
    async def wwe2k_embed(self, ctx):
        description = (
            "**WWE 2K22, 2K24, & 2K25** let you step into the ring with legendary wrestlers in a mix of simulation and arcade-style gameplay."
        )
        await self.send_game_embed(ctx, "WWE 2K Series", description, "https://cdn.cloudflare.steamstatic.com/steam/apps/2878960/library_header.jpg")

    @commands.command(name="7d2d_embed")
    async def seven_days_embed(self, ctx):
        description = (
            "**7 Days to Die** is a zombie survival crafting game with base-building, looting, and tower defense mechanics."
        )
        await self.send_game_embed(ctx, "7 Days to Die", description, "https://cdn.cloudflare.steamstatic.com/steam/apps/251570/header.jpg")

    @commands.command(name="forest_embed")
    async def forest_embed(self, ctx):
        description = (
            "**The Forest & Sons of the Forest** are horror survival games about building, exploring, and fighting off terrifying cannibals."
        )
        await self.send_game_embed(ctx, "The Forest & Sons of the Forest", description, "https://cdn.cloudflare.steamstatic.com/steam/apps/1326470/header.jpg")

    @commands.command(name="greenhell_embed")
    async def green_hell_embed(self, ctx):
        description = (
            "**Green Hell** is a realistic survival sim set in the Amazon, featuring psychological challenges, crafting, and brutal wildlife."
        )
        await self.send_game_embed(ctx, "Green Hell", description, "https://cdn.cloudflare.steamstatic.com/steam/apps/815370/header.jpg")

    @commands.command(name="mist_embed")
    async def mist_embed(self, ctx):
        description = (
            "**MIST Survival** is a single-player survival stealth sandbox where players face infection, mist-covered ambushes, and human enemies."
        )
        await self.send_game_embed(ctx, "MIST Survival", description, "https://cdn.cloudflare.steamstatic.com/steam/apps/914620/header.jpg")

    @commands.command(name="smalland_embed")
    async def smalland_embed(self, ctx):
        description = (
            "**Smalland** is a survival game where you're shrunken to bug-size. Tame insects, explore forests, and build in a massive tiny world."
        )
        await self.send_game_embed(ctx, "Smalland", description, "https://cdn.cloudflare.steamstatic.com/steam/apps/768200/header.jpg")

    @commands.command(name="grounded_embed")
    async def grounded_embed(self, ctx):
        description = (
            "**Grounded** is a co-op survival game where you’re shrunk in a backyard full of bugs, hazards, and secrets. Think ‘Honey I Shrunk the Kids’ meets crafting."
        )
        await self.send_game_embed(ctx, "Grounded", description, "https://cdn.cloudflare.steamstatic.com/steam/apps/962130/header.jpg")

    @commands.command(name="sod_embed")
    async def sod_embed(self, ctx):
        description = (
            "**State of Decay 1 & 2** are zombie survival management games focused on building communities, scavenging, and fighting back the apocalypse."
        )
        await self.send_game_embed(ctx, "State of Decay Series", description, "https://cdn.cloudflare.steamstatic.com/steam/apps/495420/header.jpg")

    @commands.command(name="jwe_embed")
    async def jwe_embed(self, ctx):
        description = (
            "**Jurassic World: Evolution 1 & 2** are park management sims where you build your own dinosaur parks and manage chaos."
        )
        await self.send_game_embed(ctx, "Jurassic World: Evolution Series", description, "https://cdn.cloudflare.steamstatic.com/steam/apps/1244460/header.jpg")

    @commands.command(name="fallout_embed")
    async def fallout_embed(self, ctx):
        description = (
            "The **Fallout** series spans multiple post-apocalyptic RPGs, including Fallout 3, 4, New Vegas, 76, and the TV series — talk about any and all of them here!"
        )
        await self.send_game_embed(ctx, "Fallout Series", description, "https://cdn.cloudflare.steamstatic.com/steam/apps/1151340/header.jpg")


async def setup(bot):
    await bot.add_cog(GameChannelEmbeds(bot))
