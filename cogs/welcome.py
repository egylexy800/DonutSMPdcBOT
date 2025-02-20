import nextcord
from nextcord.ext import commands

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
            
    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = self.bot.get_channel(1327579220351909919)
        if channel:
            embed = nextcord.Embed(
                title="Welcome to the server! 🎉",
                description=f"Hey {member.mention}, we're glad to have you here! Make sure to check out the rules and have fun!",
                color=nextcord.Color.purple()
            )
            embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
            embed.set_image(url="https://t3.ftcdn.net/jpg/08/27/83/92/360_F_827839207_iiFo5GnspGvSrH3Mg2viMnG2cAhddDgM.jpg")
            embed.set_footer(text=f"Enjoy your stay, {member.name}!", icon_url=member.avatar.url if member.avatar else member.default_avatar.url)
            await channel.send(f"||{member.mention}||", embed=embed)

def setup(bot):
    bot.add_cog(Welcome(bot))