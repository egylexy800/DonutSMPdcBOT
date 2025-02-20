import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import has_permissions, MissingPermissions

checkmark = "<:checkmark:1342071259567230976>"
crossmark = "<:crossmark:1342071086044680322>"

class Other(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(
        name="role_add", 
        description="Adds role to assigned member.", 
        default_member_permissions=nextcord.Permissions(manage_roles=True)
        )
    async def add_role(self, interaction:nextcord.Interaction, member: nextcord.Member, *, role: nextcord.Role):
        
        await interaction.response.defer(ephemeral=True)
        
        guild_member = interaction.guild.get_member(member.id)
        
        if role in guild_member.roles:
            await interaction.followup.send(f"```⚠️ {member} already has the {role} role! ⚠️```")
        else:
            await guild_member.add_roles(role)
            
            embed = nextcord.Embed(
                title=f"{checkmark} `Role added`{checkmark}",
                description=f"**{guild_member.mention}** ```has been given the {role.name} role! 🎉\n────────────```",
                color=nextcord.Color.green(),
                timestamp=nextcord.utils.utcnow()
            )
            embed.set_thumbnail(url=guild_member.display_avatar.url)
            embed.set_footer(text=f"Role added by {interaction.user.name}", icon_url=interaction.user.display_avatar.url)

            await interaction.channel.send(embed=embed)



    @nextcord.slash_command(
        name="role_remove",
        description="Removes role from assigned member.",
        default_member_permissions=nextcord.Permissions(manage_roles=True)
        )
    async def role_remove(self, interaction:nextcord.Interaction, member: nextcord.Member, *, role: nextcord.Role):
        
        await interaction.response.defer()
        
        guild_member = interaction.guild.get_member(member.id)
        
        if role in guild_member.roles:
            await guild_member.remove_roles(role)
            
            embed = nextcord.Embed(
                title=f"{crossmark} `Role Removed`{crossmark}",
                description=f"{guild_member.mention} ```No longer has the {role.name} role! 🎉\n────────────```",
                color=nextcord.Color.red(),
                timestamp=nextcord.utils.utcnow()
            )
            embed.set_thumbnail(url=guild_member.display_avatar.url)
            embed.set_footer(text=f"Role removed by {interaction.user.name}", icon_url=interaction.user.display_avatar.url)

            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(f"```⚠️ {member} does not have the {role} role! ⚠️```", delete_after=2)
            
            
            
    @nextcord.slash_command(
        name="purge",
        description="Deletes a certain amount of messages above you!",
        default_member_permissions=nextcord.Permissions(administrator=True)
        )
    async def purge(self, interaction: nextcord.Interaction, amount: int):
        await interaction.response.defer(ephemeral=True)

        if amount <= 0:
            return await interaction.followup.send("```⚠️ Please specify a number greater than 0! ⚠️```", ephemeral=True)

        try:
            deleted = await interaction.channel.purge(limit=amount)
            await interaction.followup.send("Succesfully purged.", ephemeral=True)
            await interaction.channel.send(f"```✅ Purged {len(deleted)} messages! ✅```", delete_after=3)
        except nextcord.HTTPException as e:
            await interaction.followup.send(f"```⚠️ An error occurred: {e}```", ephemeral=True)


            
    @add_role.error
    async def add_role_error(self, interaction:nextcord.Interaction, error: Exception):
        await interaction.followup.send(f"```⚠️ {error}```", ephemeral=True)

    @role_remove.error
    async def remove_role_error(self, interaction:nextcord.Interaction, error):
        await interaction.followup.send(f"```⚠️ {error}```", ephemeral=True)
    
    @purge.error
    async def purge_error(self, interaction: nextcord.Interaction, error: Exception):
        await interaction.followup.send(f"```⚠️ {error}```", ephemeral=True)

def setup(bot):
    bot.add_cog(Other(bot))