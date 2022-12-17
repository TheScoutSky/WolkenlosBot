import aiosqlite
import nextcord
from nextcord.ext import commands
import main


class WarnSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.user_command(name="Verwarnen", guild_ids=[main.GUILD_ID])
    async def warn_command(self, interaction: nextcord.Interaction, member: nextcord.Member):
        await interaction.response.send_modal(Modal(member))


class Modal(nextcord.ui.Modal):
    def __init__(self, user: nextcord.Member):
        super().__init__(
            title=f'Warn {user.name}',
            custom_id='modal:warn',
            timeout=None,
            auto_defer=True
        )
        self.USER = user
        self.REASON = nextcord.ui.TextInput(
            label='Grund',
            min_length=1,
            max_length=1000,
            style=nextcord.TextInputStyle.paragraph,
            placeholder='Er war Gemein zu mir:c',
            custom_id='input:wanr:grund'
        )
        self.add_item(self.REASON)

    async def callback(self, interaction: nextcord.Interaction):
        async with aiosqlite.connect('main.db') as db:
            async with db.cursor() as cursor:
                await cursor.execute('SELECT reason FROM warns WHERE user = ?', (self.USER.id,))
                await cursor.execute('INSERT INTO warns (reason, user) VALUES (?, ?)',
                                     (self.REASON.value, self.USER.id,))
                warns = Warnings(self.USER).warns()
            await db.commit()
            embed = nextcord.Embed(title='**__WARN__**', color=nextcord.Color.red())
            embed.add_field(name='User', value=f'{self.USER.mention}', inline=True)
            embed.add_field(name='User-ID', value=f'{self.USER.id}', inline=True)
            embed.add_field(name='Warns', value=f'{warns.__sizeof__()}', inline=False)
            embed.add_field(name='Teammitglied', value=f'{interaction.user.mention}', inline=True)
            embed.add_field(name='Grund', value=f'{self.REASON.value}', inline=True)
            async with db.cursor() as cursor:
                await cursor.execute('SELECT channel FROM log WHERE key = ?', ('log',))
                ids = f'{await cursor.fetchone()}'.replace(",", "").replace("(", "").replace(")", "")
                log = interaction.user.guild.get_channel(int(ids))
                await log.send(embed=embed)


class Warnings(nextcord.Member):
    def __init__(self, user: nextcord.Member):
        self.user = user

    async def warns(self):
        async with aiosqlite.connect('main.db') as db:
            async with db.cursor() as cursor:
                await cursor.execute('SELECT reason FROM warns WHERE user = ?', (self.user.id,))
                num = 0
                data = cursor.fetchall()
                for _ in data:
                    num += 1
            return num


def setup(bot):
    bot.add_cog(WarnSystem(bot))
