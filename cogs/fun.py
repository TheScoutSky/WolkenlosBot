import base64

from nextcord.ext import commands
import nextcord
from PIL import Image
from io import BytesIO
import aiohttp
import time
import main


class Dropdown(nextcord.ui.Select):
    def __init__(self, message, images, user):
        self.message = message
        self.images = images
        self.user = user

        options = [
            nextcord.SelectOption(label='1'),
            nextcord.SelectOption(label='2'),
            nextcord.SelectOption(label='3'),
            nextcord.SelectOption(label='4'),
            nextcord.SelectOption(label='5'),
            nextcord.SelectOption(label='6'),
            nextcord.SelectOption(label='7'),
            nextcord.SelectOption(label='8'),
            nextcord.SelectOption(label='9'),
        ]
        super().__init__(
            placeholder='Wahle das Bild was du sehen willst',
            max_values=1,
            min_values=1,
            options=options
        )

    async def callback(self, interaction: nextcord.Interaction):
        if not int(self.user) == int(interaction.user.id):
            return
        selection = int(self.values[0]) - 1
        image = BytesIO(base64.decodebytes(self.images[selection].encode('utf-8')))
        await interaction.message.edit(file=nextcord.File(image, "generatedImage.png"),
                                       view=DropdownView(self.message, self.images, interaction.user.id))


class DropdownView(nextcord.ui.View):
    def __init__(self, message, images, user):
        super().__init__()
        self.add_item(Dropdown(message, images, user))


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name='generate', guild_ids=[main.GUILD_ID])
    async def generate(self, ctx: nextcord.Interaction, promt: str):
        ETA = int(time.time() + 60)
        embed = nextcord.Embed(title="Generiere dein eigenes Bild", color=nextcord.Color.orange())
        embed.add_field(name=f'**Promt**', value=promt, inline=False)
        embed.add_field(name=f'**Wartezeit**', value=f'<t:{ETA}:R>')
        msg = await ctx.send(embed=embed, ephemeral=False)
        async with aiohttp.request("POST", "https://backend.craiyon.com/generate", json={"prompt": promt}) as resp:
            r = await resp.json()
            images = r['images']
            image = BytesIO(base64.decodebytes(images[0].encode('utf-8')))
            embed = nextcord.Embed(title="Generiere dein eigenes Bild", color=nextcord.Color.orange())
            embed.add_field(name=f'**Promt**', value=promt, inline=False)
            embed.add_field(name=f'**Wartezeit**', value=f'Fertig')
            await msg.edit(embed=embed,
                           file=nextcord.File(image, "generatedImage.png"),
                           view=DropdownView(msg, images, ctx.user.id))


def setup(bot):
    bot.add_cog(Fun(bot))
