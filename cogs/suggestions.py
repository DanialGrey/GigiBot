import discord
from discord.ext import commands

class Suggestions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.suggestion_channel_name = "suggestions"  # channel name where suggestions allowed

    @commands.command(name="suggest")
    async def suggest(self, ctx, *, suggestion: str):
        """Submit a suggestion only in the suggestions channel."""

        # Check if the command is invoked in the correct channel by name
        if ctx.channel.name != self.suggestion_channel_name:
            await ctx.send(f"This command can only be used in the #{self.suggestion_channel_name} channel.", delete_after=8)
            try:
                await ctx.message.delete()
            except:
                pass
            return

        # Delete the user's command message
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            print("Missing permission to delete messages.")
        except Exception as e:
            print(f"Error deleting message: {e}")

        embed = discord.Embed(
            title="New Suggestion",
            description=suggestion,
            color=discord.Color(0xf57ef3)
        )
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        embed.set_footer(text=f"User ID: {ctx.author.id}")

        suggestion_message = await ctx.send(embed=embed)
        await suggestion_message.add_reaction("👍")
        await suggestion_message.add_reaction("👎")

async def setup(bot):
    await bot.add_cog(Suggestions(bot))
