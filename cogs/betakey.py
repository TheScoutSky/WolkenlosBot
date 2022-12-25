import asyncio
import random
import secrets

import nextcord
from nextcord.ext import commands
import nextcord.ui
import redis

import main

CHAN = 1000


class BetaKey(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name='betakey', guild_ids=[main.GUILD_ID])
    @commands.has_permissions(administrator=True)
    async def on_command(self, ctx, channel: nextcord.TextChannel = None, chance: int = None):
        CHAN = chance or 10000
        channel = channel or ctx.channel
        author: nextcord.Member = ctx.user
        if not author.guild_permissions.administrator:
            embed = nextcord.Embed(title='Oops', description='Dazu hast du keine Rechte!', color=nextcord.Color.red())
            message = ctx.response.send_message(embed=embed, ephemeral=True)
            await asyncio.sleep(2)
            await message.delete()
            return
        thumbnail = nextcord.Embed(color=nextcord.Color.orange())
        thumbnail.set_image(
            url='https://cdn.discordapp.com/attachments/1053333236094337116/1053664659535831142/Betak-Key.png')
        keyEmbed = nextcord.Embed(title='**BETAKEY GENERATOR**', description='Generiere deinen eigenen Betakey',
                                  color=nextcord.Color.orange())
        keyEmbed.add_field(name='Wichtig', value='Du brauchst ein Minecraft-Account um einen Betakey einzuloesen!',
                           inline=False)
        keyEmbed.add_field(name='Aktuelle Wahrscheinlichkeit', value=f'1 zu {CHAN}',
                           inline=False)
        keyEmbed.set_image(
            url='https://cdn.discordapp.com/attachments/1053333236094337116/1053379533769801799/Line3.png')
        view = Buttons()
        mes = await channel.send(view=view, embeds=[thumbnail, keyEmbed])
        message = await ctx.response.send_message('Done!', ephemeral=True)
        await asyncio.sleep(1)
        await message.delete()
        await view.wait()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.bot.user.id:
            return
        resault = main.DB.user.find_one({"key": message.content})
        if not resault is None:
            if main.DB.user.find_one({"dc":message.author.id}) is None:
                main.DB.user.insert_one({
                    "dc": message.author.id,
                    "mc": resault["mc"],
                    "dc-name": message.author.name,
                    "mc-name": resault["username"],
                    "linked": "true"
                })
            else:
                main.DB.user.update_one({"dc":message.author.id},{"$set": {
                    "mc": resault["mc"],
                    "dc-name": message.author.name,
                    "mc-name": resault["username"],
                    "linked": "true"
                }})
            main.DB.user.delete_one({"key": message.content})
            embed = nextcord.Embed(title='Geschafft', color=nextcord.Color.green(),
                                   description='Du kannst jetzt dem Server joinen!')
            embed.add_field(name='Minecraft Account', value=f'{resault["username"]}')
            embed.add_field(name='Discord Account', value=message.author.name)
            await message.channel.send(embed=embed)


class Buttons(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value = None

    @nextcord.ui.button(label='Generate', style=nextcord.ButtonStyle.primary, custom_id='button:key-gen')
    async def generate(self, button: nextcord.Button, interaction: nextcord.Interaction):
        chance = random.randrange(1, CHAN)
        auhtor = interaction.user
        if chance == 1:
            key = f'BB00-{secrets.token_urlsafe(32)}'
            main.DB.user.insert_one(
                {
                    "beta-key": key
                }
            )
            embed = nextcord.Embed(title='**CONGRATULATIONS**', description='Du hast einen Betakey gewonnen',
                                   color=nextcord.Color.green())
            embed.add_field(name='__WICHTIG__', value='Teile deinen **Betakey** auf keinen Fall mit __Dritten__',
                            inline=False)
            embed.add_field(name='__BETAKEY__', value=f'```{key}```', inline=False)

            try:
                await auhtor.send(embed=embed)
                embed = nextcord.Embed(title='**Geschafft**', description='Guck in deine DMS',
                                       color=nextcord.Color.green())
                await interaction.response.send_message(embed=embed, ephemeral=True)
            except nextcord.Forbidden:
                embed.add_field(name='__Achtung__',
                                value='Da du DMs ausgeschalten hast musst du dir diesen Key umbedingt speichern')
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = nextcord.Embed(title='**Schade**', description=f'Versuche es gerne Morgen nochmal',
                                   color=nextcord.Color.red())
            message = await interaction.response.send_message(embed=embed, ephemeral=True)
            await asyncio.sleep(2)
            await message.delete()

    @nextcord.ui.button(label='Activate', style=nextcord.ButtonStyle.green, custom_id='button:key-act')
    async def activate(self, button: nextcord.Button, interaction: nextcord.Interaction):
        resault = main.DB.user.find_one({"dc": interaction.user.id})
        if resault is None:
            embed = nextcord.Embed(title='Fehler',
                                   description='Du musst deinen Discord Account mit Minecraft verlinken',
                                   color=nextcord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        else:
            if "activated" in resault:
                embed = nextcord.Embed(title='Fehler',
                                       description='Du hast bereits einen Betakey aktiviert!',
                                       color=nextcord.Color.red())
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        await interaction.response.send_modal(Modal())


class Modal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(
            title="Beta-Key Aktivieren",
            custom_id='modal:betakey',
            timeout=None,
            auto_defer=True
        )
        self.key = nextcord.ui.TextInput(
            label='Beta-Key',
            required=True,
            custom_id='txtinput:key',
            placeholder='BB00-00000000000000000000000000000000',
            min_length=48,
            max_length=48,
            style=nextcord.TextInputStyle.short
        )
        self.add_item(self.key)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        key = f'{self.key.value}'
        print(key)
        resault = main.DB.user.find_one({"beta-key": key})
        if resault is not None:
            em = nextcord.Embed(title='BETA-KEY AKTIVIERT',
                                description=f"{interaction.user.mention} hat seinen Key aktiviert",
                                color=nextcord.Color.green())
            em.add_field(name='Key', value=key)
            main.DB.user.delete_one({"beta-key": key})
            main.DB.user.update_one({"dc": interaction.user.id}, {"$set": {"activated": "true"}})
            try:
                embed = nextcord.Embed(title="BETAKEY AKTIVATED", description="Du hast deinen Betakey aktiviert",
                                       color=nextcord.Color.green())
                await interaction.user.send(embed=embed)
            except nextcord.Forbidden:
                embed = None
            results = main.DB.settings.find_one({"_id": 1})
            ids = results["log-channel"]
            log = interaction.user.guild.get_channel(int(ids))
            return await log.send(embed=em)


def setup(bot):
    bot.add_cog(BetaKey(bot))
