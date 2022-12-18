import redis
import nextcord
from nextcord.ext import commands
import main

r = redis.Redis(host='65.21.125.211', port=187)


class RedisTest(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name='test', guild_ids=[main.GUILD_ID])
    async def on_command(self, ctx):
        if r.exists('enable'):
            message = r.get('enable')
            await ctx.response.send_message(f'{message}', ephemeral=True)
        else:
            await ctx.response.send_message(f'not exist', ephemeral=True)


def setup(bot):
    bot.add_cog(RedisTest(bot))
