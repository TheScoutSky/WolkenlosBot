import asyncio
import base64
import os
import random
import time
from io import BytesIO

import aiohttp
import nextcord
import openai
from chatgpt import Conversation
from nextcord.ext import commands

import main

api_key = os.getenv('API_KEY')
openai.api_key = api_key
chatgpt = Conversation(
    access_token=api_key
)


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
    async def generate(self, ctx: nextcord.Interaction, prompt: str):
        ETA = int(time.time() + 60)
        embed = nextcord.Embed(title="Generiere dein eigenes Bild", color=nextcord.Color.orange())
        embed.add_field(name=f'**Promt**', value=prompt, inline=False)
        embed.add_field(name=f'**Wartezeit**', value=f'<t:{ETA}:R>')
        embed.set_footer(text='Made with OpenAI',
                         icon_url='https://dwglogo.com/wp-content/uploads/2019/03/1600px-OpenAI_logo.png')
        msg = await ctx.send(embed=embed, ephemeral=False)
        async with aiohttp.request("POST", "https://backend.craiyon.com/generate", json={"prompt": prompt}) as resp:
            r = await resp.json()
            images = r['images']
            image = BytesIO(base64.decodebytes(images[0].encode('utf-8')))
            embed = nextcord.Embed(title="Generiere dein eigenes Bild", color=nextcord.Color.orange())
            embed.add_field(name=f'**Prompt**', value=prompt, inline=False)
            embed.add_field(name=f'**Wartezeit**', value=f'Fertig')
            embed.set_footer(text='Made with OpenAI',
                             icon_url='https://dwglogo.com/wp-content/uploads/2019/03/1600px-OpenAI_logo.png')
            await msg.edit(embed=embed,
                           file=nextcord.File(image, "generatedImage.png"),
                           view=DropdownView(msg, images, ctx.user.id))

    @nextcord.slash_command(name='question', guild_ids=[main.GUILD_ID])
    async def question(self, interaction: nextcord.Interaction, question: str):
        ETA = int(time.time() + 30)
        embed = nextcord.Embed(title='Question', color=nextcord.Color.orange())
        embed.add_field(name='Frage', value=question, inline=False)
        embed.add_field(name='Antwort', value=f'<t:{ETA}:R>', inline=False)
        embed.set_footer(text='Made with OpenAI',
                         icon_url='https://dwglogo.com/wp-content/uploads/2019/03/1600px-OpenAI_logo.png')
        me = await interaction.response.send_message(embed=embed)
        completions = openai.Completion.create(
            model="text-davinci-003",
            prompt=question,
            temperature=0,
            max_tokens=4000,
            best_of=1,
            n=1,
        )
        await asyncio.sleep(10)
        message2 = completions.choices[0].text
        print(completions.__dict__)
        message = f'{message2.strip()}'.replace('?', '').replace('\n', '')
        embed = nextcord.Embed(title='Question', color=nextcord.Color.orange())
        embed.add_field(name='Frage', value=question, inline=False)
        embed.add_field(name='Antwort', value=f'{message.strip()}', inline=False)
        embed.set_footer(text='Made with OpenAI',
                         icon_url='https://dwglogo.com/wp-content/uploads/2019/03/1600px-OpenAI_logo.png')
        await me.edit(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, messages: nextcord.Message):
        FRAGE_WORTER = ['Weshalb', 'Wieso', 'Wer', 'Warum', 'Wann', 'weshalb', 'wieso', 'wer', 'warum', 'wann', '?']
        rand = random.randrange(1, 3)
        for mention in messages.mentions:
            if mention.id == main.CLIENT_ID:
                completions = openai.Completion.create(
                    model="text-davinci-003",
                    prompt=messages.content,
                    temperature=0,
                    max_tokens=4000,
                    best_of=1,
                    n=1, )
                await asyncio.sleep(2)
                message2 = completions.choices[0].text
                print(completions.__dict__)
                message = f'{message2.strip()}'.replace('?', '').replace('\n', '').replace('@Kai_Kai_Kai_Kai', f'{messages.guild.get_member(820333840836460565).mention}').replace('@Kirb#0001', f'{messages.guild.get_member(820333840836460565).mention}')
                embed = nextcord.Embed(title='Question', color=nextcord.Color.orange())
                embed.add_field(name='Frage', value=messages.content, inline=False)
                embed.add_field(name='Antwort', value=f'{message.strip()}', inline=False)
                embed.set_footer(text='Made with OpenAI',
                                 icon_url='https://dwglogo.com/wp-content/uploads/2019/03/1600px-OpenAI_logo.png')
            mes: nextcord.Message = await messages.channel.send(embed=embed)
            view = Button(mes)
            await mes.edit(view=view)
            await view.wait()
        for words in FRAGE_WORTER:
            if messages.content.__contains__(words):
                if not rand == 1:
                    return
                completions = openai.Completion.create(
                    model="text-davinci-003",
                    prompt=messages.content,
                    temperature=0,
                    max_tokens=4000,
                    best_of=1,
                    n=1, )
                await asyncio.sleep(2)
                message2 = completions.choices[0].text
                print(completions.__dict__)
                message = f'{message2.strip()}'.replace('?', '').replace('\n', '')
                embed = nextcord.Embed(title='Question', color=nextcord.Color.orange())
                embed.add_field(name='Frage', value=messages.content, inline=False)
                embed.add_field(name='Antwort', value=f'{message.strip()}', inline=False)
                embed.set_footer(text='Made with OpenAI',
                                 icon_url='https://dwglogo.com/wp-content/uploads/2019/03/1600px-OpenAI_logo.png')
                mes: nextcord.Message = await messages.channel.send(embed=embed)
                view = Button(mes)
                await mes.edit(view=view)
                await view.wait()


class Button(nextcord.ui.View):
    def __init__(self, message):
        super().__init__()
        self.value = None
        self.message = message

    @nextcord.ui.button(label='Delete', style=nextcord.ButtonStyle.red, custom_id='button:ai:del')
    async def delete(self, button: nextcord.Button, interaction: nextcord.Interaction):
        await self.message.delete()


def setup(bot):
    bot.add_cog(Fun(bot))
