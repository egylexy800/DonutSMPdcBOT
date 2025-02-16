import nextcord
from nextcord.ext import commands
import apikeys
import logging

intents = nextcord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    await bot.change_presence(status=nextcord.Status.do_not_disturb)
    print("The bot is now ready for use!")
    print("-----------------------------")

if __name__ == "__main__":
    bot.load_extension('cogs.automod')
    bot.load_extension('cogs.other')
    bot.load_extension('cogs.punishments')
    bot.load_extension('cogs.voicemusic')
    bot.load_extension('cogs.welcome')

bot.run(apikeys.bot_token)