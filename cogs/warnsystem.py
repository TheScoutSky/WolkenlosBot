import asyncio
import os

import aiosqlite
import nextcord
import pymongo
from nextcord.ext import commands
import main
from datetime import datetime


class WarnSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.user_command(name="Verwarnen", guild_ids=[main.GUILD_ID])
    async def warn_command(self, interaction: nextcord.Interaction, member: nextcord.Member):
        await interaction.response.send_modal(Modal(member))

    @nextcord.user_command(name="Warns", guild_ids=[main.GUILD_ID])
    async def warns_command(self, interaction: nextcord.Interaction, member: nextcord.Member):
        embed = nextcord.Embed(title=f'Warns von {member.name}', color=nextcord.Color.orange(),
                               description='Hier werden alle Warns aufgelistet')
        resault = main.DB.warns.find({"user": member.id})
        warns = 1
        for res in resault:
            embed.add_field(name=f'**{warns}. Warn**',
                            value=f'Teamitglied: {member.guild.get_member(res["warner"]).name} '
                                  f'\n Grund: {res["reason"]}'
                                  f'\n Datum: {res["date"]}', inline=False)
            warns += 1

        embed.set_footer(text=f'requested by {interaction.user.name}', icon_url=interaction.user.avatar)
        await interaction.channel.send(embed=embed)
        message = await interaction.response.send_message('Done!', ephemeral=True)
        await asyncio.sleep(2)
        await message.delete()



class Modal(nextcord.ui.Modal):
    def __init__(self, user: nextcord.Member):
        super().__init__(
            title=f'Warn {user.name}',
            custom_id='modal:warn',
            timeout=None,
            auto_defer=True
        )
        self.USER = user
        self.REASON = nextcord.ui.TextInput(
            label='Grund',
            min_length=1,
            max_length=1000,
            style=nextcord.TextInputStyle.paragraph,
            placeholder='Er war Gemein zu mir:c',
            custom_id='input:wanr:grund'
        )
        self.add_item(self.REASON)

    async def callback(self, interaction: nextcord.Interaction):
        main.DB.warns.insert_one(
            {
                "user": self.USER.id,
                "reason": self.REASON.value,
                "warner": interaction.user.id,
                "date": f'{datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}'
            })
        warns = 0
        resault = main.DB.warns.find({"user": self.USER.id})
        for _ in resault:
            warns += 1
        embed = nextcord.Embed(title='**__WARN__**', color=nextcord.Color.red())
        embed.add_field(name='User', value=f'{self.USER.mention}', inline=True)
        embed.add_field(name='User-ID', value=f'{self.USER.id}', inline=True)
        embed.add_field(name='Warns', value=f'{warns}', inline=False)
        embed.add_field(name='Teammitglied', value=f'{interaction.user.mention}', inline=True)
        embed.add_field(name='Grund', value=f'{self.REASON.value}', inline=True)
        results = main.DB.settings.find_one({"_id": 1})
        ids = results["log-channel"]
        log = interaction.user.guild.get_channel(int(ids))
        await log.send(embed=embed)



def setup(bot):
    bot.add_cog(WarnSystem(bot))
