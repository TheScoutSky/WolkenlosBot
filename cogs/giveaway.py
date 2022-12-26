import time

import nextcord
from nextcord.ext import commands
import humanfriendly
import time as pyTime

import main


class GiveAWay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name='giveaway', guild_ids=[main.GUILD_ID])
    async def giveaway(self, interaction: nextcord.Interaction):
        pass

    @giveaway.subcommand(name='start', description='Starte ein Giveaway')
    async def start(self, interaction: nextcord.Interaction, prize: str or nextcord.Role, channel: nextcord.TextChannel,
                    time: str, winners: int):
        embed = nextcord.Embed(title=f'**Wolkenlos Giveaway**', color=nextcord.Color.orange())
        time = humanfriendly.parse_timespan(time)
        epochEnd = pyTime.time() + time
        if prize in interaction.guild.roles:
            print('Yes!')
            main.DB.giveaway.insert_one({
                "channel": channel.id,
                "prize": prize.id,
                "date": time,
                "winners": winners
            })
            embed.add_field(name='**Preis**', value=f'{prize.name}', inline=False)
        else:
            main.DB.giveaway.insert_one({
                "channel": channel.id,
                "prize": prize,
                "date": time,
                "winners": winners
            })
            embed.add_field(name='**Preis**', value=f'{prize}', inline=False)
        embed.add_field(name="**Gewinnder**", value=f'{winners}', inline=False)
        embed.add_field(name='**Endet**', value=f'<t:{int(epochEnd)}:R>', inline=False)
        embed.set_image(url='https://cdn.discordapp.com/attachments/1053333236094337116/1053379533769801799/Line3.png')
        thumbnail = nextcord.Embed(color=nextcord.Color.orange())
        thumbnail.set_image(url='https://cdn.discordapp.com/attachments/1053333236094337116/1053664659535831142/Betak-Key.png')
        await channel.send(embeds=[thumbnail, embed])
        await interaction.response.send_message('Done!', ephemeral=True)



def setup(bot):
    bot.add_cog(GiveAWay(bot))
