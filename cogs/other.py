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
        default_member_permissions=nextcord.Permissions(manage_roles=True),
    )
    async def add_role(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member,
        *,
        role: nextcord.Role,
    ):

        await interaction.response.defer()

        guild_member = interaction.guild.get_member(member.id)

        if role in guild_member.roles:

            error_embed = nextcord.Embed(
                title=f"{crossmark} `Error!`{crossmark}",
                description=f"**{guild_member.mention}** already has the {role.name} role!\n`────────────────────────`",
                color=nextcord.Color.red(),
                timestamp=nextcord.utils.utcnow(),
            )
            error_embed.set_thumbnail(url=guild_member.display_avatar.url)
            await interaction.followup.send(embed=error_embed)
        else:
            await guild_member.add_roles(role)

            embed = nextcord.Embed(
                title=f"{checkmark} `Role added!`{checkmark}",
                description=f"**{guild_member.mention}** has been given the {role.name} role! 🎉\n`────────────────────────`",
                color=nextcord.Color.green(),
                timestamp=nextcord.utils.utcnow(),
            )
            embed.set_thumbnail(url=guild_member.display_avatar.url)
            embed.set_footer(
                text=f"Role added by {interaction.user.name}",
                icon_url=interaction.user.display_avatar.url,
            )

            await interaction.followup.send(embed=embed)

    @nextcord.slash_command(
        name="role_remove",
        description="Removes role from assigned member.",
        default_member_permissions=nextcord.Permissions(manage_roles=True),
    )
    async def role_remove(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member,
        *,
        role: nextcord.Role,
    ):

        await interaction.response.defer()

        guild_member = interaction.guild.get_member(member.id)

        if role in guild_member.roles:
            await guild_member.remove_roles(role)

            embed = nextcord.Embed(
                title=f"{checkmark} `Role Removed`{checkmark}",
                description=f"{guild_member.mention} No longer has the {role.name} role! 🎉\n`────────────────────────`",
                color=nextcord.Color.green(),
                timestamp=nextcord.utils.utcnow(),
            )
            embed.set_thumbnail(url=guild_member.display_avatar.url)
            embed.set_footer(
                text=f"Role removed by {interaction.user.name}",
                icon_url=interaction.user.display_avatar.url,
            )

            await interaction.followup.send(embed=embed)
        else:
            error_embed = nextcord.Embed(
                title=f"{crossmark} `Error!`{crossmark}",
                description=f"**{guild_member.mention}** does not have the {role.name} role!\n`────────────────────────`",
                color=nextcord.Color.red(),
                timestamp=nextcord.utils.utcnow(),
            )
            error_embed.set_thumbnail(url=guild_member.display_avatar.url)

            await interaction.followup.send(embed=error_embed)

    @nextcord.slash_command(
        name="purge",
        description="Deletes a certain amount of messages above you!",
        default_member_permissions=nextcord.Permissions(administrator=True),
    )
    async def purge(self, interaction: nextcord.Interaction, amount: int):

        if amount <= 0:
            amount_embed = nextcord.Embed(
                title=f"{crossmark} `Error!`{crossmark}",
                description="You cannot delete 0 or less messages!",
                color=nextcord.Color.red(),
                timestamp=nextcord.utils.utcnow(),
            )
            await interaction.response.send_message(embed=amount_embed)
            return

        try:
            deleted = await interaction.channel.purge(limit=amount)
            embed = nextcord.Embed(
                title=f"{checkmark} `Successfully Purged!`{checkmark}",
                description=f"Successfully deleted {len(deleted)} messages! \n`────────────────────────`",
                color=nextcord.Color.green(),
                timestamp=nextcord.utils.utcnow(),
            )
            embed.set_thumbnail(url=interaction.guild.icon.url)
            embed.set_footer(
                text=f"Purged by {interaction.user.name}",
                icon_url=interaction.user.display_avatar.url,
            )
            await interaction.response.send_message(embed=embed)
        except nextcord.HTTPException as e:
            error_embed = nextcord.Embed(
                title=f"{crossmark} `Error!`{crossmark}",
                description=f"An error occurred while purging messages: {e}",
                color=nextcord.Color.red(),
                timestamp=nextcord.utils.utcnow(),
            )
            await interaction.response.send_message(embed=error_embed)

    @add_role.error
    async def add_role_error(self, interaction: nextcord.Interaction, error: Exception):
        await interaction.followup.send(f"```⚠️ {error}```", ephemeral=True)

    @role_remove.error
    async def remove_role_error(self, interaction: nextcord.Interaction, error):
        await interaction.followup.send(f"```⚠️ {error}```", ephemeral=True)

    @purge.error
    async def purge_error(self, interaction: nextcord.Interaction, error: Exception):
        if isinstance(error, nextcord.ext.commands.errors.MissingPermissions):
            await interaction.followup.send(
                "You do not have permission to use this command.", ephemeral=True
            )
        else:
            await interaction.followup.send(f"```⚠️ {error}```", ephemeral=True)
        print(f"An error occurred in the purge command: {error}")


def setup(bot):
    bot.add_cog(Other(bot))