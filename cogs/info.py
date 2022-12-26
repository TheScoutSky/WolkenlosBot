import nextcord
from nextcord.ext import commands

import main


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name='info')
    async def on_command(self, interaction: nextcord.Interaction, user:nextcord.Member = None):
        user = user or interaction.user
        info = main.DB.user.find_one({'dc':user.id})
        if info is not None:
            mc = "None"
            if "mc" in info:
                mc = info["mc"]
            mc_name = "None"
            if "mc-name" in info:
                mc_name = info["mc-name"]
            activated = "flase"
            if "activated" in info:
                activated = info["activated"]
            linked = "false"
            if "linked" in info:
                linked = info["linked"]
            level = 0
            if "dclvl" in info:
                level = info["dclvl"]
        embed = nextcord.Embed(title=f'Infos von {user.name}', description='Hier sind alle informationen vom Spieler gelistet', color=nextcord.Color.orange())
        embed.add_field(name='**Discord Name**', value=f'{user.name}')
        embed.add_field(name='**Discord ID**', value=f'{user.id}')
        embed.add_field(name='**Minecraft Name**', value=f'{mc_name}')
        embed.add_field(name='**Minecraft ID**', value=f'{mc}')
        embed.add_field(name='**Linked**', value=f'{linked}')
        embed.add_field(name='**Betakey**', value=f'{activated}')
        embed.add_field(name='**Level (Dc)**', value=f'{level}')
        await interaction.response.send_message(embed=embed, ephemeral=True)




def setup(bot):
    bot.add_cog(Info(bot))