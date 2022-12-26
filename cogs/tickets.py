import asyncio
import random
import secrets
import time

import nextcord
from nextcord.ext import commands
import nextcord.ui
import redis

import main

CHAN = 1000


class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name='sticket')
    async def main(self, inteaction: nextcord.Interaction):
        pass

    @main.subcommand(name='set')
    @commands.has_permissions(administrator=True)
    async def on_setup_command(self, interaction: nextcord.Interaction, kategorie: nextcord.CategoryChannel):
        if main.DB.tickets.find_one({'_id': 'settings'}) is None:
            main.DB.tickets.insert_one({
                "_id": "settings",
                "kategorie": kategorie.id
            })
        else:
            main.DB.tickets.update_one({'_id': 'settings'}, {'$set': {'kategorie': kategorie.id}})
        channel = await kategorie.create_text_channel(name='Tickets')
        main.DB.tickets.update_one({'_id': 'settings'}, {'$set': {'channel': channel.id}})
        embed = nextcord.Embed(title='**Ticket Automat**',
                               description='Hier kannst du Tickets erstellen wenn du Hilfe brauchst',
                               color=nextcord.Color.orange())
        message = await channel.send(embed=embed, view=TicketButton())
        main.DB.tickets.update_one({'_id': 'settings'}, {'$set': {'message': message.id}})
        await interaction.response.send_message('Done!', ephemeral=True)

    @main.subcommand(name='edit')
    @commands.has_permissions(administrator=True)
    async def on_edit_command(self, interaction: nextcord.Interaction, titel: str, text: str):
        res = main.DB.tickets.find_one({'_id': 'settings'})
        if res is None:
            return
        channel = interaction.guild.get_channel(res["channel"])
        message = channel.get_partial_message(res["message"])
        embed = nextcord.Embed(title=titel, description=text, color=nextcord.Color.orange())
        await message.edit(embed=embed)
        await interaction.response.send_message('Done!', ephemeral=True)


class TicketButton(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value = None

    @nextcord.ui.button(label='Erstellen', style=nextcord.ButtonStyle.primary, custom_id='button:ticket-erstellen')
    async def generate(self, button: nextcord.Button, interaction: nextcord.Interaction):
        if main.DB.tickets.find_one({'user': interaction.user.id}) is not None:
            embed = nextcord.Embed(title='Oops', description='Du kannst maximal 1 Ticket gleichzeitig haben!',
                                   color=nextcord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        if "ticketID" not in main.DB.tickets.find_one({'_id': 'settings'}):
            main.DB.tickets.update_one({'_id': 'settings'}, {'$set': {'ticketID': 0}})
        res = main.DB.tickets.find_one({'_id': 'settings'})
        ticketID = res["ticketID"]
        ticketID += 1
        main.DB.tickets.update_one({'_id': 'settings'}, {'$set': {'ticketID': ticketID}})
        category: nextcord.CategoryChannel = interaction.guild.get_channel(res["kategorie"])
        channel: nextcord.TextChannel = await category.create_text_channel(name=f'ticket-{ticketID}')
        overwrite = nextcord.PermissionOverwrite()
        overwrite.view_channel = False
        await channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
        overwrite.view_channel = True
        await channel.set_permissions(interaction.user, overwrite=overwrite)
        embed = nextcord.Embed(title=f'Ticket {ticketID} by {interaction.user.name}',
                               description='Bitte schreibe hier deine Problemlage rein!', color=nextcord.Color.orange())
        message = await channel.send(embed=embed, view=TicketButtons())
        main.DB.tickets.insert_one({
            '_id': ticketID,
            'user': interaction.user.id,
            'channel': channel.id,
            'message': message.id
        })
        results = main.DB.settings.find_one({"_id": 1})
        ids = results["log-channel"]
        log = interaction.user.guild.get_channel(int(ids))
        embed = nextcord.Embed(title='Ticket Created', color=nextcord.Color.green())
        embed.add_field(name='Ticket created by', value=f'{interaction.user.mention}', inline=False)
        embed.add_field(name='Ticket', value=f'{channel.name}', inline=False)
        await log.send(embed=embed)
        await interaction.response.send_message('Ticket created!', ephemeral=True)


class TicketButtons(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value = None

    @nextcord.ui.button(label='Delete', style=nextcord.ButtonStyle.red, custom_id='button:ticket-delete')
    async def generate(self, button: nextcord.Button, interaction: nextcord.Interaction):
        if not interaction.user.guild_permissions.kick_members:
            embed = nextcord.Embed(title='Oops', description='Du hast keine Rechte das Ticket zu loeschen!',
                                   color=nextcord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        ETA = int(time.time() + 60)
        embed = nextcord.Embed(title='Deleting...', description=f'<t:{ETA}:R>', color=nextcord.Color.red())
        res = main.DB.tickets.find_one({'channel': interaction.channel.id})
        user = interaction.guild.get_member(res["user"])
        main.DB.tickets.delete_one({'channel': interaction.channel.id})
        await interaction.response.send_message(embed=embed)
        await asyncio.sleep((58))
        await interaction.channel.delete()
        results = main.DB.settings.find_one({"_id": 1})
        ids = results["log-channel"]
        log = interaction.user.guild.get_channel(int(ids))
        embed = nextcord.Embed(title='Ticket Delete', color=nextcord.Color.red())
        embed.add_field(name='Teammitglied', value=f'{interaction.user.mention}', inline=False)
        embed.add_field(name='Ticket created by', value=f'{user.mention}', inline=False)
        embed.add_field(name='Ticket', value=f'{interaction.channel.name}', inline=False)
        await log.send(embed=embed)

    @nextcord.ui.button(label='Transcript', style=nextcord.ButtonStyle.blurple, custom_id='button:ticket-trans')
    async def transcript(self, button: nextcord.Button, interaction: nextcord.Interaction):
        if not interaction.user.guild_permissions.kick_members:
            embed = nextcord.Embed(title='Oops', description='Du hast keine Rechte das Ticket zu loeschen!',
                                   color=nextcord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        fileName = f'transcripts/{interaction.channel.name}.txt'
        with open(fileName, "w") as file:
            async for msg in interaction.channel.history(limit=None):
                file.write(f'{msg.created_at} - {msg.author.display_name}: {msg.clean_content}\n')
        file: nextcord.File = nextcord.File(fileName)
        results = main.DB.settings.find_one({"_id": 1})
        ids = results["log-channel"]
        log = interaction.user.guild.get_channel(int(ids))
        embed = nextcord.Embed(title='Ticket Transcription', color=nextcord.Color.orange())
        embed.add_field(name='Teammitglied', value=f'{interaction.user.mention}', inline=False)
        embed.add_field(name='Ticket', value=f'{interaction.channel.name}', inline=False)
        await log.send(embed=embed, file=file)


def setup(bot):
    bot.add_cog(TicketSystem(bot))
