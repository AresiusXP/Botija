import signal
import os
import discord
import sql
import asyncio
import alarm
from datetime import datetime,timedelta 
from dateutil.relativedelta import relativedelta
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='!')
global next_alarm

def trigger_alarm(*args):
    trigger_alarm = next_alarm
    print("Trigger Alarm Time: {0}".format(trigger_alarm.reminder_time.strftime("%b %d %Y %H:%M:%S")))
    asyncio.ensure_future(send_alarm_message(trigger_alarm.channel_id, trigger_alarm.author_id, trigger_alarm.message))

async def send_alarm_message(alarm_channel_id, alarm_author_id, alarm_message):
    channel = bot.get_channel(alarm_channel_id)
    member = bot.get_user(alarm_author_id)
    await channel.send(f"{member.mention} - Reminder: {alarm_message}")

@bot.event
async def on_ready():
    # Setup alarm table
    if not sql.alarm_table_exists():
        sql.create_table

    # Get next alarm
    global next_alarm
    next_alarm = sql.get_next_alarm()

    # Setup alarm signal
    signal.signal(signal.SIGALRM, trigger_alarm)
    signal.alarm(int((next_alarm.reminder_time - datetime.now()).total_seconds()))

    print(f'{bot.user.name} has connected to Discord!')
    
    # for guild in client.guilds:
    guild = discord.utils.get(bot.guilds)
    print(
        f'{bot.user.name} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})\n'
        "Next alarm: {0} by {1}\n".format(next_alarm.reminder_time.strftime("%b %d %Y %H:%M"), next_alarm.author_name)
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
        "h": "hours",
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
        print(f"""New reminder created 
                Time: {reminder_time}
                Message: {message}
                Channel: {ctx.channel.name}
                Channel ID: {ctx.channel.id}
                Guild: {ctx.guild.name}
                Author: {ctx.message.author.name}""")
        
        # Create alarm object and insert in DB
        new_alarm = alarm.Alarm(reminder_time, message, ctx.channel.name, ctx.channel.id, ctx.guild.name, ctx.message.author.id, ctx.message.author.name)
        sql.create_alarm(new_alarm)

        # Renew signal
        next_alarm = sql.get_next_alarm()
        print("Next alarm: {0} by {1}".format(next_alarm.reminder_time.strftime("%b %d %Y %H:%M"), next_alarm.author_name))
        
        signal.signal(signal.SIGALRM, trigger_alarm)
        signal.alarm(int((next_alarm.reminder_time - datetime.now()).total_seconds()))
        
        reminder_format=reminder_time.strftime("%b %d %Y %H:%M")
        await ctx.send(f"Your reminder has been set for {reminder_format} with message \"{message}\"")

if sql.test_sql_connection() == "success":
    bot.run(TOKEN)
else:
    print("Connection to SQL Failed.")