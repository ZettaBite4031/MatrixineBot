import os
import typing as t
import datetime as dt
import random as r
import math
import re
from io import BytesIO

import aiohttp
import discord
from discord.ext import commands
from discord.utils import get

TIME_REGEX = r"((?P<weeks>\d+)w)?((?P<days>\d+)d)?((?P<hours>\d+)h)?((?P<minutes>\d+)m)?((?P<seconds>\d+)s)?"


async def url_to_discord_file(url, file_name="image.txt"):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            image = await resp.read()
            return discord.File(BytesIO(image), filename=file_name)


def personalize_message(member: discord.Member, message, channel, old_level=0, new_level=0) -> str:
    # Handle simple replacements
    replacement_mapping = {
        "{user}": member.mention,
        "{nickname}": member.nick or member.global_name,
        "{username}": member.name,
        "{avatar}": member.avatar.url,
        "{server}": member.guild.name,
        "{channel}": channel,
        "{level}": new_level,
        "{old_level}": old_level,
        "{everyone}": "@everyone",
        "{here}": "@here",
    }

    for template, value in replacement_mapping.items():
        message = message.replace(f"{template}", f"{value}")

    # Handle custom channel placeholders
    channel_placeholders = re.findall(r"{#(.*?)}", message)
    for channel_mention in channel_placeholders:
        custom_channel = None
        if channel_mention.isdigit():
            # Channel was passed by ID
            custom_channel = member.guild.get_channel(int(channel_mention))
        else:
            # Channel was passed by name
            custom_channel = discord.utils.get(member.guild.channels, name=channel_mention)
        if custom_channel:
            message = message.replace(f"{{#{channel_mention}}}", custom_channel.mention)

    # Handle custom role placeholders
    role_placeholders = re.findall(r"{@(.*?)}", message)
    for role_mention in role_placeholders:
        role = None
        if role_mention.isdigit():
            # Role was passed by ID
            role = member.guild.get_role(int(role_mention))
        else:
            # Role was passed by name
            role = discord.utils.get(member.guild.roles, name=role_mention)
        if role:
            message = message.replace(f"{{@{role_mention}}}", role.mention)

    return message


def time_string_to_timedelta(time_string):
    time_dict = re.match(TIME_REGEX, time_string).groupdict()
    return dt.timedelta(weeks=int(time_dict.get("weeks") or 0),
                        days=int(time_dict.get("days") or 0),
                        hours=int(time_dict.get("hours") or 0),
                        minutes=int(time_dict.get("minutes") or 0),
                        seconds=int(time_dict.get("seconds") or 0))


def time_string_to_seconds(time_string):
    return time_string_to_timedelta(time_string).total_seconds()


def time_string_formatted_string(time_string):
    """
        Turns a time string into a datetime formatted string
        1d12h -> 1 day 12 hours in the future.
        Parameters
        -----------
        time_string: str
            Converts the string to the designated time in the future.
    """
    return timedelta_to_datetime(time_string_to_timedelta(time_string)).strftime("%Y-%m-%dT%H:%M:%SZ")


def time_string_to_datetime(time_string):
    """
        Turns a time string into a datetime
        1d12h -> 1 day 12 hours in the future.
        Parameters
        -----------
        time_string: str
            Converts the string to the designated date-time in the future.
    """
    return timedelta_to_datetime(time_string_to_timedelta(time_string))


def timedelta_to_string(timedelta):
    duration_string = ""
    if timedelta.days > 1:
        if (weeks := timedelta.days // 7) >= 1:
            duration_string += f"{weeks} weeks "
        if days := timedelta.days % 7:
            duration_string += f"{days} days "
    hours, remainder = divmod(timedelta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours >= 1:
        duration_string += f"{hours} hours "
    if minutes >= 1:
        duration_string += f"{minutes} minutes"
    if seconds >= 1:
        duration_string += f"{seconds} seconds"
    return duration_string


def timedelta_to_datetime(timedelta):
    """
        Returns a datetime object in the future by timedelta.

        Args:
            timedelta (datetime.timedelta): The input time delta.

        Returns:
            datetime (datetime.datetime): The date in the future.
    """
    return dt.datetime.now() + timedelta


def ordinal_suffix(n):
    """
        Returns the ordinal suffix for a given number.

        Args:
            n (int): The input number.

        Returns:
            str: The ordinal suffix for the number.
    """
    # Special cases for 11, 12, 13
    if 11 <= (n % 100) <= 13:
        suffix = "th"
    else:
        # Determine suffix based on the last digit
        last_digit = n % 10
        if last_digit == 1:
            suffix = "st"
        elif last_digit == 2:
            suffix = "nd"
        elif last_digit == 3:
            suffix = "rd"
        else:
            suffix = "th"

    return f"{n}{suffix}"