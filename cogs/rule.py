import nextcord
from nextcord.ext import commands

import main


class EmbedModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(
            title="Service Request",
            custom_id="persistent_modal:service",
            timeout=None,
            auto_defer=True
        )
        self.emTile = nextcord.ui.TextInput(
            label='Embed Title',
            required=True,
            default_value='Hi',
            custom_id='id23',
            placeholder='Enter Embed',
            style=nextcord.TextInputStyle.paragraph
        )
        self.add_item(self.emTile)
        self.description = nextcord.ui.TextInput(
            label='Description',
            required=True,
            custom_id='id33',
            placeholder='Enter Description',
            style=nextcord.TextInputStyle.paragraph
        )
        self.add_item(self.description)
        self.test = nextcord.ui.TextInput(
            label='Description',
            required=True,
            custom_id='id43',
            placeholder='Enter Description',
            style=nextcord.TextInputStyle.paragraph
        )
        self.add_item(self.test)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        title = self.emTile.value
        desc = self.description.value
        em = nextcord.Embed(title=title, description=desc)
        return await interaction.response.send_message(embed=em)


class Rule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name='rules', guild_ids=[main.GUILD_ID])
    async def rule_cmd(self, interaction: nextcord.Interaction):
        await interaction.response.send_modal(EmbedModal())

def setup(bot):
    bot.add_cog(Rule(bot))
