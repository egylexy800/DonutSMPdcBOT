import discord
from discord.ext import commands
from apikeys import *
from discord import member
from discord import Permissions
from discord.ext.commands import has_permissions, MissingPermissions
from datetime import timedelta
import yt_dlp
import asyncio
import signal
import sys

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

queue = []

@bot.command(name="shutdown")
@has_permissions(administrator=True)
async def shutdown_command(ctx):
    await ctx.send("```Shutting down...```")
    await bot.close()


def search_youtube(query):
    """Search YouTube and return the audio URL and title for streaming."""
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

@bot.command()
async def play(ctx, *, search_query):
    """Plays audio from YouTube directly without downloading."""
    url, title = search_youtube(search_query)
    queue.append((url, title))
    await ctx.send(f"```✅ {title} has been added to the queue!```")
    
    if not ctx.voice_client or not ctx.voice_client.is_connected():
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send("```❌ You must be in a voice channel! ❌```")
            return

    if not ctx.voice_client.is_playing():
        await play_next(ctx)

async def play_next(ctx):
    """Plays the next song in the queue if available."""
    if queue:
        url, title = queue.pop(0)
        ffmpeg_options = {
         'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
         'options': '-vn'
         }
        ctx.voice_client.play(
            discord.FFmpegOpusAudio(url, executable="ffmpeg", before_options=ffmpeg_options, options="-filter:a 'volume=0.3'"),
            after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop)
        )
        await ctx.send(f"```🎶 Now playing: {title}```")
    else:
        await ctx.send("```Queue is empty!```")


@bot.command()
@has_permissions(administrator=True)
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("```⏭️ Song skipped by an admin!```")
        await play_next(ctx)
    else:
        await ctx.send("```⚠️ No song is currently playing!```")

@skip.error
async def skip_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("```❌ You need to be an admin to skip songs! ❌```")

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.do_not_disturb)
    print("The bot is now ready for use!")
    print("-----------------------------")

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(Welcome)
    if channel:
        embed = discord.Embed(
            title="Welcome to the server! 🎉",
            description=f"Hey {member.mention}, we're glad to have you here! Make sure to check out the rules and have fun!",
            color=discord.Color.purple()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.set_image(url="https://t3.ftcdn.net/jpg/08/27/83/92/360_F_827839207_iiFo5GnspGvSrH3Mg2viMnG2cAhddDgM.jpg")
        embed.set_footer(text=f"Enjoy your stay, {member.name}!", icon_url=member.avatar.url if member.avatar else member.default_avatar.url)
        await channel.send(embed=embed)

@bot.command(pass_context = True)
async def join(ctx):
    if (ctx.author.voice):
        channel = ctx.message.author.voice.channel
        await channel.connect()
        await ctx.send(f"```I succesfully joined the voice channel.```")
    else:
        await ctx.send(f"```You are not in a voice channel, you must be in a voice channel to run this command!```")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("```I left the voice channel.```")
    else:
        await ctx.send("```I am not in a voice channel!```")

@bot.command()
@has_permissions(moderate_members=True)
async def mute(ctx, member: discord.Member, *, time: str, reason=None):
    try:
        # Convert time string to a timedelta object
        time_seconds = int(time)  # Assuming the time is passed as a number of seconds
        timeout_duration = timedelta(seconds=time_seconds)
        
        await member.timeout(timeout_duration)
        await ctx.send(f"```✅User {member} has been muted for {time_seconds} seconds.✅```")
    except ValueError:
        await ctx.send("```❌ Invalid time format. Please provide a valid number of seconds.❌```")

@bot.command()
@has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f"```✅ User {member} has been kicked. ✅```")

@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("```❌ You don't have permission to kick users! ❌```")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("```❌ I don't have permission to kick users! ❌```")
    else:
        await ctx.send(f"```⚠️ {error}```")

@bot.command()
@has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f"```✅ User {member} has been banned. ✅```")

@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"```❌ You don't have permission to ban users! ❌```")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send(f"```❌ I don't have permission to ban users! ❌```")
    else:
        await ctx.send(f"```⚠️ {error}```")

@bot.command()
@has_permissions(manage_roles=True)
async def addRole(ctx, user: discord.Member, *, role: discord.Role):
    if role in user.roles:
        await ctx.send(f"```⚠️ {user.mention} already has the {role} role! ⚠️```")
    else:
        await user.add_roles(role)
        await ctx.send(f"```✅ The role {role} has been added to {user.mention}! ✅```")        

@addRole.error
async def role_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"```❌ You do not have permissions to use this command! ❌```")
    else:
        await ctx.send(f"```⚠️ {error}```")

@bot.command()
@has_permissions(manage_roles=True)
async def removeRole(ctx, user: discord.Member, *, role: discord.Role):
    if role in user.roles:
        await user.remove_roles(role)
        await ctx.send(f"```✅ The role {role} has been removed from {user.mention}! ✅```")
    else:
        await ctx.send(f"```⚠️ {user.mention} does not have the {role} role! ⚠️```")        

@removeRole.error
async def role_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"```❌ You do not have permissions to use this command! ❌```")
    else:
        await ctx.send(f"```⚠️ An error occurred: {error}```")

@bot.command()
@has_permissions(administrator = True)
async def purge(ctx, amount: int):
    if amount <= 0:
        await ctx.send(f"```⚠️ Please specify a number greater than 0! ⚠️```")
    else:
      deleted = await ctx.channel.purge(limit=amount + 1)
      await ctx.send(f"```✅ Deleted {len(deleted) - 1} messages! ✅```", delete_after=3)

@purge.error
async def purge_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"```❌ You do not have permissions to use this command! ❌```")
    else:
        await ctx.send(f"```⚠️ {error}```")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if any(word in message.content.lower() for word in banned_words):
        await message.delete()

        log_channel = bot.get_channel(log_channel_id)
        if log_channel:
            embed = discord.Embed(
                title="Automod Log",
                description=f"**User:** {message.author.mention}\n"
                            f"**Message:** {message.content}",
                color=discord.Color.orange()
            )
            await log_channel.send(embed=embed)

        try:
            warn_embed = discord.Embed(
                title="⚠️ Warning Issued",
                description="You have been warned for using inappropriate language.",
                color=discord.Color.orange()
            )
            warn_embed.add_field(name="🔹 Server", value=message.guild.name, inline=False)
            warn_embed.add_field(name="📝 Your Message", value=message.content, inline=False)
            warn_embed.set_footer(text="Please follow the server rules to avoid further actions.")

            await message.author.send(embed=warn_embed)
        except discord.Forbidden:
            pass

        await message.channel.send("Don't send that again!")

    await bot.process_commands(message)


bot.run(token)