import discord
from discord.ext import commands

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_name = "welcome"  # The channel where welcome messages are posted

    print("[Welcome] Cog loaded.")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Look for the #welcome channel in the guild
        channel = discord.utils.get(member.guild.text_channels, name=self.channel_name)
        if channel:
            embed = discord.Embed(
                title="👋 Welcome!",
                description=f"Hey {member.mention}, welcome to **{member.guild.name}**!",
                color=discord.Color.blue()
            )
            embed.set_footer(text="We're glad to have you here. Enjoy your stay!")
            await channel.send(embed=embed)
        else:
            print(f"⚠️ Channel #{self.channel_name} not found in {member.guild.name}")

async def setup(bot):
    await bot.add_cog(Welcome(bot))
