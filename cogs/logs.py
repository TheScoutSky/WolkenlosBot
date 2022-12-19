import discord
import nextcord
from nextcord.ext import commands
import main
import pymongo
import os


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
            main.DB.settings.insert_one(
                {
                    "_id": 1,
                    "log-channel": channel.id
                }
            )
            embed = nextcord.Embed(title='SETTINGS', description=f'Der Log-Channel ist nun {channel.mention}',
                                   color=nextcord.Color.green())
            await ctx.response.send_message(embed=embed, ephemeral=True)
        else:
            results = main.DB.settings.find_one({"_id": 1})
            ids = results["log-channel"]
            print(ids)
            log = ctx.user.guild.get_channel(int(ids))
            print(log)
            embed = nextcord.Embed(title='SETTINGS', description=f'Der Log-Channel ist momentan {log.mention}',
                                   color=nextcord.Color.blurple())
            await ctx.response.send_message(embed=embed, ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message):
        results = main.DB.settings.find_one({"_id": 1})



def setup(bot):
    bot.add_cog(Logs(bot))
