import datetime

class Alarm:
    def __init__(self, reminder_time: datetime, message, channel, channel_id, guild_name, author_id, author_name):
        self.reminder_time = reminder_time
        self.message = message
        self.channel = channel
        self.channel_id = channel_id
        self.guild_name = guild_name
        self.author_id = author_id
        self.author_name = author_name