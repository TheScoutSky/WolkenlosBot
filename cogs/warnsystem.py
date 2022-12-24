import asyncio
import os
import secrets

import nextcord
import pymongo
from nextcord.ext import commands
import main
from datetime import datetime


class WarnSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.user_command(name="Verwarnen", guild_ids=[main.GUILD_ID])
    @commands.has_permissions(kick_members=True)
    async def warn_command(self, interaction: nextcord.Interaction, member: nextcord.Member):
        await interaction.response.send_modal(Modal(member))

    @nextcord.user_command(name="Warns", guild_ids=[main.GUILD_ID])
    @commands.has_permissions(kick_members=True)
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
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @nextcord.user_command(name="Delete Warn", guild_ids=[main.GUILD_ID])
    @commands.has_permissions(kick_members=True)
    async def del_warns_command(self, interaction: nextcord.Interaction, member: nextcord.Member):
        embed = nextcord.Embed(title=f'Delete Warns von {member.name}', color=nextcord.Color.orange(),
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
        me = await interaction.response.send_message(embed=embed, ephemeral=True)
        await me.edit(view=DropdownView(member, warns, me))


class DropDownMenu(nextcord.ui.Select):
    def __init__(self, user, amount, message):
        self.user = user
        self.amount =amount
        self.message = message
        resault = main.DB.warns.find({"user": self.user.id})
        opt = []
        warns = 1
        for res in resault:
            opt.append(nextcord.SelectOption(label=f"{warns}"))
            warns +=1
        if warns is 1:
            opt.append(nextcord.SelectOption(label='None'))

        super().__init__(
            placeholder='Welcher Warn',
            max_values=1,
            min_values=1,
            options=opt
        )

    async def callback(self, interaction: nextcord.Interaction):
        if self.values[0] == 'None':
            return
        selection = int(self.values[0])
        resault = main.DB.warns.find({"user": self.user.id})
        num = 0
        for res in resault:
            num += 1
            if num == selection:
                print(res["user"])
                print(num)
                print(f'{selection}')
                main.DB.warns.delete_one({"_id":f"{res['_id']}"})
                embed = nextcord.Embed(title=f'Delete Warns von {self.user.name}', color=nextcord.Color.orange(),
                                       description='Hier werden alle Warns aufgelistet')
                resault = main.DB.warns.find({"user": self.user.id})
                warns = 1

                for res in resault:
                    embed.add_field(name=f'**{warns}. Warn**',
                                    value=f'Teamitglied: {self.user.guild.get_member(res["warner"]).name} '
                                          f'\n Grund: {res["reason"]}'
                                          f'\n Datum: {res["date"]}', inline=False)
                    warns += 1

                embed.set_footer(text=f'requested by {interaction.user.name}', icon_url=interaction.user.avatar)
                await self.message.edit(view=DropdownView(self.user, self.amount, self.message), embed=embed)
                results = main.DB.settings.find_one({"_id": 1})
                ids = results["log-channel"]
                embed = nextcord.Embed(title=f"__Deleted Warn from {self.user.name}__", description=f'Deleted by {interaction.user.mention}', color=nextcord.Color.red())
                warner = self.user.guild.get_member(res["warner"])
                embed.add_field(name='User-ID', value=f'{self.user.id}', inline=False)
                embed.add_field(name='Teammitglied', value=f'{warner.mention}', inline=False)
                embed.add_field(name='Grund', value=f'{res["reason"]}', inline=False)
                log = interaction.user.guild.get_channel(int(ids))
                await log.send(embed=embed)
            else:
                print('RIP')


class DropdownView(nextcord.ui.View):
    def __init__(self, user, amount, message):
        super().__init__()
        self.add_item(DropDownMenu(user, amount, message))


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
                "_id":secrets.token_urlsafe(40),
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
