import os
import discord
from datetime import datetime,timedelta 
from dateutil.relativedelta import relativedelta
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

@bot.command(name="RemindMe", help="Creates a reminder. Syntax: !RemindMe [int] [m|h|d|M|y] \"Message to record\"")
async def remind_me(ctx, amount: int, time, message)
    current_time=datetime.now()
    if time == "m":
        reminder_time=current_time + timedelta(minutes=amount)
    if time == "h":
        reminder_time=current_time + timedelta(hours=amount)
    if time == "d":
        reminder_time=current_time + timedelta(days=amount)
    if time == "M":
        reminder_time=current_time + relativedelta(months=+amount)
    if time == "y":
        reminder_time=current_time + relativedelta(years=+amount)

    await ctx.send("Your reminders has been set for {reminder_time} with message \"{message}\"")

bot.run(TOKEN)