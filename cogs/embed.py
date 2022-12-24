import nextcord
from nextcord.ext import commands
import main
import asyncio

CHANNEL = {}


class Embed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name='embed', guild_ids=[main.GUILD_ID])
    async def on_command(self, ctx, channel: nextcord.TextChannel = None):
        channel = channel or ctx.channel
        author: nextcord.Member = ctx.user
        if not author.guild_permissions.manage_messages:
            embed = nextcord.Embed(title='Oops', description='Dazu hast du keine Rechte!',
                                   color=nextcord.Color.red())
            message = await ctx.response.send_message(embed=embed, ephemeral=True)
            await asyncio.sleep(2)
            await message.delete()
            return
        CHANNEL.__setitem__(author.id, channel.id)
        await ctx.response.send_modal(Modal())


class Modal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(
            title='Erstelle deine eigene Embed Message',
            custom_id='modal:embed',
            timeout=False,
            auto_defer=True
        )
        self.TITLE = nextcord.ui.TextInput(
            label='Title',
            style=nextcord.TextInputStyle.short,
            min_length=1,
            max_length=30,
            custom_id='input:title',
            required=False,
            placeholder='Das ist der Titel'
        )
        self.add_item(self.TITLE)
        self.DESCRIPTION = nextcord.ui.TextInput(
            label='Description',
            style=nextcord.TextInputStyle.paragraph,
            min_length=1,
            max_length=4000,
            custom_id='input:description',
            required=False,
            placeholder='Das ist die beschreibung'
        )
        self.add_item(self.DESCRIPTION)
        self.IMAGE = nextcord.ui.TextInput(
            label='Image',
            style=nextcord.TextInputStyle.short,
            max_length=4000,
            custom_id='input:image',
            required=False,
            placeholder='Link'
        )
        self.add_item(self.IMAGE)
        self.AUTHOR = nextcord.ui.TextInput(
            label='Author Text',
            style=nextcord.TextInputStyle.short,
            max_length=4000,
            custom_id='input:author',
            required=False,
            placeholder='TheSkyScout oder Wolkenlos Team'
        )
        self.add_item(self.AUTHOR)
        self.AUTHOR_URL = nextcord.ui.TextInput(
            label='Author Image',
            style=nextcord.TextInputStyle.short,
            max_length=4000,
            custom_id='input:author_image',
            required=False,
            placeholder='Link'
        )
        self.add_item(self.AUTHOR_URL)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        embed = nextcord.Embed(
            title=self.TITLE.value,
            description=self.DESCRIPTION.value,
            color=nextcord.Color.orange()
        )
        embed.set_image(url='https://cdn.discordapp.com/attachments/1053333236094337116/1053379533769801799/Line3.png')
        if self.AUTHOR and self.AUTHOR_URL is not None:
            embed.set_footer(text=f'{self.AUTHOR.value}',
                            icon_url=self.AUTHOR_URL.value)

        channel = interaction.user.guild.get_channel(CHANNEL.__getitem__(interaction.user.id))
        if self.IMAGE is None:
            await channel.send(embed=embed)
        else:
            image = nextcord.Embed(color=nextcord.Color.orange())
            image.set_image(self.IMAGE.value)
            await channel.send(embeds=[image, embed])
        mes = await interaction.response.send_message('Done!', ephemeral=True)
        await asyncio.sleep(2)
        await mes.delete()


def setup(bot):
    bot.add_cog(Embed(bot))
