import discord
from discord.ext import commands
import random

class MemberExit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("[MemberExit] Cog loaded.")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        # Attempt to get the #campfire-gone-cold channel
        channel = discord.utils.get(member.guild.text_channels, name="campfire-gone-cold")
        if not channel:
            return

        # List of possible farewell messages
        exit_messages = [
            "**{member}** has left the campfire. The embers grow cold…",
            "The wind whispers: **{member}** is gone.",
            "A log cracks in the fire — **{member}** has stepped into the dark.",
            "The circle tightens. **{member}** won’t be returning tonight.",
            "A seat sits empty. **{member}** has vanished into the trees.",
            "The warmth fades slightly… **{member}** has wandered off.",
            "A shadow flickers. **{member}** is no longer among us.",
            "**{member}** left no trace but ash in the firelight.",
            "One less voice in the dark — **{member}** has departed.",
            "A silence settles in. **{member}** has walked away from the flame.",
            "The campfire crackles softly. **{member}** is gone.",
            "A spark fades. **{member}** has left the circle.",
            "The stars dim a little. **{member}** is no longer with us.",
            "**{member}** took their leave without a word — the fire sighs.",
            "A whisper in the smoke says goodbye to **{member}**."
        ]

        # Choose a random message and send it
        farewell = random.choice(exit_messages).format(member=member.display_name)
        await channel.send(farewell)

async def setup(bot):
    await bot.add_cog(MemberExit(bot))
