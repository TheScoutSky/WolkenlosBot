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
        self.COLOR_RED = nextcord.ui.TextInput(
            label='Color - RED',
            style=nextcord.TextInputStyle.short,
            max_length=3,
            custom_id='input:color',
            required=False,
            default_value='255'
        )
        self.add_item(self.COLOR_RED)
        self.COLOR_GREEN = nextcord.ui.TextInput(
            label='Color - Green',
            style=nextcord.TextInputStyle.short,
            max_length=3,
            custom_id='input:color2',
            required=False,
            default_value='156'
        )
        self.add_item(self.COLOR_GREEN)
        self.COLOR_BLUE = nextcord.ui.TextInput(
            label='Color - Blue',
            style=nextcord.TextInputStyle.short,
            max_length=3,
            custom_id='input:color3',
            required=False,
            default_value='0'
        )
        self.add_item(self.COLOR_BLUE)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        embed = nextcord.Embed(
            title=self.TITLE.value,
            description=self.DESCRIPTION.value,
            color=nextcord.Color.from_rgb(int(self.COLOR_RED.value), int(self.COLOR_GREEN.value), int(self.COLOR_BLUE.value))
        )
        embed.set_image(url='https://cdn.discordapp.com/attachments/1053333236094337116/1053379533769801799/Line3.png')
        embed.set_footer(text=f'{interaction.user.top_role.name} | {interaction.user.name}', icon_url=interaction.user.avatar)
        channel = interaction.user.guild.get_channel(CHANNEL.__getitem__(interaction.user.id))
        await channel.send(embed=embed)
        mes = await interaction.response.send_message('Done!', ephemeral=True)
        await asyncio.sleep(2)
        await mes.delete()


def setup(bot):
    bot.add_cog(Embed(bot))
