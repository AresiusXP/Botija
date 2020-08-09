import signal
import os
import discord
import sql
import asyncio
import alarm
import re
import random
from datetime import datetime,timedelta 
from dateutil.relativedelta import relativedelta
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='!')
next_alarm = ""
DRY_RUN = os.getenv('DRY_RUN')

def trigger_alarm(*args):
    global next_alarm
    trigger_alarm = next_alarm
    print("Trigger Alarm Time: {0}".format(trigger_alarm.reminder_time.strftime("%b %d %Y %H:%M:%S")))
    asyncio.ensure_future(send_alarm_message(trigger_alarm.channel_id, trigger_alarm.author_id, trigger_alarm.message))
    set_signal_next_alarm()

def set_signal_next_alarm():
    global next_alarm
    next_alarm = sql.get_next_alarm()
    if next_alarm:
        # Setup alarm signal
        signal.signal(signal.SIGALRM, trigger_alarm)
        signal.alarm(int((next_alarm.reminder_time - datetime.now()).total_seconds()))
        
        # Print next alarm
        print("Next alarm: {0} by {1}".format(next_alarm.reminder_time.strftime("%b %d %Y %H:%M"), next_alarm.author_name))
    else:
        print("No alarms next.")


async def send_alarm_message(alarm_channel_id, alarm_author_id, alarm_message):
    channel = bot.get_channel(alarm_channel_id)
    member = bot.get_user(alarm_author_id)
    await channel.send(f"{member.mention} - Reminder: \"{alarm_message}\"")

@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds)
    print(
        f'{bot.user.name} has connected to Discord!\n'
        f'{bot.user.name} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

    # Setup alarm table
    if not sql.alarm_table_exists():
        print("No database found. Creating...")
        sql.create_table()

    # Get next alarm
    set_signal_next_alarm()

@bot.event
async def on_member_join(member):
    if member.guild.name == "Cacodemons":
        default_channel = member.guild.text_channels[0]
        await default_channel.send(file=discord.File('images/cacodemons.png'))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    chance = 10
    curr_random = random.randint(0,1000)
    if chance > curr_random:
        pepiline = str(sql.get_pepiline())
        if "@" in pepiline:
            members = message.channel.members
            for member in members:
                regex_str = re.search(r'\@\w+', pepiline).group(0)[1:]
                if regex_str in str(member):
                    pepiline = re.sub(r'\@\w+', member.mention, pepiline)
        await message.channel.send(pepiline)
        
    await bot.process_commands(message)

@bot.command(name="pepi", help="Random Pepi ML line")
async def pepi_cmd(ctx):
    pepiline = str(sql.get_pepiline())
    if "@" in pepiline:
        members = ctx.message.channel.members
        for member in members:
            regex_str = re.search(r'\@\w+', pepiline).group(0)[1:]
            if regex_str in str(member):
                pepiline = re.sub(r'\@\w+', member.mention, pepiline)
    await ctx.send(pepiline)

@bot.command(name="hello", help="It says hello back!")
async def hello_chat(ctx):
    await ctx.send(f'Hello {ctx.message.author.name}!')
    print(f"{ctx.message.author.name} just said hello to me.")

@bot.command(name="contribute", help="Prints the github address of the bot")
async def contribute(ctx):
    await ctx.send(f"Hey {ctx.message.author.name}, if you want to contribute I live here: https://github.com/AresiusXP/Botija.git")
    print(f"{ctx.message.author.name} wants to contribute")

@bot.command(name="RemindMe", help="Creates a reminder. Uses UTC.\nSyntax:\n!RemindMe [int] [m|h|d|M|y] \"Message to record\"\n!RemindMe dd/mm/yyyy HH:MM\"Message to record\"")
async def remind_me(ctx, amount, time, *message):
    time_reg = re.compile("\d{2}:\d{2}$")
    date_reg = re.compile("\d{2}/\d{2}/\d{4}$")
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
        params[mapping[time]] = int(amount)
        reminder_time = current_time + relativedelta(**params)
    elif (time_reg.match(time) is not None) and (date_reg.match(amount) is not None):
        reminder_time = datetime.strptime(amount + " " + time, "%d/%m/%Y %H:%M")
        print("Using reminder_time with dd/mm/yyyy. {0}".format(reminder_time.strftime("%b %d %Y %H:%M")))
    else:
        await ctx.send("Wrong syntax. Please check `!help RemindMe`.")

    formatted_message = " ".join(message)

    if reminder_time != "":
        print(f"""New reminder created 
                Time: {reminder_time}
                Message: {formatted_message}
                Channel: {ctx.channel.name}
                Channel ID: {ctx.channel.id}
                Guild: {ctx.guild.name}
                Author: {ctx.message.author.name}""")
        
        # Create alarm object and insert in DB
        new_alarm = alarm.Alarm(reminder_time, formatted_message, ctx.channel.name, ctx.channel.id, ctx.guild.name, ctx.message.author.id, ctx.message.author.name)
        sql.create_alarm(new_alarm)

        # Renew signal
        set_signal_next_alarm()
        
        reminder_format=reminder_time.strftime("%b %d %Y %H:%M")
        await ctx.send(f"Your reminder has been set for {reminder_format} with message \"{formatted_message}\"")

if sql.test_sql_connection() == "success":
    if int(DRY_RUN) != 1:
        bot.run(TOKEN)
    else: 
        print("Dry run finished. No discord connection attempted.")
else:
    print("Connection to SQL Failed.")