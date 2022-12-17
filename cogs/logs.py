import discord
import nextcord
from nextcord.ext import commands
import aiosqlite

import main


class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name='logs', guild_ids=[main.GUILD_ID])
    async def on_command(self, ctx: nextcord.Interaction, channel: nextcord.TextChannel = None):
        if not channel == None:
            author: discord.Member = ctx.user
            if not author.guild_permissions.administrator:
                embed = nextcord.Embed(title='Oops', description='Dazu hast du keine Rechte!',
                                       color=nextcord.Color.red())
                message = ctx.response.send_message(embed=embed, ephemeral=True)
                await ctx.sleep(2)
                await message.delete()
                return
            async with aiosqlite.connect('main.db') as db:
                async with db.cursor() as cursor:
                    await cursor.execute('SELECT channel FROM log WHERE key = ?', ('log',))
                    data = await cursor.fetchone()
                    if data:
                        await cursor.execute('UPDATE log SET channel = ? WHERE key = ?', (channel.id, 'log',))
                    else:
                        await cursor.execute('INSERT INTO log (channel, key) VALUES (?, ?)', (channel.id, 'log',))
                await db.commit()
                embed = nextcord.Embed(title='SETTINGS', description=f'Der Log-Channel ist nun {channel.mention}',
                                       color=nextcord.Color.green())
                await ctx.response.send_message(embed=embed, ephemeral=True)
        else:
            async with aiosqlite.connect('main.db') as db:
                async with db.cursor() as cursor:
                    await cursor.execute('SELECT channel FROM log WHERE key = ?', ('log',))
                    ids = f'{await cursor.fetchone()}'.replace(",", "").replace("(", "").replace(")", "")
                    log = ctx.user.guild.get_channel(int(ids))
                    print(log)
                    print(ids)
                    embed = nextcord.Embed(title='SETTINGS', description=f'Der Log-Channel ist momentan {log.mention}',
                                           color=nextcord.Color.blurple())
                    await ctx.response.send_message(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(Logs(bot))
