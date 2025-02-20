import nextcord
from nextcord.ext import commands
import apikeys
import aiohttp
import os

intents = nextcord.Intents.default()
intents.message_content = True
intents.members = True
intents.dm_messages = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    await bot.change_presence(status=nextcord.Status.do_not_disturb)
    

    print(f"Logged in as {bot.user}")
    print("The bot is now ready for use!")
    print("-----------------------------")

@bot.slash_command(
    name="shutdown",
    description="Shuts down the bot.",
    default_member_permissions=nextcord.Permissions(administrator=True)
    )
async def shutdown(interaction: nextcord.Interaction):
    await interaction.send("```Shutting down bot...```")
    await bot.close()
    await aiohttp.ClientSession().close()

initial_extension = []

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        initial_extension.append("cogs."+ filename[:-3])
        
if __name__ == "__main__":
    for extension in initial_extension:
        bot.load_extension(extension)

bot.run(apikeys.bot_token)