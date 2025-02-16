import os
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
import asyncio
import logging
import apikeys

logging.basicConfig(level=logging.INFO) 

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

async def load_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
    async with bot:
        await load_cogs()
        await bot.start(apikeys.bot_token)

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("\nBot manually stopped. Exiting cleanly...")