import os
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
import apikeys

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.do_not_disturb)
    print("The bot is now ready for use!")
    print("-----------------------------")

@bot.command(name="shutdown")
@has_permissions(administrator=True)
async def shutdown_command(ctx):
    await ctx.send("```Shutting down...```")
    await bot.close()

async def load_extensions():
    initial_extensions = []
    
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            initial_extensions.append(f'cogs.{filename[:-3]}')

    for extension in initial_extensions:
        try:
            await bot.load_extension(extension)
        except Exception as e:
            print(f"Failed to load extension {extension}: {e}")

async def setup_hook():
    await load_extensions()

bot.setup_hook = setup_hook

bot.run(apikeys.bot_token)