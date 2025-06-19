import discord
from discord.ext import commands
import json
import os

REACTION_ROLES_FILE = "reaction_roles.json"


def load_reaction_roles():
    if os.path.exists(REACTION_ROLES_FILE):
        with open(REACTION_ROLES_FILE, "r") as f:
            return json.load(f)
    return {}


def save_reaction_roles(data):
    with open(REACTION_ROLES_FILE, "w") as f:
        json.dump(data, f, indent=4)


class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reaction_roles = load_reaction_roles()
        print("[ReactionRoles] Cog loaded.")

    def is_mod_or_apex():
        async def predicate(ctx):
            roles = [role.name for role in ctx.author.roles]
            return "Moderator" in roles or "Apex" in roles

        return commands.check(predicate)

    @commands.command(name="testping")
    async def testping(self, ctx):
        print("[ReactionRoles] testping command triggered.")
        await ctx.send("Pong!")

    @commands.command(name="reactionrole")
    @is_mod_or_apex()
    async def reactionrole(self, ctx, *, emoji_role_pairs: str):
        # ✅ Only allow usage in a specific channel
        allowed_channel_name = "get_roles"
        if ctx.channel.name != allowed_channel_name:
            await ctx.send(f"⚠️ This command can only be used in #{allowed_channel_name}.", delete_after=5)
            return


        print("[ReactionRoles] Command invoked.")
        tokens = emoji_role_pairs.split()
        if len(tokens) % 2 != 0:
            await ctx.send("❌ You must provide pairs of emoji and role names.", delete_after=10)
            return

        multi_select = "game roles" in emoji_role_pairs.lower()

        # Clean out "game roles"
        cleaned_tokens = []
        skip_next = False
        for i, token in enumerate(tokens):
            if skip_next:
                skip_next = False
                continue
            if token.lower() == "game" and i + 1 < len(tokens) and tokens[i + 1].lower() == "roles":
                skip_next = True
                continue
            cleaned_tokens.append(token)

        tokens = cleaned_tokens
        emoji_role_map = {}
        for i in range(0, len(tokens), 2):
            emoji = tokens[i]
            role_name = tokens[i + 1]
            role = discord.utils.get(ctx.guild.roles, name=role_name)
            if role is None:
                await ctx.send(f"❌ Role '{role_name}' not found.", delete_after=10)
                return
            emoji_role_map[emoji] = role.id

            # ✅ Delete the original command message
            try:
                await ctx.message.delete()
            except discord.Forbidden:
                print("⚠️ Missing permission to delete messages.")
            except Exception as e:
                print(f"⚠️ Failed to delete command message: {e}")

        # 📩 Send message in the same channel the command was run
        description_lines = [f"{emoji} : {ctx.guild.get_role(role_id).name}" for emoji, role_id in
                             emoji_role_map.items()]
        description = "\n".join(description_lines)

        message = await ctx.send(
            f"React to get roles! {'(Multiple roles allowed)' if multi_select else '(Only one role at a time)'}\n\n{description}"
        )

        for emoji in emoji_role_map.keys():
            try:
                await message.add_reaction(emoji)
            except Exception as e:
                print(f"⚠️ Failed to add reaction {emoji}: {e}")

        self.reaction_roles[str(message.id)] = {
            "emoji_role_map": emoji_role_map,
            "multi_select": multi_select
        }
        save_reaction_roles(self.reaction_roles)

        print("[ReactionRoles] Reaction role message posted.")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id:
            return

        msg_id = str(payload.message_id)
        if msg_id not in self.reaction_roles:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            return

        emoji = str(payload.emoji)
        rr_data = self.reaction_roles[msg_id]
        emoji_role_map = rr_data["emoji_role_map"]
        multi_select = rr_data.get("multi_select", False)

        if emoji not in emoji_role_map:
            return

        role_id = emoji_role_map[emoji]
        role = guild.get_role(role_id)
        member = guild.get_member(payload.user_id)
        if member is None or role is None:
            return

        # If not multi select, remove other roles from this reaction role set
        if not multi_select:
            for e, r_id in emoji_role_map.items():
                if r_id != role_id and r_id in [r.id for r in member.roles]:
                    try:
                        await member.remove_roles(guild.get_role(r_id))
                    except Exception:
                        pass

        try:
            await member.add_roles(role)
        except Exception:
            pass

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.user_id == self.bot.user.id:
            return

        msg_id = str(payload.message_id)
        if msg_id not in self.reaction_roles:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            return

        emoji = str(payload.emoji)
        rr_data = self.reaction_roles[msg_id]
        emoji_role_map = rr_data["emoji_role_map"]

        if emoji not in emoji_role_map:
            return

        role_id = emoji_role_map[emoji]
        role = guild.get_role(role_id)
        member = guild.get_member(payload.user_id)
        if member is None or role is None:
            return

        try:
            await member.remove_roles(role)
        except Exception:
            pass


async def setup(bot):
    await bot.add_cog(ReactionRoles(bot))
