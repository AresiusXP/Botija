import signal
import os
import discord
import sql
import asyncio
from datetime import datetime,timedelta 
from dateutil.relativedelta import relativedelta
from discord.ext import commands
#from dotenv import load_dotenv

#load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

def get_next_alarm():
    # to do:
    # sql query next alarm
    alarm_channel_id = 737465752495325207
    alarm_nick = 279976715764367371
    alarm_message = "Test 123"
    return alarm_channel_id, alarm_nick, alarm_message

def trigger_alarm(*args):
    alarm_channel_id, alarm_nick, alarm_message = get_next_alarm()
    asyncio.ensure_future(send_alarm_message(alarm_channel_id, alarm_nick, alarm_message))

async def send_alarm_message(alarm_channel_id, alarm_nick, alarm_message):
    channel = bot.get_channel(alarm_channel_id)
    member = bot.get_user(alarm_nick)
    await channel.send(f"{member.mention} - Reminder: {alarm_message}")

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


@bot.command(name="hello", help="It says hello back!")
async def hello_chat(ctx):
    await ctx.send(f'Hello {ctx.message.author.name}!')

@bot.command(name="RemindMe", help="Creates a reminder. Syntax: !RemindMe [int] [m|h|d|M|y] \"Message to record\"")
async def remind_me(ctx, amount: int, time, message):
    current_time=datetime.now()
    mapping = {
        "s": "seconds",
        "m": "minutes",
        "h": "hours"
        "d": "days",
        "M": "months",
        "y": "years"
    }

    params = {}
    if time in mapping:
        params[mapping[time]] = amount
        reminder_time = current_time + relativedelta(**params)
    else:
        await ctx.send("Wrong syntax. Please check `!help RemindMe`.")

    if reminder_time != "":
        print(f"New reminder created - Time: {reminder_time} - Message: {message} - Channel: {ctx.channel} - Channel ID: {ctx.channel.id} - Guild: {ctx.guild.name} - Author: {ctx.message.author.id}")

        signal.signal(signal.SIGALRM, trigger_alarm)
        signal.alarm(int((reminder_time - current_time).total_seconds()))
        
        reminder_format=reminder_time.strftime("%b %d %Y %H:%M")
        await ctx.send(f"Your reminder has been set for {reminder_format} with message \"{message}\"")

bot.run(TOKEN)