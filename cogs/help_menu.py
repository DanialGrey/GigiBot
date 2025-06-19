import discord
from discord.ext import commands

class HelpMenu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("[HelpMenu] Cog loaded.")

        #List your commands with the info about them.
        self.command_info = {
            "rank": {
                "description": "Check your XP level and current server rank.",
                "call": "!rank",
                "usage": "An embed is sent with your rank and current XP",
                "channel": "#ranks"
            },
            "leaderboard": {
                "description": "Check the current top 10 members on the server.",
                "call": "!leaderboard",
                "usage": "An embed is send showing the current top 10.",
                "channel": "#ranks"
            },
            "buildcheck": {
                "description": "Submit a build of yours for GigiBot to give a fun rating on.",
                "call": "!buildcheck",
                "usage": "The bot will ask you to upload a build image. Once uploaded the bot will post an embed with your build and give you a fun rating.",
                "channel": "#share-your-builds"
            },
            "buildtip": {
                "description": "Need inspiration, or just a pick-me-up? GigiBot will give you a fun building tip.",
                "call": "!buildtip",
                "usage": "The bot will respond with a tip.",
                "channel": "#bot_things"
            },
            "dadjoke": {
                "description": "Get a fresh dad joke to lighten the mood. 😄",
                "call": "!dadjoke",
                "usage": "The bot will respond with a joke and a 'Why?' button. Click the button and the answer will be posted as a spoiler.",
                "channel": "#dad-jokes"
            },
            "suggest": {
                "description": "Make suggestions for the community. New games, Discord channels, builds to make, etc.",
                "call": "!suggest [Your suggestion here]",
                "usage": "The bot will post an embed of your suggestions, and community members can upvote or downvote on it.",
                "channel": "#suggestions"
            },
            # Add more commands as needed...
        }


    @commands.command(name="help")
    async def help_command(self, ctx, *, command_name: str = None):
        """Sends help info: general list or specific command details."""

        # Delete the user's command message
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            print("Missing permission to delete messages.")
        except Exception as e:
            print(f"Error deleting message: {e}")

        # Send the main help menu
        if command_name is None:
            embed = discord.Embed(
                title="📖 GigiBot Help Menu",
                description="Here's all the available commands in the server, and where to use them:\nUse `!help [command]` for detailed info.",
                color=discord.Color(0xf57ef3)
            )

            for cmd, info in self.command_info.items():
                embed.add_field(
                    name=f"✨ `!{cmd}`",
                    value=f"📍 **Channel:** {info['channel']}",
                    inline=False
                )

            await ctx.send(embed=embed)
            return

        # Send detailed help for a specific command
        cmd = command_name.lower()

        if cmd not in self.command_info:
            await ctx.send(f"❌ No help available for `{cmd}`. Make sure it's a valid command.")
            return

        info = self.command_info[cmd]
        embed = discord.Embed(
            title=f"🔍 Help: `!{cmd}`",
            description=info["description"],
            color=discord.Color(0xf57ef3)
        )
        embed.add_field(name="✏️ How to Call", value=f"`{info['call']}`", inline=False)
        embed.add_field(name="📌 Usage", value=f"{info['usage']}", inline=False)
        embed.add_field(name="📍 Available In", value=info["channel"], inline=False)

        await ctx.send(embed=embed)

# Required setup function
async def setup(bot):
    await bot.add_cog(HelpMenu(bot))
