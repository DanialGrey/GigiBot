import discord
from discord.ext import commands
import asyncio
import random

class BuildCheck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    print("[BuildCheck] Cog loaded.")

    @commands.command(name="buildcheck")
    async def build_check(self, ctx, *, description: str = None):
        """Submit a build screenshot and receive a quirky GigiBot rating."""

        # ✅ Restrict to #share-your-builds channel only
        if ctx.channel.name != "share-your-builds":
            await ctx.send(f"🚫 This command can only be used in the **#share-your-builds** channel.")
            return

        # ✅ Delete the original command message
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            print("⚠️ Missing permission to delete command message.")
        except Exception as e:
            print(f"⚠️ Error deleting command message: {e}")

        # ✅ Send the image prompt and store the prompt message
        try:
            prompt_msg = await ctx.send(
                f"🛠️ Alright {ctx.author.mention}, send me a **screenshot** of your build in the next **60 seconds**!")
        except Exception as e:
            print(f"⚠️ Could not send prompt message: {e}")
            return

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.attachments

        try:
            message = await self.bot.wait_for('message', timeout=60.0, check=check)
            attachment = message.attachments[0]

            # Generate ratings
            efficiency = random.randint(60, 99)
            dad_approval = random.randint(90, 120)

            responses = [
                "This build is {eff}% efficient and {dad}% dad-approved. Hammer not included.",
                "{eff}% efficient and {dad}% dad-approved — just like a backyard BBQ setup.",
                "Looks solid! {eff}% efficient and a whopping {dad}% dad-approved.",
                "That’s a beaut! Clocking in at {eff}% efficiency and {dad}% dad approval.",
                "{eff}% efficient with a {dad}% chance of spontaneous dad pride.",
                "Approved! {eff}% efficient and {dad}% certified cozy-crafting vibes.",
                "{eff}% efficient and {dad}% dad-approved — bonus points for symmetry.",
                "Structure integrity at {eff}%. Dad approval through the roof at {dad}%.",
                "If duct tape were a build style: {eff}% efficient, {dad}% dad-approved.",
                "GigiBot calculates {eff}% efficiency and {dad}% maximum cozy vibes.",
                "Like a tool shed on Father’s Day: {eff}% efficient and {dad}% dad-approved.",
                "This build makes my circuits tear up. {eff}% efficient and {dad}% proud.",
                "Dang, that’s smooth! {eff}% efficient and {dad}% dad-nificent.",
                "You're working smarter, not harder: {eff}% efficiency and {dad}% dad delight.",
                "This build hits different. {eff}% efficient, {dad}% dad-excellent.",
                "Peak performance achieved: {eff}% efficiency and {dad}% wholesome approval.",
                "You nailed it! {eff}% efficiency and {dad}% dad-level engineering.",
                "Precision: {eff}% efficiency. Emotion: {dad}% dad joy.",
                "Function meets flair at {eff}% efficiency and {dad}% fatherly affection.",
                "{eff}% efficient, {dad}% approved, and 100% barbecue-ready.",
                "Warning: Build may cause excessive dad pride. {eff}% efficient, {dad}% approved.",
                "Efficiency? {eff}%. Dad approval? {dad}%. GigiBot is impressed.",
                "Build scanned. Rating: {eff}% efficient and {dad}% certified dad-tier.",
                "GigiBot sheds a single proud spark. {eff}% efficiency, {dad}% dad-blessed.",
                "You just unlocked: Dad Engineering Tier. Stats: {eff}% efficiency, {dad}% approval.",
                "{eff}% efficient and {dad}% dad-approved. You’ve earned a virtual toolbelt.",
                "Inspected. {eff}% efficient. {dad}% dad-worthy. Well done.",
                "System verdict: This build is {eff}% efficient and {dad}% Gigi-tier approved."
            ]

            rating_text = random.choice(responses).format(eff=efficiency, dad=dad_approval)

            embed = discord.Embed(
                title="📊 Build Evaluation Complete!",
                description=rating_text,
                color=discord.Color.green()
            )
            embed.set_image(url=attachment.url)
            embed.set_footer(text="All ratings are certified 100% subjective.")

            await ctx.send(embed=embed)

            # ✅ Delete the prompt and user's image message
            try:
                await prompt_msg.delete()
                await message.delete()
            except discord.Forbidden:
                print("⚠️ Missing permission to delete prompt or image message.")
            except Exception as e:
                print(f"⚠️ Failed to delete messages: {e}")

            if not attachment.content_type.startswith("image/"):
                await ctx.send("🚫 That's not an image. Try again with a screenshot next time!")
                return

        except asyncio.TimeoutError:
            try:
                await prompt_msg.delete()
            except Exception:
                pass
            await ctx.send(
                "⌛ Timed out! You didn’t upload an image in time. Try `!buildcheck` again when you're ready.")


async def setup(bot):
    await bot.add_cog(BuildCheck(bot))
