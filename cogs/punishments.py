import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import has_permissions, MissingPermissions
from datetime import timedelta

waringemoji = "<:securitywarning:1342067614293299235>"
checkmark = "<:checkmark:1342071259567230976>"

class punishments(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(
        name="ban",
        description="Bans the specified member.",
        default_member_permissions=nextcord.Permissions(ban_members=True)
    )
    async def ban(self, interaction: nextcord.Interaction, member: nextcord.User, *, reason=None):
        await interaction.response.defer(ephemeral=True)

        guild_member = interaction.guild.get_member(member.id)
        reason = reason or "No reason provided."
        
        private_embed = nextcord.Embed(
            title=f"{waringemoji} `User Banned` {waringemoji}",
            description=f"You have been banned from Donutsmp Hangout | Egylexy's Giveaways. \nReason: **{reason}** \nIf you believe this was a mistake, please contact a staff member. \n`─────────────────────`",
            color=nextcord.Color.red(),
            timestamp=nextcord.utils.utcnow()
        )
        private_embed.set_footer(text=f"Banned by {interaction.user.name}", icon_url=interaction.user.display_avatar.url)

        try:
            await member.send(embed=private_embed)
            await member.send("```This is an automated message, Do not reply. ```")
        except nextcord.Forbidden as e:
            await interaction.followup.send(f"⚠️ Could not send a DM to {member.mention} (They may have DMs disabled). Error: {e}", ephemeral=True)
        
        await guild_member.ban(reason=reason)

        embed = nextcord.Embed(
            title=f"{waringemoji} `User Banned` {waringemoji}",
            description=f"{guild_member.mention} has been banned from the server.\nReason: **{reason}** \n────────────",
            color=nextcord.Color.red(),
            timestamp=nextcord.utils.utcnow()
        )
        embed.set_thumbnail(url=guild_member.display_avatar.url)
        embed.set_footer(text=f"Banned by {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
        
        await interaction.followup.send(f"{checkmark}`Succesfully banned`{checkmark}")
        await interaction.channel.send(embed=embed)
         

        
    @nextcord.slash_command(
        name="kick",
        description="Kicks the specified member.",
        default_member_permissions=nextcord.Permissions(kick_members=True)
        )
    async def kick(self, interaction:nextcord.Interaction, member: nextcord.User, *, reason=None):
        
        await interaction.response.defer(ephemeral=True)
                
        guild_member = interaction.guild.get_member(member.id)
        
        await guild_member.kick(reason=reason)
        embed = nextcord.Embed(
                title=f"{waringemoji} `User Kicked` {waringemoji}",
                description=f"{guild_member.mention} has been kicked from the server.\nReason: **{reason}** \n────────────",
                color=nextcord.Color.red(),
                timestamp=nextcord.utils.utcnow()
                )
        embed.set_thumbnail(url=guild_member.display_avatar.url)
        embed.set_footer(text=f"Kicked by {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
        await interaction.followup.send(f"{checkmark}`Succesfully kicked`{checkmark}")
        await interaction.channel.send(embed=embed)
        
    @nextcord.slash_command(
        name="mute",
        description="Mutes the specified member. You can use Minutes, Hours, or days.",
        default_member_permissions=nextcord.Permissions(moderate_members=True)
    )
    async def mute(self, interaction: nextcord.Interaction, member: nextcord.User, *, time: str, reason=None):
        await interaction.response.defer(ephemeral=True)
        
        if interaction.user.top_role <= member.top_role:
            await interaction.followup.send("```❌ You cannot mute someone with an equal or higher role. ❌```", ephemeral=True)
            return
        
        guild_member = interaction.guild.get_member(member.id)

        try:
            unit = time[-1].lower()
            amount = int(time[:-1])
        except (ValueError, IndexError):
            await interaction.followup.send("```❌ Invalid time format. Please use a number followed by a unit (m for minutes, h for hours, or d for days). ❌```", delete_after=3)
            return

        if unit == 'm':
            seconds = amount * 60
        elif unit == 'h':
            seconds = amount * 3600
        elif unit == 'd':
            seconds = amount * 86400
        else:
            await interaction.followup.send("```❌ Invalid time unit. Use m for minutes, h for hours, or d for days. ❌```", delete_after=3)
            return

        timeout_duration = timedelta(seconds=seconds)
        await guild_member.timeout(timeout_duration, reason=reason)
        embed = nextcord.Embed(
                title=f"{waringemoji} `User Muted` {waringemoji}",
                description=f"{guild_member.mention} has been muted for **{amount}{unit}**.\n Reason: **{reason}**\n────────────",
                color=nextcord.Color.orange(),
                timestamp=nextcord.utils.utcnow()
                )
        embed.set_thumbnail(url=guild_member.display_avatar.url)
        embed.set_footer(text=f"Muted by {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
        await interaction.followup.send(f"{checkmark}`Succesfully Muted`{checkmark}")
        await interaction.channel.send(embed=embed)
            
    @ban.error
    async def ban_error(self, interaction: nextcord.Interaction, error: Exception):
        await interaction.send(f"```⚠️ {error}```", ephemeral=True)

    @kick.error
    async def kick_error(self, interaction: nextcord.Interaction, error: Exception):
        await interaction.send(f"```⚠️ {error}```", ephemeral=True)
    
    @mute.error
    async def mute_error(self, interaction: nextcord.Interaction, error: Exception):
        if isinstance(error, nextcord.Forbidden):
            await interaction.followup.send("```⚠️ I do not have permission to mute this member!```", ephemeral=True)
        elif isinstance(error, nextcord.ext.commands.MissingPermissions):
            await interaction.followup.send("```⚠️ You do not have permission to use this command!```", ephemeral=True)
        else:
            await interaction.followup.send(f"```⚠️ {error}```", ephemeral=True)

def setup(bot):
    bot.add_cog(punishments(bot))