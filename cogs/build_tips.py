# cogs/build_tips.py

import discord
from discord.ext import commands
import random

class BuildTips(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tips = {
            "automation": [
                "Automate early, automate often. If you're still hand-crafting, you're living in the past.",
                "Belts, pipes, and power — the holy trinity of automation.",
                "Redundancy in automation saves tears later. Trust dad.",
                "Looping conveyor belts might look silly, but they’ll save your build from jamming up.",
                "The best automation is the kind you forget exists — until it breaks.",
                "Machines don’t sleep, and neither should your production line.",
                "Splitters are your friends. Treat them right and they’ll feed the whole base.",
                "Automating coal is like teaching your kid to make their own lunch. Pure freedom.",
                "A bottleneck isn’t a problem — it’s an opportunity to over-engineer.",
                "If it moves on its own, it’s magic. If it moves well, it’s automation.",
            ],
            "base_building": [
                "Plan for more space than you think you need. You’ll use it all. Trust me.",
                "Elevators and ramps make your base feel real — and usable.",
                "Build your base with flow in mind. You should be able to run through it without tripping on wires.",
                "Every dad-approved base has a viewing deck. Optional grill included.",
                "Use the terrain — don’t fight it. Natural elevation can be your blueprint.",
                "Start small, build smart. Bigger doesn't always mean better — but it's still fun.",
                "A ladder is just a vertical regret prevention system.",
                "Always build with escape routes. You *will* get chased eventually.",
                "Try building a 'command center' — somewhere to oversee your chaos like a true dad general.",
                "Multi-level bases keep your cables tidy and your brain happier.",
            ],
            "storage": [
                "If you’re scrolling to find items, you need more boxes.",
                "Label everything. Future-you will high-five past-you.",
                "Overflow storage isn't lazy — it’s pro-level preparedness.",
                "Storage rooms should be organized like a dad’s garage — chaotic but knowable.",
                "Don't be afraid to go vertical with storage. Stack it like pancakes.",
                "When in doubt, double it. Then make it symmetrical.",
                "Storage isn’t just where you put stuff — it’s where dreams go until you need them.",
                "If your inventory’s full, your system’s not finished.",
                "A clean storage room is the sign of a messy adventure.",
                "Label one chest 'junk' and watch it become the most visited spot in your base.",
            ],
            "aesthetics": [
                "Symmetry brings peace. So do floor tiles that align properly.",
                "Light your base like you're showing it off on a real estate channel.",
                "Pathways and railings make it feel like home — and prevent falls.",
                "Functional *and* fabulous — your builds can be both.",
                "Glass floors: risky, stylish, and a little unhinged. Just like dad.",
                "Add windows. If you’re going to grind for hours, you might as well have a view.",
                "Accent lighting: because nothing says ‘power plant’ like mood lighting.",
                "Patterned floors are the dad flannel shirts of your factory. Timeless.",
                "A pretty base is a productive base. Science (probably).",
                "Use railings. Falling is funny until it’s you with 200 copper ingots.",
            ],
            "motivation": [
                "A scuffed base is still a base. Keep building, champ.",
                "Rome wasn’t built in a day, and neither was your storage system.",
                "You got this, one conveyor belt at a time.",
                "Messy builds have character — and so do you.",
                "Even if it’s held together with duct tape and dreams, it works. And that’s what counts.",
                "When in doubt, take a break, grab a juice box, and come back stronger.",
                "Every failed build is a blueprint for your next success.",
                "Build like someone’s going to tour your base — even if it’s just your kid.",
                "If your base makes sense to you, that’s all that matters. Mostly.",
                "Remember: no one starts as a master builder. But every master builder started.",
                "Your chaos is someone else’s blueprint. Share it proudly.",
                "Your base might be messy — but it’s yours. And that’s beautiful.",
                "A bad day building is still better than a good day grinding with no base.",
                "Even dad didn’t build the grill station right the first time. You’re doing great.",
            ]
        }

    print("[BuildTips] Cog loaded.")

    @commands.command(name="buildtip")
    async def build_tip(self, ctx, theme: str = None):
        """Get a random building or motivational tip. Optionally specify a theme: automation, base_building, storage, aesthetics, motivation"""
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            print("⚠️ Missing permission to delete messages.")
        except Exception as e:
            print(f"⚠️ Failed to delete command message: {e}")

        if theme and theme.lower() in self.tips:
            tip = random.choice(self.tips[theme.lower()])
            await ctx.send(f"💡 **{theme.title()} Tip:** {tip}")
        else:
            theme = random.choice(list(self.tips.keys()))
            tip = random.choice(self.tips[theme])
            await ctx.send(f"💡 **{theme.title()} Tip:** {tip}")
            # ✅ Delete the original command message


async def setup(bot):
    await bot.add_cog(BuildTips(bot))
