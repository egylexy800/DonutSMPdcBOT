import discord
from discord.ext import commands
import apikeys

class automod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if any(word in message.content.lower() for word in apikeys.banned_words):
            await message.delete()

            log_channel = self.bot.get_channel(apikeys.discord_logs)
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

        await self.bot.process_commands(message)

async def setup(bot):
    await bot.add_cog(automod(bot))