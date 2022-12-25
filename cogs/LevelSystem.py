import asyncio
import math
import random

import nextcord
from nextcord.ext import commands

import main

XP_WAITING = []

class LevelSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if XP_WAITING.__contains__(message.author.id):
            return
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
        xp_insg = math.floor(random.randrange(1,3) + len(message.clean_content) / 10) + xp
        xp_needed = math.floor(((lvl*(lvl - 1)) / 15) * 100) + 100
        if xp_insg > xp_needed:
            xp_insg = 0
            lvl += 1
            embed = nextcord.Embed(title='**Level Up**',
                                   description=f'{message.author.mention} hat erfolgreich Level **{lvl}** erreicht!',
                                   color=nextcord.Color.orange())
            await message.channel.send(embed=embed)
        main.DB.user.update_one({"dc": message.author.id}, {"$set": {"dclvl": lvl}})
        main.DB.user.update_one({"dc": message.author.id}, {"$set": {"dcxp": xp_insg}})
        XP_WAITING.append(message.author.id)
        await asyncio.sleep(60)
        XP_WAITING.remove(message.author.id)

    @nextcord.slash_command(name='level', description='Zeigt das Level von dir', guild_ids=[main.GUILD_ID])
    async def on_level_command(self, interaction: nextcord.Interaction, member:nextcord.Member = None):
        member = member or interaction.user
        res = main.DB.user.find_one({"dc": member.id})
        if res is None:
            main.DB.user.insert_one({
                "dc": member.id
            })
        res = main.DB.user.find_one({"dc": member.id})
        if "dclvl" not in res:
            main.DB.user.update_one({"dc": member.id}, {"$set": {"dclvl": 0}})
            main.DB.user.update_one({"dc": member.id}, {"$set": {"dcxp": 0}})
        res = main.DB.user.find_one({"dc": member.id})
        lvl = res["dclvl"]
        xp = res["dcxp"]
        xp_needed = math.floor(((lvl*(lvl - 1)) /15) *100) + 100
        embed = nextcord.Embed(title=f'Level von {member.name}', description='Das sind deine Stats',
                               color=nextcord.Color.orange())
        embed.add_field(name='Level', value=f'{lvl}')
        embed.add_field(name='XP', value=f'**{xp}**/{xp_needed}')
        embed.set_thumbnail(url=member.avatar)
        await interaction.response.send_message(embed=embed)


def setup(bot):
    bot.add_cog(LevelSystem(bot))
