import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import has_permissions
import yt_dlp
import asyncio
import apikeys

class voicemusic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def search_youtube(self, query):
        ydl_opts = {
            "format": "bestaudio",
            "noplaylist": True,
            "default_search": "ytsearch1",
            "quiet": True,
            "extract_flat": False
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            video = info["entries"][0] if "entries" in info else info
            return video["url"], video["title"]
    
    @commands.command(pass_context=True)
    async def join(self, ctx):
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
            await ctx.send("```I successfully joined the voice channel.```")
        else:
            await ctx.send("```You are not in a voice channel! You must be in a voice channel to run this command.```")
    
    @commands.command()
    async def leave(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("```I left the voice channel.```")
        else:
            await ctx.send("```I am not in a voice channel!```")

    @commands.command()
    async def play(self, ctx, *, search_query):
        url, title = self.search_youtube(search_query)
        apikeys.queue.append((url, title))
        await ctx.send(f"```✅ {title} has been added to the queue!```")
        
        if not ctx.voice_client or not ctx.voice_client.is_connected():
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("```❌ You must be in a voice channel! ❌```")
                return

        if not ctx.voice_client.is_playing():
            await self.play_next(ctx)

    async def play_next(self, ctx):
        if apikeys.queue:
            url, title = apikeys.queue.pop(0)
            ffmpeg_options = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                'options': '-vn'
            }
            ctx.voice_client.play(
                nextcord.FFmpegOpusAudio(url, executable="ffmpeg", before_options=ffmpeg_options, options="-filter:a 'volume=0.3'"),
                after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop)
            )
            await ctx.send(f"```🎶 Now playing: {title}```")
        else:
            await ctx.send("```Queue is empty!```")
    
    @commands.command()
    @has_permissions(administrator=True)
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("```⏭️ Song skipped by an admin!```")
            await self.play_next(ctx)
        else:
            await ctx.send("```⚠️ No song is currently playing!```")
    
    @skip.error
    async def skip_error(ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("```❌ You need to be an admin to skip songs! ❌```")

def setup(bot):
    bot.add_cog(voicemusic(bot))