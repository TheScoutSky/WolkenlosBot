import nextcord
from nextcord.ext import commands


class AutoModeration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        author: nextcord.Member = message.author
        BlackList = ["hurensohn", "nuttensohn", "arschloch", "neger", "nigger", "negger", "hs", "hillbilly",
                     "arschgesicht", "dummkopf", "eierkopf", "hackfresse", "hurenkind", "schwanzlutscher",
                     "schwachkopf", "sackratte", "vollpfosten", "wichser", "wixer", "wixxer", "wickser", "wikser",
                     "mooz"]
        for word in BlackList:
            if message.content.lower().__contains__(word):
                embed = nextcord.Embed(title='So nicht', description='Bitte verwende Solche Worte nicht!',
                                       color=nextcord.Color.red())
                await message.delete()
                await message.channel.send(embed=embed)


def setup(bot):
    bot.add_cog(AutoModeration(bot))
