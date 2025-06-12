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

    def is_mod_or_apex():
        async def predicate(ctx):
            roles = [role.name for role in ctx.author.roles]
            return "Moderator" in roles or "Apex" in roles

        return commands.check(predicate)

    @commands.command(name="reactionrole")
    @is_mod_or_apex()
    async def reactionrole(self, ctx, channel: discord.TextChannel, *, emoji_role_pairs: str):
        """
        Usage:
        !reactionrole #channel emoji1 role1 emoji2 role2 ...
        Special command name 'game roles' anywhere in the string enables multi-select.
        """
        # Parse args: split emoji_role_pairs into tokens
        tokens = emoji_role_pairs.split()
        if len(tokens) % 2 != 0:
            await ctx.send("You must provide pairs of emoji and role names.")
            return

        # Detect if multi-select (e.g. "game roles" keyword)
        multi_select = "game roles" in emoji_role_pairs.lower()

        # Remove the 'game roles' text if present, so it doesn't mess role parsing
        cleaned_tokens = []
        skip_next = False
        for i, token in enumerate(tokens):
            if skip_next:
                skip_next = False
                continue
            # Skip "game" and "roles" tokens
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
                await ctx.send(f"Role '{role_name}' not found on this server.")
                return
            emoji_role_map[emoji] = role.id

        # Send message to channel
        description_lines = []
        for emoji, role_id in emoji_role_map.items():
            role = ctx.guild.get_role(role_id)
            description_lines.append(f"{emoji} : {role.name}")
        description = "\n".join(description_lines)

        message = await channel.send(
            f"React to get roles! {'(Multiple roles allowed)' if multi_select else '(Only one role at a time)'}\n\n{description}"
        )

        # Add reactions
        for emoji in emoji_role_map.keys():
            try:
                await message.add_reaction(emoji)
            except Exception as e:
                await ctx.send(f"Failed to add reaction {emoji}: {e}")

        # Save to json
        self.reaction_roles[str(message.id)] = {
            "emoji_role_map": emoji_role_map,
            "multi_select": multi_select
        }
        save_reaction_roles(self.reaction_roles)

        await ctx.send(f"Reaction role message created in {channel.mention}!")

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
