import discord
from discord.ext import commands

class WelcomeEmbed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("[WelcomeEmbed] Cog loaded.")

    @commands.command(name="send_welcome_embed")
    @commands.has_permissions(administrator=True)
    async def send_welcome_embed(self, ctx):
        # ✅ Delete the original command message
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            print("⚠️ Missing permission to delete messages.")
        except Exception as e:
            print(f"⚠️ Failed to delete command message: {e}")
        """Sends a custom welcome embed to the current channel."""
        embed = discord.Embed(
            title="🎉 Welcome to GirlDad Gaming Co!",
            description=(
                "👋 We’re a cozy community of survival, crafting, and sim game lovers — especially the *girl dads* among us.\n\n"
                "**Get Started:**\n"
                "🔹 Read the rules (you already did this — nice work!)\n"
                "🔹 Head to <#get-roles> to select the games you play\n"
                "🔹 Jump into <#general> and say hi!\n\n"
                "**Need help?** Ping a mod or post in <#general>.\n"
                "🎮 We play games like ARK, Valheim, Satisfactory, Enshrouded, and more!\n\n"
                "💙 Thanks for being here!"
            ),
            color=discord.Color(0xf57ef3)
        )
        embed.set_footer(text="Wraithborne • GirlDad Gaming Co")
        await ctx.send(embed=embed)

    @commands.command(name="send_rules_embed")
    @commands.has_permissions(administrator=True)
    async def send_rules_embed(self, ctx):
        # ✅ Delete the original command message
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            print("⚠️ Missing permission to delete messages.")
        except Exception as e:
            print(f"⚠️ Failed to delete command message: {e}")
        """Sends the server rules as an embed to the current channel."""
        embed = discord.Embed(
            title="📕 Server Rules",
            color=discord.Color(0xf57ef3)
        )

        embed.add_field(
            name="1️⃣ Be Respectful",
            value="Treat everyone with kindness. No hate speech, harassment, discrimination, etc.",
            inline=False
        )
        embed.add_field(
            name="2️⃣ Keep It Clean",
            value="No NSFW content, excessive swearing, or inappropriate usernames/pics.",
            inline=False
        )
        embed.add_field(
            name="3️⃣ Use Channels Properly",
            value="Stick to the topic for each channel. For example, post dad jokes in `#dad-jokes`, not `#general`.",
            inline=False
        )
        embed.add_field(
            name="4️⃣ No Spam or Self-Promo",
            value="Don't spam messages, links, or promote your own content without permission.",
            inline=False
        )
        embed.add_field(
            name="5️⃣ Respect the Mods",
            value="If asked to do something, or not do something by the mods, follow their directions",
            inline=False
        )
        embed.add_field(
            name="6️⃣ Follow Discord’s Guidelines",
            value="[Click here](https://discord.com/guidelines) to read Discord’s Community Guidelines.",
            inline=False
        )

        embed.set_footer(text="Breaking rules may result in a timeout or ban. Play nice. 🛠️")

        await ctx.send(embed=embed)

    @commands.command(name="send_roles_embed")
    @commands.has_permissions(administrator=True)
    async def send_roles_embed(self, ctx):
        # ✅ Delete the original command message
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            print("⚠️ Missing permission to delete messages.")
        except Exception as e:
            print(f"⚠️ Failed to delete command message: {e}")
        """Sends a get-roles instruction embed to the current channel."""
        embed = discord.Embed(
            title="🎭 Choose Your Roles",
            description=(
                "Welcome to `#get-roles`! Here you can assign yourself roles to customize your experience.\n\n"
                "Pick the games you play, your platform, or other fun tags to unlock special channels and pings."
            ),
            color=discord.Color(0xf57ef3)
        )

        embed.add_field(
            name="🎮 Game Roles",
            value="Select roles like `ARK`, `Valheim`, or `Satisfactory` to join those conversations.",
            inline=False
        )

        embed.add_field(
            name="🛠️ Platform Roles (Optional)",
            value="Let others know if you’re on `PC`, `Xbox`, or `PlayStation`.",
            inline=False
        )

        embed.add_field(
            name="📢 Why Bother?",
            value="We use roles to unlock channels, tag groups for updates, and keep things tidy.\nPick what fits you!",
            inline=False
        )

        embed.set_footer(text="Use the reactions below to pick your roles. You can change them anytime!")
        await ctx.send(embed=embed)

    @commands.command(name="send_ranks_embed")
    @commands.has_permissions(administrator=True)
    async def send_ranks_embed(self, ctx):
        """Sends the ranks system explanation embed and handles pinning/cleanup."""

        # Delete the command invocation (user's !send_ranks_embed message)
        await ctx.message.delete()

        # Create the embed
        embed = discord.Embed(
            title="🏆 Server Ranks & XP System",
            description=(
                "Every message you post (with substance!) helps you earn XP and level up.\n"
                "Reach new ranks, earn cool role titles, and show off your progress!"
            ),
            color=discord.Color(0xf57ef3)
        )

        embed.add_field(
            name="💡 How It Works",
            value=(
                "- Messages longer than 10 characters earn XP\n"
                "- You get XP **no more than once every 5 minutes**\n"
                "- Commands and spam don't count\n"
                "- Use `!rank` to check your level!"
            ),
            inline=False
        )

        embed.add_field(
            name="🎖️ Rank Rewards",
            value="As you level up, you'll automatically get roles like:\n• `New Recruit`\n• `Junior Engineer`\n• `Cozy Crafter`\n• `Factory Foreman`\n…and more!",
            inline=False
        )

        embed.set_footer(text="Stay active, be helpful, and have fun leveling up!")

        # Send the embed
        message = await ctx.send(embed=embed)

        # Pin the embed message
        await message.pin()

        # Attempt to delete the system "pinned a message to this channel" message
        async for msg in ctx.channel.history(limit=10):
            if msg.type == discord.MessageType.pins_add and msg.author == ctx.guild.me:
                try:
                    await msg.delete()
                    break
                except discord.Forbidden:
                    print("[Warning] Missing permission to delete system pin message.")
                except Exception as e:
                    print(f"[Error] Failed to delete pin system message: {e}")

    @commands.command(name="send_dadjokes_embed")
    @commands.has_permissions(administrator=True)
    async def send_dadjokes_embed(self, ctx):
        """Sends the dad jokes intro embed, pins it, and deletes system messages."""

        # Delete the command message
        await ctx.message.delete()

        # Create the embed
        embed = discord.Embed(
            title="👨‍👧 Dad Jokes Central",
            description=(
                "This is the sacred ground of puns, groaners, and eye-rollers.\n\n"
                "Whether you’re a seasoned dad or just aspiring to peak cringe, this is your space to share the worst best jokes you know."
            ),
            color=discord.Color(0xf57ef3)
        )

        embed.add_field(
            name="📜 The Rules Are Simple:",
            value=(
                "• Keep it clean (PG jokes only — this server is kid-friendly)\n"
                "• Jokes only — reactions welcome, discussions go in `#general`\n"
                "• Bonus points for original material 🧠"
            ),
            inline=False
        )

        embed.set_footer(text="Don't forget to groan. That's how we know it's working.")

        # Send the embed
        message = await ctx.send(embed=embed)

        # Pin it
        await message.pin()

        # Delete the system “pinned a message” notification
        async for msg in ctx.channel.history(limit=10):
            if msg.type == discord.MessageType.pins_add and msg.author == ctx.guild.me:
                try:
                    await msg.delete()
                    break
                except discord.Forbidden:
                    print("[Warning] Missing permission to delete system pin message.")
                except Exception as e:
                    print(f"[Error] Failed to delete pin system message: {e}")

    @commands.command(name="send_builds_embed")
    @commands.has_permissions(administrator=True)
    async def send_builds_embed(self, ctx):
        """Sends the 'share-your-builds' embed, pins it, and deletes system messages."""

        # Delete the command message
        await ctx.message.delete()

        # Build the embed
        embed = discord.Embed(
            title="🏗️ Share Your Builds",
            description=(
                "This is the place to show off what you've built in your favorite survival, crafting, and sim games.\n\n"
                "From sprawling factories to treehouse hideouts, we want to see it!"
            ),
            color=discord.Color(0xf57ef3)
        )

        embed.add_field(
            name="📸 What to Share",
            value=(
                "• Screenshots of your builds\n"
                "• Time-lapse clips, reels, or tours\n"
                "• Creative layouts, designs, or contraptions\n"
                "• Before/after shots, cursed builds, or proud fails 😅"
            ),
            inline=False
        )

        embed.add_field(
            name="🛠️ Tips",
            value=(
                "• Include the game name in your post (especially if it’s less obvious)\n"
                "• Want feedback? Ask for it!\n"
                "• Be kind and hype each other up 🙌"
            ),
            inline=False
        )
        embed.add_field(
            name="📋 How to Use",
            value=(
                "Use the `!buildcheck` command here to start the bot.\n"
                "You will be prompted to upload a build photo (you have 60 seconds to upload, so have it ready before starting!).\n"
                "Gigi Bot will 'review' you build and rate it."
            ),
            inline=False
        )

        embed.set_footer(text="Built something epic? Let’s see it! 💪")

        # Send the embed
        message = await ctx.send(embed=embed)

        # Pin the message
        await message.pin()

        # Delete the system “pinned a message” notice
        async for msg in ctx.channel.history(limit=10):
            if msg.type == discord.MessageType.pins_add and msg.author == ctx.guild.me:
                try:
                    await msg.delete()
                    break
                except discord.Forbidden:
                    print("[Warning] Missing permission to delete system pin message.")
                except Exception as e:
                    print(f"[Error] Failed to delete pin system message: {e}")

    @commands.command(name="send_botthings_embed")
    @commands.has_permissions(administrator=True)
    async def send_botthings_embed(self, ctx):
        """Sends the 'bot-things' embed, pins it, and deletes system messages."""

        # Delete the command message
        await ctx.message.delete()

        # Create the embed
        embed = discord.Embed(
            title="🤖 Bot Things Happen Here",
            description=(
                "`#bot-things` is your go-to channel for interacting with GigiBot and other bots.\n\n"
                "Use this space for bot commands, test runs, leveling up, and automation fun!"
            ),
            color=discord.Color(0xf57ef3)
        )

        embed.add_field(
            name="🛠️ What Goes Here",
            value=(
                "• `!rank`, `!buildcheck`, `!dadjoke`, and similar commands\n"
                "• Slash commands like `/stats`, `/ping`, etc.\n"
                "• Bot-generated messages that don’t fit elsewhere"
            ),
            inline=False
        )

        embed.add_field(
            name="📌 Why This Channel Exists",
            value="Keeps your other channels focused and clean. If you're testing or exploring commands, this is the safe zone.",
            inline=False
        )

        embed.set_footer(text="If it beeps or blips, it belongs here.")

        # Send the embed
        message = await ctx.send(embed=embed)

        # Pin the message
        await message.pin()

        # Delete the system “pinned a message” notification
        async for msg in ctx.channel.history(limit=10):
            if msg.type == discord.MessageType.pins_add and msg.author == ctx.guild.me:
                try:
                    await msg.delete()
                    break
                except discord.Forbidden:
                    print("[Warning] Missing permission to delete system pin message.")
                except Exception as e:
                    print(f"[Error] Failed to delete pin system message: {e}")

    @commands.command(name="send_giveaways_embed")
    @commands.has_permissions(administrator=True)
    async def send_giveaways_embed(self, ctx):
        """Sends the 'giveaways' embed, pins it, and deletes system messages."""

        # Delete the command message
        await ctx.message.delete()

        # Create the embed
        embed = discord.Embed(
            title="🎁 Giveaways & Drops",
            description=(
                "Welcome to `#giveaways`, the channel where free stuff happens!\n\n"
                "From game codes and channel merch to seasonal surprises — keep an eye out here for chances to win!"
            ),
            color=discord.Color(0xf57ef3)
        )

        embed.add_field(
            name="📋 How It Works",
            value=(
                "• We'll post a giveaway with instructions — usually a reaction or short entry form\n"
                "• Winners are selected randomly (unless noted)\n"
                "• Some giveaways are for certain roles or ranks — make sure you’ve picked yours!"
            ),
            inline=False
        )

        embed.add_field(
            name="✅ Rules",
            value=(
                "• One entry per person (don’t try to cheat, GigiBot sees all 👀)\n"
                "• Don’t ping staff or beg for prizes\n"
                "• If you win, you’ll be contacted via DM or @mention"
            ),
            inline=False
        )

        embed.set_footer(text="Good luck and may the loot gods be ever in your favor!")

        # Send the embed
        message = await ctx.send(embed=embed)

        # Pin the embed message
        await message.pin()

        # Delete the system “pinned a message” notice
        async for msg in ctx.channel.history(limit=10):
            if msg.type == discord.MessageType.pins_add and msg.author == ctx.guild.me:
                try:
                    await msg.delete()
                    break
                except discord.Forbidden:
                    print("[Warning] Missing permission to delete system pin message.")
                except Exception as e:
                    print(f"[Error] Failed to delete pin system message: {e}")


    @commands.command(name="send_suggestions_embed")
    @commands.has_permissions(administrator=True)
    async def send_suggestions_embed(self, ctx):
        """Sends the suggestions channel info embed, pins it, and deletes system pin messages."""

        # Delete the command invocation message
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            print("⚠️ Missing permission to delete messages.")
        except Exception as e:
            print(f"⚠️ Failed to delete command message: {e}")

        embed = discord.Embed(
            title="💡 Suggestions & Feedback",
            description=(
                "Welcome to `#suggestions`! This is the place to share your ideas to improve the community, "
                "suggest new features, or give feedback.\n\n"
                "Please be respectful and constructive with your suggestions. React with 👍 or 👎 to vote on ideas!"
            ),
            color=discord.Color(0xf57ef3)
        )

        embed.add_field(
            name="📋 How to Suggest",
            value=(
                "Use `!suggest` followed by your suggestion here to submit your ideas.\n"
                "ie. !suggest Keep up the good work!.\n"
                "Try to be clear and concise for best results"
            ),
            inline=False
        )

        embed.add_field(
            name="🔔 Notifications",
            value=(
                "The community team will update this channel with accepted suggestions, "
                "planned features, or reasons why some ideas can't be implemented."
            ),
            inline=False
        )

        embed.set_footer(text="Your voice matters! Thanks for helping us grow. 💙")

        message = await ctx.send(embed=embed)
        await message.pin()

        # Delete the system "pinned a message" notification
        async for msg in ctx.channel.history(limit=10):
            if msg.type == discord.MessageType.pins_add and msg.author == ctx.guild.me:
                try:
                    await msg.delete()
                    break
                except discord.Forbidden:
                    print("[Warning] Missing permission to delete system pin message.")
                except Exception as e:
                    print(f"[Error] Failed to delete pin system message: {e}")

# Required setup function to load the cog
async def setup(bot):
    await bot.add_cog(WelcomeEmbed(bot))
