import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import has_permissions
import yt_dlp
import asyncio
import apikeys

class voicemusic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = {}  # Dictionary to store queues for different guilds
        self.now_playing = {}  # Store current playing song

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

    @nextcord.slash_command(name="join", description="Makes the bot join the voice channel that you're in!")
    async def join(self, interaction: nextcord.Interaction):
        if interaction.user.voice:
            channel = interaction.user.voice.channel
            await channel.connect()
            await interaction.response.send_message("```I successfully joined the voice channel.```")
        else:
            await interaction.response.send_message("```You are not in a voice channel!```", ephemeral=True)

    @nextcord.slash_command(name="leave", description="Makes the bot leave the voice channel!")
    async def leave(self, interaction: nextcord.Interaction):
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect()
            await interaction.response.send_message("```I left the voice channel.```")
        else:
            await interaction.response.send_message("```I am not in a voice channel!```", ephemeral=True)

    @nextcord.slash_command(name="play", description="Adds a song to the queue!")
    async def play(self, interaction: nextcord.Interaction, search_query: str):
        await interaction.response.defer()

        url, title = self.search_youtube(search_query)
        
        guild_id = interaction.guild.id
        if guild_id not in self.song_queue:
            self.song_queue[guild_id] = []
        
        self.song_queue[guild_id].append((url, title))

        await interaction.followup.send(f"```✅ {title} has been added to the queue!```")

        if not interaction.guild.voice_client:
            if interaction.user.voice:
                await interaction.user.voice.channel.connect()
            else:
                await interaction.followup.send("```❌ You must be in a voice channel! ❌```", ephemeral=True)
                return

        if not interaction.guild.voice_client.is_playing():
            await self.play_next(interaction.guild)

    async def play_next(self, guild):
        guild_id = guild.id
        if guild_id not in self.song_queue or len(self.song_queue[guild_id]) == 0:
            return  # No more songs in the queue

        url, title = self.song_queue[guild_id].pop(0)
        self.now_playing[guild_id] = title  # Store current song
        
        ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }
        vc = guild.voice_client

        if vc:
            source = nextcord.FFmpegOpusAudio(url, **ffmpeg_options)
            vc.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(self.check_queue(guild), self.bot.loop))
            
            channel = guild.system_channel or next((c for c in guild.text_channels if c.permissions_for(guild.me).send_messages), None)
            if channel:
                await channel.send(f"```🎶 Now playing: {title}```")

    async def check_queue(self, guild):
        await asyncio.sleep(2)  # Small delay before checking
        if guild.voice_client and not guild.voice_client.is_playing():
            await self.play_next(guild)

    @nextcord.slash_command(name="skip", description="Skips the current song!")
    @has_permissions(administrator=True)
    async def skip(self, interaction: nextcord.Interaction):
        if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
            interaction.guild.voice_client.stop()
            await interaction.response.send_message("```⏭️ Song skipped!```")
        else:
            await interaction.response.send_message("```⚠️ No song is currently playing!```")

    @skip.error
    async def skip_error(self, interaction: nextcord.Interaction, error):
        if isinstance(error, commands.MissingPermissions):
            await interaction.response.send_message("```❌ You need to be an admin to skip songs! ❌```", ephemeral=True)

def setup(bot):
    bot.add_cog(voicemusic(bot))