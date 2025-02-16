import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions

class punishments(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        await member.ban(reason=reason)
        await ctx.send(f"```✅ User {member} has been banned. ✅```")
        
    @commands.command()
    @has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        await member.kick(reason=reason)
        await ctx.send(f"```✅ User {member} has been kicked. ✅```")
        
    @commands.command()
    @has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member, *, time: str, reason=None):
        try:
            time_seconds = int(time)
            timeout_duration = self.timedelta(seconds=time_seconds)
            
            await member.timeout(timeout_duration)
            await ctx.send(f"```✅User {member} has been muted for {time_seconds} seconds.✅```")
        except ValueError:
            await ctx.send("```❌ Invalid time format. Please provide a valid number of seconds.❌```")
            
    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'member':
                await ctx.send(f"```⚠️ member is a required argument that is missing.```")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("```❌ You don't have permission to ban users! ❌```")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("```❌ I don't have permission to ban users! ❌```")
        else:
            await ctx.send(f"```⚠️ {error}```")

    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("```❌ You don't have permission to kick users! ❌```")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("```❌ I don't have permission to kick users! ❌```")
        else:
            await ctx.send(f"```⚠️ {error}```")

async def setup(bot):
    await bot.add_cog(punishments(bot))