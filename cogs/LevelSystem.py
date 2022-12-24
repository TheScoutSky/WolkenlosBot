import random

import nextcord
from nextcord.ext import commands

import main


class LevelSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        res = main.DB.user.find_one({"dc": message.author.id})
        if res is None:
            main.DB.user.insert_one({
                "dc":message.author.id
            })
        res = main.DB.user.find_one({"dc": message.author.id})
        if "dclvl" not in res:
            main.DB.user.update_one({"dc": message.author.id}, {"$set": {"dclvl": 0}})
            main.DB.user.update_one({"dc": message.author.id}, {"$set": {"dcxp": 0}})
        res = main.DB.user.find_one({"dc": message.author.id})
        lvl = res["dclvl"]
        xp = res["dcxp"]
        xp_insg = random.randrange(3, 10) + xp + len(message.clean_content)
        print(len(message.clean_content))
        if xp_insg > (20 * lvl) ** 2 + 1000:
            xp_insg = 0
            lvl += 1
            embed = nextcord.Embed(title='**Level Up**',
                                   description=f'{message.author.mention} hat erfolgreich Level **{lvl}** erreicht!',
                                   color=nextcord.Color.orange())
            await message.channel.send(embed=embed)
        main.DB.user.update_one({"dc": message.author.id}, {"$set": {"dclvl": lvl}})
        main.DB.user.update_one({"dc": message.author.id}, {"$set": {"dcxp": xp_insg}})

    @nextcord.slash_command(name='level', description='Zeigt das Level von dir', guild_ids=[main.GUILD_ID])
    async def on_level_command(self, interaction: nextcord.Interaction):
        res = main.DB.user.find_one({"dc": interaction.user.id})
        if res is None:
            main.DB.user.insert_one({
                "dc": interaction.user.id
            })
        if "dclvl" not in res:
            main.DB.user.update_one({"dc": interaction.user.id}, {"$set": {"dclvl": 0}})
            main.DB.user.update_one({"dc": interaction.user.id}, {"$set": {"dcxp": 0}})
        res = main.DB.user.find_one({"dc": interaction.user.id})
        lvl = res["dclvl"]
        xp = res["dcxp"]
        xp_needed = (20 * lvl) ** 2 + 1000
        embed = nextcord.Embed(title=f'Level von {interaction.user.name}', description='Das sind deine Stats',
                               color=nextcord.Color.orange())
        embed.add_field(name='Level', value=f'{lvl}')
        embed.add_field(name='XP', value=f'**{xp}**/{xp_needed}')
        await interaction.response.send_message(embed=embed)


def setup(bot):
    bot.add_cog(LevelSystem(bot))
