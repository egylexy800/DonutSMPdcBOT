import nextcord
from nextcord.ext import commands
import yt_dlp
import asyncio

checkmark = "<:checkmark:1342071259567230976>"
music = "<a:music:1342229973729017956>"
arrow = "<a:purple_arrow:1342233471619432519>"
crossmark = "<:crossmark:1342071086044680322>"

class VoiceMusic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = {}
        self.now_playing = {}

    def search_youtube(self, query):
        ydl_opts = {
            "format": "bestaudio",
            "noplaylist": True,
            "default_search": "ytsearch1",
            "quiet": True,
            "extract_flat": False,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            video = info["entries"][0] if "entries" in info else info
            return video["url"], video["title"]

    @nextcord.slash_command(
        name="join",
        description="Makes the bot join the voice channel that you're in!",
        default_member_permissions=nextcord.Permissions(mute_members=True),
    )
    async def join(self, interaction: nextcord.Interaction):

        await interaction.response.defer()

        if interaction.user.voice:
            channel = interaction.user.voice.channel
            await channel.connect()

            embed = nextcord.Embed(
                title=f"{checkmark} Connected to Voice Channel {checkmark}",
                description=f"I have successfully joined **{channel.name}** and I'm ready to play! \n`Use /play to add songs to queue!`",
                color=nextcord.Color.green(),
                timestamp=nextcord.utils.utcnow(),
            )
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            embed.set_footer(
                text=f"Requested by {interaction.user.name}",
                icon_url=interaction.user.display_avatar.url,
            )

            await interaction.followup.send(embed=embed)

        else:
            novoice_embed = nextcord.Embed(
                title=f"{crossmark} You are not in a voice channel! {crossmark}",
                description="You must be in a voice channel to use this command! \n`────────────────────────`",
                color=nextcord.Color.red(),
                timestamp=nextcord.utils.utcnow(),
            )
            novoice_embed.set_thumbnail(url=self.bot.user.display_avatar.url)

            await interaction.followup.send(embed=novoice_embed)

    @nextcord.slash_command(
        name="leave",
        description="Makes the bot leave the voice channel!",
        default_member_permissions=nextcord.Permissions(mute_members=True),
    )
    async def leave(self, interaction: nextcord.Interaction):
        await interaction.response.defer()

        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect()

            embed = nextcord.Embed(
                title=f"{checkmark} `Left Voice Channel` {checkmark}",
                description="I have successfully disconnected from the voice channel. \n`────────────────────────`",
                color=nextcord.Color.red(),
                timestamp=nextcord.utils.utcnow(),
            )
            embed.set_footer(
                text=f"Requested by {interaction.user.name}",
                icon_url=interaction.user.display_avatar.url,
            )

            await interaction.followup.send(embed=embed)
        else:
            novoice_embed = nextcord.Embed(
                title=f"{crossmark} I'm not in a voice channel! {crossmark}",
                description="I'm not in a voice channel right now! \n`────────────────────────`",
                color=nextcord.Color.red(),
                timestamp=nextcord.utils.utcnow(),
            )
            novoice_embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            await interaction.followup.send(embed=novoice_embed)

    @nextcord.slash_command(
        name="play",
        description="Adds a song to the queue!",
        default_member_permissions=None,
    )
    async def play(self, interaction: nextcord.Interaction, search_query: str):
        await interaction.response.defer()

        url, title = self.search_youtube(search_query)

        guild_id = interaction.guild.id
        if guild_id not in self.song_queue:
            self.song_queue[guild_id] = []

        self.song_queue[guild_id].append((url, title))

        added_embed = nextcord.Embed(
            title=f"{checkmark} Song added to queue! {checkmark}",
            description=f"{music} **{title}** has been added to the queue!{music} \n`────────────────────────`",
            color=nextcord.Color.green(),
            timestamp=nextcord.utils.utcnow(),
        )
        added_embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        added_embed.set_footer(
            text=f"Requested by {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
        await interaction.followup.send(embed=added_embed)

        if not interaction.guild.voice_client:
            if interaction.user.voice:
                await interaction.user.voice.channel.connect()
            else:
                novoice_embed = nextcord.Embed(
                    title=f"{crossmark} You are not in a voice channel! {crossmark}",
                    description="You must be in a voice channel to use this command! \n`────────────────────────`",
                    color=nextcord.Color.red(),
                    timestamp=nextcord.utils.utcnow(),
                )
                novoice_embed.set_thumbnail(url=self.bot.user.display_avatar.url)
                await interaction.followup.send(embed=novoice_embed)
                return

        if not interaction.guild.voice_client.is_playing():
            await self.play_next(interaction.guild)

    async def play_next(self, guild):
        guild_id = guild.id
        if guild_id not in self.song_queue or len(self.song_queue[guild_id]) == 0:
            return

        url, title = self.song_queue[guild_id].pop(0)
        self.now_playing[guild_id] = title

        ffmpeg_options = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn",
        }
        vc = guild.voice_client

        if vc:
            source = nextcord.FFmpegOpusAudio(url, **ffmpeg_options)
            vc.play(
                source,
                after=lambda e: asyncio.run_coroutine_threadsafe(
                    self.check_queue(guild), self.bot.loop
                ),
            )

            channel = guild.system_channel or next(
                (
                    c
                    for c in guild.text_channels
                    if c.permissions_for(guild.me).send_messages
                ),
                None,
            )
            if channel:
                await channel.send(f" {music} `Now playing: {title}` {music}")

    async def check_queue(self, guild):
        await asyncio.sleep(2)
        if guild.voice_client and not guild.voice_client.is_playing():
            await self.play_next(guild)

    @nextcord.slash_command(
        name="skip",
        description="Skips the current song!",
        default_member_permissions=nextcord.Permissions(administrator=True),
    )
    async def skip(self, interaction: nextcord.Interaction):
        await interaction.response.defer()

        vc = interaction.guild.voice_client

        if vc and vc.is_playing():
            vc.stop()
            embed = nextcord.Embed(
                title=f"{checkmark} Skipped! {checkmark}",
                description=f"{arrow}Song has been skipped by {interaction.user.mention} {arrow}! \nNow playing:{music} {self.now_playing[interaction.guild.id]} {music} \n`────────────────────────`",
                color=nextcord.Color.green(),
                timestamp=nextcord.utils.utcnow(),
            )
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            await interaction.followup.send(embed=embed)
        else:
            nosong = nextcord.Embed(
                title=f"{crossmark} No song is currently playing! {crossmark}",
                description="There is no song currently playing! \n`Use /play to add songs to queue!` \n`────────────────────────`",
                color=nextcord.Color.red(),
                timestamp=nextcord.utils.utcnow(),
            )
            nosong.set_thumbnail(url=self.bot.user.display_avatar.url)
            await interaction.followup.send(embed=nosong)

    @join.error
    async def join_error(self, interaction: nextcord.Interaction, error: Exception):
        await interaction.send(f"```⚠️ {error}```", ephemeral=True)

    @leave.error
    async def leave_error(self, interaction: nextcord.Interaction, error: Exception):
        await interaction.send(f"```⚠️ {error}```", ephemeral=True)

    @play.error
    async def play_error(self, interaction: nextcord.Interaction, error: Exception):
        await interaction.send(f"```⚠️ {error}```", ephemeral=True)

    @skip.error
    async def skip_error(self, interaction: nextcord.Interaction, error: Exception):
        await interaction.send(f"```⚠️ {error}```", ephemeral=True)


def setup(bot):
    bot.add_cog(VoiceMusic(bot))