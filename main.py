import logging
import os
from pathlib import Path
import aiosqlite
import nextcord
import pymongo
from nextcord.ext import commands
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('BOT-MAIN')

bot = commands.Bot(
    command_prefix='!',
    intents=nextcord.Intents.all(),
    activity=nextcord.Activity(type=nextcord.ActivityType.playing, name='Wolkenlos!!!'),
    status=nextcord.Status.online
)


@bot.event
async def on_ready():
    MONGO = pymongo.MongoClient(os.getenv('MONGO_URI'))
    DB = MONGO.wolkenlos
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
