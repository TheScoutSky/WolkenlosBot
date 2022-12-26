import random

import nextcord
import main
from nextcord.ext import commands
from nextcord.ext import tasks



class Minecraft(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name='mc', guild_ids=[main.GUILD_ID])
    async def main(self, interacton: nextcord.Interaction):
        pass

    @main.subcommand(name='chat', description='setze oder erstelle den Minecraft Discord Chat')
    @commands.has_permissions(administrator=True)
    async def chat_command(self, interaction: nextcord.Interaction, channel: nextcord.TextChannel = None):
        category: nextcord.CategoryChannel = interaction.channel.category
        channel = channel or await category.create_text_channel('minecraftchat')
        main.DB.settings.update_one({'_id': 1}, {"$set": {"mc-channel": channel.id}})
        embed = nextcord.Embed(title="Setup", description=f'Der neue Minecraftchannel ist nun {channel.mention}',
                               color=nextcord.Color.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @tasks.loop(seconds=1)
    async def chat(self):
        resault = main.DB.chat.find()
        res = main.DB.settings.find_one({'_id': 1})
        channel = self.bot.get_guild(main.GUILD_ID).get_channel(res["mc-channel"])
        if resault is not None:
            for r in resault:
                text = r["text"]
                user = r["user"]
                embed = nextcord.Embed(title='Message', description=f'{user}: {text}', color=nextcord.Color.orange())
                embed.set_thumbnail(url=f'https://minotar.net/avatar/{user}.png')
                await channel.send(embed=embed)
                main.DB.chat.delete_one({"_id": r["_id"]})

    @tasks.loop(seconds=1)
    async def ACTIVITY(self):
        SENTENCE = ["Banause hausen in Banausenschlauhausen", "Keko du Hengst", "Fische fliegen!", "Schlange is cool", "Seife ist lecker", "TheSkyScout? Wer ist das?", "W-w-wolkenlos", "Python <3"]
        lenght = int(len(SENTENCE))
        main.x += 1
        if main.x == 20:
            await self.bot.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.playing,
                                                                      name=f'{SENTENCE.__getitem__(random.randrange(0, lenght))}'))
            main.x = 0

    @commands.Cog.listener()
    async def on_ready(self):
        self.chat.start()
        self.ACTIVITY.start()


def setup(bot):
    bot.add_cog(Minecraft(bot))
