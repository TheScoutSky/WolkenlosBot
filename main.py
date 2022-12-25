import logging
import os
from pathlib import Path

import nextcord

import pymongo
from nextcord.ext import commands
from dotenv import load_dotenv

from cogs import betakey, tickets

load_dotenv()

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('BOT-MAIN')

bot = commands.Bot(
    command_prefix='!',
    intents=nextcord.Intents.all(),
    activity=nextcord.Activity(type=nextcord.ActivityType.playing, name='Frohe Weihnachten!'),
    status=nextcord.Status.online
)


@bot.event
async def on_ready():
    MONGO = pymongo.MongoClient(os.getenv('MONGO_URI'))
    DB = MONGO.wolkenlos
    resault = DB.settings.find_one({"_id": "generator"})
    if resault is not None:
        guild: nextcord.Guild = bot.get_guild(GUILD_ID)
        channel = guild.get_channel(resault["channel"])
        mes = channel.get_partial_message(resault["message"])
        betakey.CHAN = resault["chance"]
        await mes.edit(view=betakey.Buttons())
    resault = DB.tickets.find_one({"_id": "settings"})
    if resault is not None:
        guild: nextcord.Guild = bot.get_guild(GUILD_ID)
        channel = guild.get_channel(resault["channel"])
        mes = channel.get_partial_message(resault["message"])
        await mes.edit(view=tickets.TicketButton())
    print('bot is ready')


USER_VERIFY = {}
GUILD_SAVE = {}
GEN_USE = {}
VERIFY_ROLE_ID = 1030426886242840586
GUILD_ID = 1030425830725271562
CLIENT_ID = 1051582605050523649
MONGO = pymongo.MongoClient(os.getenv('MONGO_URI'))
DB = MONGO.wolkenlos

if __name__ == '__main__':
    log.info('Starting bot...')
    cogs = [p.stem for p in Path('cogs').glob('**/*.py') if not p.name.startswith('__')]
    log.info('Loading %d extentions...', len(cogs))
    for cog in cogs:
        bot.load_extension(f'cogs.{cog}')
        log.info('Loaded %s', cog)
    token = os.getenv('BOT_TOKEN')
    bot.run(token)
