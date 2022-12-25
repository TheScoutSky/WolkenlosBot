import asyncio
import random
import secrets

import nextcord
from nextcord.ext import commands
import nextcord.ui
import redis

import main

CHAN = 1000


class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name='sticket', guild_ids=[])
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


class TicketButton(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @nextcord.ui.button(label='Erstellen', style=nextcord.ButtonStyle.primary, custom_id='button:ticket-erstellen')
    async def generate(self, button: nextcord.Button, interaction: nextcord.Interaction):
        pass


def setup(bot):
    bot.add_cog(TicketSystem(bot))
