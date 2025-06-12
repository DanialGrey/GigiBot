import discord
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions, MissingPermissions
import re
from datetime import datetime, timedelta

class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.muted_users = {}
        self.banned_users = {}
        self.check_timeouts.start()

    @tasks.loop(minutes=1)
    async def check_timeouts(self):
        now = datetime.utcnow()
        for user_id, (guild_id, unmute_time) in list(self.muted_users.items()):
            if now >= unmute_time:
                guild = self.bot.get_guild(guild_id)
                member = guild.get_member(user_id)
                mute_role = discord.utils.get(guild.roles, name="Muted")
                if member and mute_role in member.roles:
                    await member.remove_roles(mute_role)
                    self.muted_users.pop(user_id)

        for user_id, (guild_id, unban_time) in list(self.banned_users.items()):
            if now >= unban_time:
                guild = self.bot.get_guild(guild_id)
                banned_users = await guild.bans()
                for ban_entry in banned_users:
                    if ban_entry.user.id == user_id:
                        await guild.unban(ban_entry.user)
                        self.banned_users.pop(user_id)
                        break

    async def log_action(self, ctx, message):
        log_channel = discord.utils.get(ctx.guild.text_channels, name="mod-log")
        if log_channel:
            await log_channel.send(message)

    @commands.command()
    @has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        await member.kick(reason=reason)
        await ctx.send(f"👢 {member.mention} has been kicked. Reason: {reason}")
        await self.log_action(ctx, f"👢 {member} kicked. Reason: {reason}")

    @commands.command()
    @has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, duration: int = 0, *, reason=None):
        await member.ban(reason=reason)
        await ctx.send(f"🔨 {member.mention} has been banned. Reason: {reason}")
        await self.log_action(ctx, f"🔨 {member} banned. Reason: {reason}")
        if duration > 0:
            self.banned_users[member.id] = (ctx.guild.id, datetime.utcnow() + timedelta(minutes=duration))

    @commands.command()
    @has_permissions(ban_members=True)
    async def unban(self, ctx, *, member_name):
        banned_users = await ctx.guild.bans()
        name, discriminator = member_name.split("#")
        for ban_entry in banned_users:
            user = ban_entry.user
            if user.name == name and user.discriminator == discriminator:
                await ctx.guild.unban(user)
                await ctx.send(f"🛡️ Unbanned {user.mention}")
                await self.log_action(ctx, f"🛡️ Unbanned {user}")
                return
        await ctx.send("❌ User not found.")

    @commands.command()
    @has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, duration: int = 0, *, reason=None):
        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not mute_role:
            mute_role = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(mute_role, speak=False, send_messages=False)
        await member.add_roles(mute_role)
        await ctx.send(f"🔇 {member.mention} has been muted. Reason: {reason}")
        await self.log_action(ctx, f"🔇 {member} muted. Reason: {reason}")
        if duration > 0:
            self.muted_users[member.id] = (ctx.guild.id, datetime.utcnow() + timedelta(minutes=duration))

    @commands.command()
    @has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if mute_role in member.roles:
            await member.remove_roles(mute_role)
            await ctx.send(f"🔊 {member.mention} has been unmuted.")
            await self.log_action(ctx, f"🔊 {member} unmuted")
        else:
            await ctx.send(f"❌ {member.mention} is not muted.")

    @commands.command(aliases=["purge"])
    @has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"🧹 Cleared {amount} messages.", delete_after=5)
        await self.log_action(ctx, f"🧹 Cleared {amount} messages in #{ctx.channel}")

    @commands.command()
    @has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int):
        await ctx.channel.edit(slowmode_delay=seconds)
        await ctx.send(f"🐌 Set slowmode to {seconds} seconds.")
        await self.log_action(ctx, f"🐌 Set slowmode in #{ctx.channel} to {seconds} seconds")

    @commands.command()
    @has_permissions(manage_channels=True)
    async def lock(self, ctx):
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send("🔒 Channel locked.")
        await self.log_action(ctx, f"🔒 Locked #{ctx.channel}")

    @commands.command()
    @has_permissions(manage_channels=True)
    async def unlock(self, ctx):
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = True
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send("🔓 Channel unlocked.")
        await self.log_action(ctx, f"🔓 Unlocked #{ctx.channel}")

    # Info commands
    @commands.command()
    async def userinfo(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        roles = ", ".join([r.mention for r in member.roles if r != ctx.guild.default_role])
        await ctx.send(embed=discord.Embed(title=f"👤 User Info: {member}", description=f"ID: {member.id}\nRoles: {roles}", color=discord.Color.blue()))

    @commands.command()
    async def roleinfo(self, ctx, *, role: discord.Role):
        await ctx.send(embed=discord.Embed(title=f"🎭 Role Info: {role.name}", description=f"ID: {role.id}\nMembers: {len(role.members)}", color=discord.Color.green()))

    @commands.command()
    async def serverinfo(self, ctx):
        guild = ctx.guild
        await ctx.send(embed=discord.Embed(title=f"🌐 Server Info: {guild.name}", description=f"ID: {guild.id}\nMembers: {guild.member_count}\nRoles: {len(guild.roles)}\nChannels: {len(guild.channels)}", color=discord.Color.purple()))

    # Anti-spam and filters
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Anti-Invite
        if re.search(r"(discord\.gg/|discord\.com/invite/)", message.content):
            await message.delete()
            await message.channel.send("🚫 Invite links are not allowed.", delete_after=5)

        # Anti-token grabbers
        if "grabify" in message.content or "iplogger" in message.content:
            await message.delete()
            await message.channel.send("🚫 Malicious links are not allowed.", delete_after=5)

        # Anti-caps spam
        if sum(1 for c in message.content if c.isupper()) > 15 and len(message.content) < 50:
            await message.delete()
            await message.channel.send("🚫 Too many capital letters. Please chill.", delete_after=5)

        # Text filter (example words)
        banned_words = ["badword1", "badword2"]
        if any(word in message.content.lower() for word in banned_words):
            await message.delete()
            await message.channel.send("🚫 That word isn't allowed here.", delete_after=5)

    @kick.error
    @ban.error
    @unban.error
    @mute.error
    @unmute.error
    @clear.error
    @slowmode.error
    @lock.error
    @unlock.error
    async def permission_error(self, ctx, error):
        if isinstance(error, MissingPermissions):
            await ctx.send("🚫 You don't have permission to do that.")


def setup(bot):
    bot.add_cog(Utilities(bot))
