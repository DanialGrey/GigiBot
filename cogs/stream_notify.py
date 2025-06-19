import discord
from discord.ext import commands, tasks
import os
import aiohttp
import asyncio
import logging
from dotenv import load_dotenv
from datetime import datetime, timedelta

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
        self.last_youtube_check = datetime.min
        self.check_streams.start()
        print("[StreamNotify] Cog loaded.")

    def cog_unload(self):
        self.check_streams.cancel()

    @tasks.loop(minutes=3)
    async def check_streams(self):
        await self.bot.wait_until_ready()

        announce_channel_name = self.bot.config.get("ANNOUNCEMENT_CHANNEL", "announcements")
        announce_channel = discord.utils.get(self.bot.get_all_channels(), name=announce_channel_name)
        if not announce_channel:
            logging.warning("[StreamNotify] Announcement channel not found.")
            return

        # === TWITCH CHECK ===
        twitch_live, stream_title = await self.is_twitch_live()
        if twitch_live and not self.twitch_streaming:
            self.twitch_streaming = True
            embed = discord.Embed(
                title="🎮 Girldad is LIVE on Twitch!",
                description=f"**{stream_title}**\n[Watch Now](https://www.twitch.tv/{TWITCH_USERNAME})",
                color=discord.Color.purple()
            )
            embed.set_thumbnail(url=f"https://static-cdn.jtvnw.net/previews-ttv/live_user_{TWITCH_USERNAME.lower()}-640x360.jpg")
            embed.set_footer(text="Catch the stream before it's gone!")
            await announce_channel.send(embed=embed)
            logging.info(f"[StreamNotify] Twitch stream started: {stream_title}")

        elif not twitch_live and self.twitch_streaming:
            self.twitch_streaming = False
            embed = discord.Embed(
                title="🛑 Girldad has ended the Twitch stream.",
                color=discord.Color.red()
            )
            await announce_channel.send(embed=embed)
            logging.info("[StreamNotify] Twitch stream ended.")

        # === YOUTUBE CHECK ===
        if datetime.utcnow() - self.last_youtube_check >= timedelta(minutes=10):
            latest_video = await self.get_latest_youtube_video()
            if latest_video and latest_video["id"] != self.last_youtube_video_id:
                self.last_youtube_video_id = latest_video["id"]
                self.last_youtube_check = datetime.utcnow()
                embed = discord.Embed(
                    title="📺 New YouTube Upload!",
                    description=f"**{latest_video['title']}**\n[Watch here](https://www.youtube.com/watch?v={latest_video['id']})",
                    color=discord.Color.blue()
                )
                embed.set_thumbnail(url=f"https://i.ytimg.com/vi/{latest_video['id']}/hqdefault.jpg")
                embed.set_footer(text="Subscribe so you never miss a drop!")
                await announce_channel.send(embed=embed)
                logging.info(f"[StreamNotify] New YouTube video: {latest_video['title']}")

    async def is_twitch_live(self):
        if not self.twitch_token:
            await self.get_twitch_token()

        headers = {
            "Client-ID": TWITCH_CLIENT_ID,
            "Authorization": f"Bearer {self.twitch_token}"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://api.twitch.tv/helix/users?login={TWITCH_USERNAME}", headers=headers) as resp:
                    if resp.status == 401:
                        await self.get_twitch_token()
                        return await self.is_twitch_live()
                    data = await resp.json()
                    if "data" not in data or not data["data"]:
                        return False, None
                    user_id = data["data"][0]["id"]

                async with session.get(f"https://api.twitch.tv/helix/streams?user_id={user_id}", headers=headers) as resp:
                    if resp.status == 401:
                        await self.get_twitch_token()
                        return await self.is_twitch_live()
                    data = await resp.json()
                    if data.get("data"):
                        return True, data["data"][0].get("title", "Streaming now!")
                    return False, None
        except Exception as e:
            logging.error(f"[StreamNotify] Twitch check failed: {e}")
            return False, None

    async def get_twitch_token(self):
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "client_id": TWITCH_CLIENT_ID,
                    "client_secret": TWITCH_CLIENT_SECRET,
                    "grant_type": "client_credentials"
                }
                async with session.post("https://id.twitch.tv/oauth2/token", data=payload) as resp:
                    data = await resp.json()
                    self.twitch_token = data.get("access_token")
                    logging.info("[StreamNotify] Twitch token refreshed.")
        except Exception as e:
            logging.error(f"[StreamNotify] Failed to get Twitch token: {e}")

    async def get_latest_youtube_video(self):
        try:
            async with aiohttp.ClientSession() as session:
                url = (
                    f"https://www.googleapis.com/youtube/v3/search?"
                    f"key={YOUTUBE_API_KEY}&channelId={YOUTUBE_CHANNEL_ID}"
                    f"&part=snippet,id&order=date&maxResults=1"
                )
                async with session.get(url) as resp:
                    data = await resp.json()
                    items = data.get("items", [])
                    if not items:
                        return None

                    video = items[0]
                    if video.get("id", {}).get("kind") != "youtube#video":
                        return None

                    video_id = video["id"].get("videoId")
                    title = video["snippet"].get("title", "New Video")

                    if not video_id:
                        return None

                    return {"id": video_id, "title": title}
        except Exception as e:
            logging.error(f"[StreamNotify] YouTube check failed: {e}")
            return None

async def setup(bot):
    await bot.add_cog(StreamNotify(bot))
