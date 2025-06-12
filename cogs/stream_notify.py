import discord
from discord.ext import commands, tasks
import os
import aiohttp
import asyncio
import logging
from dotenv import load_dotenv

load_dotenv()

ANNOUNCE_CHANNEL_NAME = os.getenv("ANNOUNCEMENT_CHANNEL")
TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
TWITCH_USERNAME = os.getenv("TWITCH_USERNAME")
YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

class StreamNotify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.twitch_token = None
        self.last_youtube_video_id = None
        self.twitch_streaming = False
        self.check_streams.start()

    def cog_unload(self):
        self.check_streams.cancel()

    @tasks.loop(minutes=3)
    async def check_streams(self):
        await self.bot.wait_until_ready()

        announce_channel = discord.utils.get(self.bot.get_all_channels(), name=ANNOUNCE_CHANNEL_NAME)
        if not announce_channel:
            logging.warning("Announcement channel not found.")
            return

        # === TWITCH CHECK ===
        twitch_live, stream_title = await self.is_twitch_live()
        if twitch_live and not self.twitch_streaming:
            self.twitch_streaming = True
            await announce_channel.send(f"🎮 **Girldad is now LIVE on Twitch!**\n**{stream_title}**\nhttps://www.twitch.tv/{TWITCH_USERNAME}")
        elif not twitch_live:
            self.twitch_streaming = False

        # === YOUTUBE CHECK ===
        latest_video = await self.get_latest_youtube_video()
        if latest_video and latest_video != self.last_youtube_video_id:
            self.last_youtube_video_id = latest_video
            await announce_channel.send(f"📺 **New YouTube upload!**\nhttps://www.youtube.com/watch?v={latest_video}")

    async def is_twitch_live(self):
        if not self.twitch_token:
            await self.get_twitch_token()

        # Get user ID
        headers = {
            "Client-ID": TWITCH_CLIENT_ID,
            "Authorization": f"Bearer {self.twitch_token}"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.twitch.tv/helix/users?login={TWITCH_USERNAME}", headers=headers) as resp:
                data = await resp.json()
                if "data" not in data or not data["data"]:
                    return False, None
                user_id = data["data"][0]["id"]

            async with session.get(f"https://api.twitch.tv/helix/streams?user_id={user_id}", headers=headers) as resp:
                data = await resp.json()
                if data.get("data"):
                    return True, data["data"][0].get("title", "Streaming now!")
                return False, None

    async def get_twitch_token(self):
        async with aiohttp.ClientSession() as session:
            payload = {
                "client_id": TWITCH_CLIENT_ID,
                "client_secret": TWITCH_CLIENT_SECRET,
                "grant_type": "client_credentials"
            }
            async with session.post("https://id.twitch.tv/oauth2/token", data=payload) as resp:
                data = await resp.json()
                self.twitch_token = data.get("access_token")

    async def get_latest_youtube_video(self):
        async with aiohttp.ClientSession() as session:
            url = f"https://www.googleapis.com/youtube/v3/search?key={YOUTUBE_API_KEY}&channelId={YOUTUBE_CHANNEL_ID}&part=snippet,id&order=date&maxResults=1"
            async with session.get(url) as resp:
                data = await resp.json()
                items = data.get("items", [])
                if items:
                    video = items[0]
                    if video["id"].get("kind") == "youtube#video":
                        return video["id"].get("videoId")
                return None

def setup(bot):
    bot.add_cog(StreamNotify(bot))
