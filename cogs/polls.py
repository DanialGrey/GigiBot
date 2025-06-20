import discord
from discord.ext import commands
import asyncio

class Polls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("[Polls] Cog loaded.")

    @commands.command(name="poll")
    @commands.has_any_role("Moderator", "Apex")
    async def create_poll(self, ctx):
        """Creates a multiple-choice poll (up to 10 options)"""

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        # ✅ Delete the original command message
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            print("⚠️ Missing permission to delete messages.")
        except Exception as e:
            print(f"⚠️ Failed to delete command message: {e}")

        # Ask for the poll question
        prompt1 = await ctx.send("🗳 What is the poll question? Type `cancel` to cancel.")
        try:
            question_msg = await self.bot.wait_for("message", check=check, timeout=180)  # 3 minutes timeout
            if question_msg.content.lower() == 'cancel':
                await ctx.send("❌ Poll creation canceled.")
                return
            question = question_msg.content
        except asyncio.TimeoutError:
            await ctx.send("⏰ Timed out. Try starting the poll again.")
            return
        await prompt1.delete()
        await question_msg.delete()

        # Ask for the role to ping (or none)
        prompt2 = await ctx.send("🔔 Who should be pinged? Type a role name or @role, or type 'none' for no ping. Type `cancel` to cancel.")
        try:
            ping_role_msg = await self.bot.wait_for("message", check=check, timeout=180)  # 3 minutes timeout
            if ping_role_msg.content.lower() == 'cancel':
                await ctx.send("❌ Poll creation canceled.")
                return
            ping_role_input = ping_role_msg.content.strip()

            if ping_role_input == 'none':
                ping_role = None
                ping_content = ""  # No ping content if 'none' is selected
            else:
                # Try to parse role mentions (e.g., @role)
                role_mention = discord.utils.get(ctx.guild.roles, mention=ping_role_input)
                if role_mention:
                    ping_role = role_mention
                    ping_content = f"<@&{role_mention.id}>"
                else:
                    await ctx.send(f"❌ Role `{ping_role_input}` not found. Proceeding with no ping.")
                    ping_role = None
                    ping_content = ""  # No ping content if invalid role
        except asyncio.TimeoutError:
            await ctx.send("⏰ Timed out. Try starting the poll again.")
            return
        await prompt2.delete()
        await ping_role_msg.delete()

        # Ask for poll options one by one
        options = []
        prompt3 = await ctx.send("🔢 Please enter the first poll option (or type 'done' to finish or `cancel` to cancel).")
        try:
            while len(options) < 10:
                option_msg = await self.bot.wait_for("message", check=check, timeout=180)  # 3 minutes timeout
                if option_msg.content.lower() == 'cancel':
                    await ctx.send("❌ Poll creation canceled.")
                    return
                option = option_msg.content.strip()

                if option.lower() == 'done':  # If 'done' is typed, exit the loop
                    if len(options) == 0:  # Check if no options were added before 'done'
                        await ctx.send("❌ You must provide at least one option before typing 'done'.")
                    await option_msg.delete()  # Delete the 'done' message
                    break
                elif option:
                    options.append(option)  # Add valid options to the list
                    await prompt3.edit(content=f"🔢 Please enter option {len(options) + 1} (or type 'done' to finish).")
                else:
                    await ctx.send("❌ Option cannot be empty. Please enter a valid option.")
                await option_msg.delete()

            if len(options) == 0:
                await ctx.send("❌ You must provide at least one option.")
                return

            if len(options) > 10:
                await ctx.send("❌ You can only have up to 10 options.")
                return
        except asyncio.TimeoutError:
            await ctx.send("⏰ Timed out. Try starting the poll again.")
            return
        await prompt3.delete()

        emoji_map = ["🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭", "🇮", "🇯"]
        description = "\n".join(f"{emoji_map[i]} {option}" for i, option in enumerate(options))

        embed = discord.Embed(
            title=f"📊 {question}",
            description=description,  # List of options added here
            color=discord.Color(0xf57ef3)  # GirlDad Gaming pink
        )
        embed.set_footer(text=f"Poll started by {ctx.author.display_name}")

        # Send the poll message
        poll_msg = await ctx.send(content=ping_content, embed=embed)

        for i in range(len(options)):
            await poll_msg.add_reaction(emoji_map[i])

        # Initialize vote tracking (this will store votes for each option)
        votes = {i: 0 for i in range(len(options))}

        def update_poll_results():
            total_votes = sum(votes.values())
            results = []
            for i, vote_count in votes.items():
                percentage = (vote_count / total_votes * 100) if total_votes > 0 else 0
                results.append(f"{emoji_map[i]} {options[i]}: {vote_count} votes ({percentage:.2f}%)")
            return "\n".join(results)

        # Listen for new reactions and update poll results
        def check_reaction(reaction, user):
            return reaction.message.id == poll_msg.id and not user.bot

        first_vote_cast = False

        while True:
            reaction, _ = await self.bot.wait_for("reaction_add", check=check_reaction)

            # Update the vote count when a new reaction is added
            index = emoji_map.index(str(reaction.emoji))
            votes[index] += 1

            # Update results when a new reaction is added
            results = update_poll_results()
            await poll_msg.edit(embed=discord.Embed(
                title=f"📊 {question}",
                description=f"{description}\n\n{results}",  # Keep the options intact here
                color=discord.Color(0xf57ef3)
            ).set_footer(text=f"Poll started by {ctx.author.display_name}"))

            # Delete the initial options after the first vote
            if not first_vote_cast:
                description = ""  # Clear options from the description
                first_vote_cast = True
                await poll_msg.edit(embed=discord.Embed(
                    title=f"📊 {question}",
                    description=f"{results}",  # Only display the results now
                    color=discord.Color(0xf57ef3)
                ).set_footer(text=f"Poll started by {ctx.author.display_name}"))

            # Handle reaction removal and vote deduction
            @self.bot.event
            async def on_reaction_remove(reaction, user):
                if reaction.message.id == poll_msg.id and not user.bot:
                    index = emoji_map.index(str(reaction.emoji))
                    votes[index] -= 1
                    results = update_poll_results()
                    await poll_msg.edit(embed=discord.Embed(
                        title=f"📊 {question}",
                        description=f"{description}\n\n{results}",
                        color=discord.Color(0xf57ef3)
                    ).set_footer(text=f"Poll started by {ctx.author.display_name}"))

    @create_poll.error
    async def poll_error(self, ctx, error):
        if isinstance(error, commands.MissingAnyRole):
            await ctx.send("🚫 You need the **Moderator** or **Apex** role to start a poll.")

async def setup(bot):
    await bot.add_cog(Polls(bot))
