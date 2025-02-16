import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions

class other(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @has_permissions(manage_roles=True)
    async def addRole(self, ctx, user: discord.Member, *, role: discord.Role):
        if role in user.roles:
            await ctx.send(f"```⚠️ {user.mention} already has the {role} role! ⚠️```")
        else:
            await user.add_roles(role)
            await ctx.send(f"```✅ The role {role} has been added to {user.mention}! ✅```")  

    @commands.command()
    @has_permissions(manage_roles=True)
    async def removeRole(self, ctx, user: discord.Member, *, role: discord.Role):
        if role in user.roles:
            await user.remove_roles(role)
            await ctx.send(f"```✅ The role {role} has been removed from {user.mention}! ✅```")
        else:
            await ctx.send(f"```⚠️ {user.mention} does not have the {role} role! ⚠️```")
            
    @commands.command()
    @has_permissions(administrator = True)
    async def purge(self, ctx, amount: int):
        if amount <= 0:
            await ctx.send(f"```⚠️ Please specify a number greater than 0! ⚠️```")
        else:
            deleted = await ctx.channel.purge(limit=amount + 1)
            await ctx.send(f"```✅ Deleted {len(deleted) - 1} messages! ✅```", delete_after=3)
            
    @addRole.error
    async def role_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(f"```❌ You do not have permissions to use this command! ❌```")
        else:
            await ctx.send(f"```⚠️ {error}```")

    @removeRole.error
    async def role_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(f"```❌ You do not have permissions to use this command! ❌```")
        else:
            await ctx.send(f"```⚠️ An error occurred: {error}```")
    
    @purge.error
    async def purge_error(ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(f"```❌ You do not have permissions to use this command! ❌```")
        else:
            await ctx.send(f"```⚠️ {error}```")

async def setup(bot):
    await bot.add_cog(other(bot))