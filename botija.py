import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    
    # for guild in client.guilds:
    guild = discord.utils.get(bot.guilds)
    print(
        f'{bot.user.name} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

# @bot.event
# async def on_message(message):
#     if message.author == bot.user:
#         return

@bot.command(name="hello", help="It says hello back!")
async def hello_chat(ctx):
    await ctx.send(f'Hello {ctx.message.author.name}!')

bot.run(TOKEN)