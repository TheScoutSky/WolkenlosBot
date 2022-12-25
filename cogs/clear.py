import nextcord
from nextcord.ext import commands

import main


class Clear(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name='clear', description='Loesche eine beliebige Anzahl an Nachrichten',
                            guild_ids=[main.GUILD_ID])
    @commands.has_permissions(manage_messages=True)
    async def clear_command(self, interaction: nextcord.Interaction, anzahl: int):
        await interaction.channel.purge(limit=anzahl)
        embed = nextcord.Embed(title="Delete Messages", color=nextcord.Color.green(),
                               description=f'Du hast erfolgreich {anzahl} Nachrichten geloescht')
        await interaction.response.send_message(embed=embed, ephemeral=True)
        embed = nextcord.Embed(title="Delete Messages", color=nextcord.Color.green())
        embed.add_field(name='User', value=f'{interaction.user.mention}', inline=True)
        embed.add_field(name='Anzahl', value=f'{anzahl}', inline=True)
        embed.add_field(name='Channel', value=f'{interaction.channel.mention}', inline=False)
        results = main.DB.settings.find_one({"_id": 1})
        ids = results["log-channel"]
        log = interaction.user.guild.get_channel(int(ids))
        await log.send(embed=embed)


def setup(bot):
    bot.add_cog(Clear(bot))
