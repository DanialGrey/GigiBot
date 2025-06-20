import discord
from discord.ext import commands
from discord.ext.commands import BucketType, cooldown, CommandOnCooldown
from dotenv import load_dotenv
from rapidfuzz import fuzz
import os
import json
from datetime import datetime

load_dotenv()

SUGGESTION_CHANNEL_ID = int(os.getenv("SUGGESTION_CHANNEL_ID", 0))
FALLBACK_CHANNEL_NAME = "suggestions"
SUGGESTIONS_FILE = "suggestions.json"
SIMILARITY_THRESHOLD = 85  # percent

class Suggestions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.suggestion_channel_id = SUGGESTION_CHANNEL_ID
        self.fallback_channel_name = FALLBACK_CHANNEL_NAME

    @commands.command(name="suggest")
    @cooldown(1, 900, BucketType.user)  # 15 minutes
    async def suggest(self, ctx, *, suggestion: str):
        """Submit a suggestion (15 min cooldown). Must be in the suggestion channel."""

        if not self._is_valid_channel(ctx):
            await ctx.send(
                f"🚫 This command can only be used in <#{self.suggestion_channel_id or self.fallback_channel_name}>.",
                delete_after=8
            )
            try:
                await ctx.message.delete()
            except discord.Forbidden:
                pass
            return

        try:
            await ctx.message.delete()
        except Exception as e:
            print(f"[Suggest Command] Error deleting user message: {e}")

        # ✅ Check for duplicates
        if self._is_duplicate_suggestion(suggestion):
            await ctx.send("⚠️ That suggestion is too similar to an existing one. Try rewording or submitting a new idea!", delete_after=10)
            return

        # ✅ Create and send embed
        embed = discord.Embed(
            title="📬 New Suggestion",
            description=discord.utils.escape_markdown(suggestion),
            color=discord.Color(0xf57ef3),
            timestamp=datetime.utcnow()
        )
        embed.set_author(
            name=ctx.author.display_name,
            icon_url=ctx.author.avatar.url if ctx.author.avatar else discord.Embed.Empty
        )
        embed.set_footer(text=f"User ID: {ctx.author.id}")

        try:
            suggestion_message = await ctx.send(embed=embed)
            await suggestion_message.add_reaction("👍")
            await suggestion_message.add_reaction("👎")
        except discord.Forbidden:
            await ctx.send("⚠️ I don't have permission to send embeds or add reactions here.")
            return

        # ✅ Save to file
        await self._store_suggestion(
            user=ctx.author,
            suggestion_text=suggestion,
            timestamp=datetime.utcnow().isoformat()
        )

    @suggest.error
    async def suggest_error(self, ctx, error):
        if isinstance(error, CommandOnCooldown):
            minutes = int(error.retry_after // 60)
            seconds = int(error.retry_after % 60)
            await ctx.send(
                f"⏳ You're on cooldown! Try again in {minutes}m {seconds}s.",
                delete_after=8
            )
        else:
            raise error  # re-raise unexpected errors for debugging

    def _is_valid_channel(self, ctx):
        return (
            (self.suggestion_channel_id and ctx.channel.id == self.suggestion_channel_id) or
            (not self.suggestion_channel_id and ctx.channel.name == self.fallback_channel_name)
        )

    def _is_duplicate_suggestion(self, new_suggestion):
        if not os.path.exists(SUGGESTIONS_FILE):
            return False

        try:
            with open(SUGGESTIONS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return False

        for entry in data:
            existing = entry.get("suggestion", "")
            similarity = fuzz.token_set_ratio(new_suggestion, existing)
            if similarity >= SIMILARITY_THRESHOLD:
                print(f"⚠️ Similar suggestion detected: {similarity}% match with: {existing}")
                return True

        return False

    async def _store_suggestion(self, user, suggestion_text, timestamp):
        data = []
        if os.path.exists(SUGGESTIONS_FILE):
            try:
                with open(SUGGESTIONS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                print("⚠️ Could not parse suggestions.json. Starting fresh.")

        data.append({
            "user_id": user.id,
            "user_name": user.name,
            "suggestion": suggestion_text,
            "timestamp": timestamp
        })

        with open(SUGGESTIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

async def setup(bot):
    await bot.add_cog(Suggestions(bot))
