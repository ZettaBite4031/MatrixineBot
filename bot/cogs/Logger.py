import io
import json
import datetime as dt
import os

from dateutil.relativedelta import relativedelta

import discord
import discord.flags
from discord.ext import commands

import util


class Logger(commands.Cog):
    """Handles logging events and commands"""
    def __init__(self, bot):
        self.bot = bot
        self.guilds = self.bot.MONGO_DB["Guilds"]
        self.leveling = self.bot.MONGO_DB["Leveling"]

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if not (result := self.guilds.find_one(member.guild.id)):
            return
        if not (member_joined_channel_id := result["data"]["log"]["member_joined_channel"]):
            return

        member_joined_channel = self.bot.get_channel(int(member_joined_channel_id))

        now = dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        now = dt.datetime.strptime(now, "%Y-%m-%d %H:%M:%S")
        then = member.created_at.strftime("%Y-%m-%d %H:%M:%S")
        then = dt.datetime.strptime(then, "%Y-%m-%d %H:%M:%S")
        diff = relativedelta(now, then)
        td = now - then

        years = diff.years
        months = diff.months
        days = diff.days

        if td.days >= result["data"]["log"]["new_account_age"]:
            msg = f"This account is {years} years, {months} months, {days} days old"
        else:
            seconds = td.total_seconds()
            seconds = seconds - (days * 24 * 3600)
            hours, remainder = divmod(seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            msg = f"This account is only {hours} hours, {minutes} minutes, and {seconds} seconds old!"

        embed = discord.Embed(title="Member joined",
                              description=f"{member.mention} is number {member.guild.member_count} to join.\n{msg}",
                              color=self.bot.COLOR, timestamp=dt.datetime.now())
        embed.set_footer(icon_url=self.bot.user.avatar.url, text=f"Logging developed by {self.bot.OWNER_USERNAME}")
        embed.set_author(name=f"{member.name}", icon_url=member.guild.icon.url)
        embed.set_thumbnail(url=member.avatar.url)
        await member_joined_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        if not (result := self.guilds.find_one(member.guild.id)):
            return
        if not (member_leave_channel_id := result["data"]["log"]["member_left_channel"]):
            return

        member_leave_channel = self.bot.get_channel(int(member_leave_channel_id))

        now = dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        now = dt.datetime.strptime(now, "%Y-%m-%d %H:%M:%S")
        then = member.joined_at.strftime("%Y-%m-%d %H:%M:%S")
        then = dt.datetime.strptime(then, "%Y-%m-%d %H:%M:%S")
        diff = relativedelta(now, then)
        td = now - then

        years = diff.years
        months = diff.months
        days = diff.days

        if td.days >= result["data"]["log"]["new_account_age"]:
            msg = f"This account joined {years} years, {months} months, {days} days ago"
        else:
            seconds = td.total_seconds()
            seconds = seconds - (days * 24 * 3600)
            hours, remainder = divmod(seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            msg = f"This account was here for only {hours} hours, {minutes} minutes, and {seconds} seconds!"

        roles = ' '.join([x.mention for x in member.roles if x.name not in ('@here', '@everyone')])
        embed = discord.Embed(title="Member left",
                              description=f"{msg}\n**Roles:** {roles}",
                              color=self.bot.COLOR, timestamp=dt.datetime.now())
        embed.set_footer(icon_url=self.bot.user.avatar.url, text=f"Logging developed by {self.bot.OWNER_USERNAME}")
        embed.set_author(name=f"{member.name}", icon_url=member.guild.icon.url)
        embed.set_thumbnail(url=member.avatar.url)
        await member_leave_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.content == after.content:
            return
        if not (result := self.guilds.find_one(before.guild.id)):
            return
        if not (logs := result["data"]["log"]):
            return
        if not (edited_message_channel_id := logs["edited_message_channel"]):
            return
        edited_message_channel = self.bot.get_channel(int(edited_message_channel_id))

        embed = discord.Embed(
            title="Message Edited",
            color=self.bot.COLOR,
            timestamp=dt.datetime.utcnow()
        )
        embed.add_field(name="**Member:**", value=after.author.mention, inline=False)
        embed.add_field(name="**Original:**", value=f"`{before.content}`", inline=True)
        embed.add_field(name="**Current:**", value=f"`{after.content}`", inline=True)
        embed.add_field(name="**Channel:**", value=before.channel.mention, inline=False)
        embed.add_field(name="**Message ID:**", value=before.id, inline=False)
        embed.set_footer(text=f"ID: {before.author.id}")
        embed.set_thumbnail(url=before.author.avatar.url)

        await edited_message_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if not (result := self.guilds.find_one(message.guild.id)):
            return
        if not (logs := result["data"]["log"]):
            return
        if not (deleted_message_channel_id := logs["deleted_message_channel"]):
            return
        deleted_message_channel = self.bot.get_channel(int(deleted_message_channel_id))

        embed = discord.Embed(
            title="Message Deleted",
            color=self.bot.COLOR,
            timestamp=dt.datetime.utcnow()
        )
        embed.add_field(name="**Member:**", value=message.author.mention, inline=False)
        embed.add_field(name="**Message:**", value=f"`{message.content}`", inline=True)
        embed.add_field(name="**Channel:**", value=message.channel.mention, inline=True)
        embed.add_field(name="**Message ID:**", value=message.id, inline=False)
        embed.set_footer(text=f"ID: {message.author.id}")
        embed.set_thumbnail(url=message.author.avatar.url)

        await deleted_message_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages: list[discord.Message]):
        guild: discord.Guild = messages[0].guild
        if not (result := self.guilds.find_one(guild.id)):
            return
        if not (logs := result["data"]["log"]):
            return
        if not (deleted_message_channel_id := logs["deleted_message_channel"]):
            return
        deleted_message_channel = self.bot.get_channel(int(deleted_message_channel_id))

        message_count = len(messages)
        with open(f"purge.json", "w+") as j:
            data = dict()
            for message in messages:
                author: discord.User = message.author
                entree = {
                    message.id: {
                        "Username": f"{author.name}",
                        "ID": author.id,
                        "Message": message.content,
                        "Attachments": [attachment.url for attachment in message.attachments]
                    }
                }
                data.update(entree)
            text_data = json.dumps(data, indent=4)
            bytes_data = io.BytesIO(text_data.encode("utf-8"))

        embed = discord.Embed(
            title=f"{message_count} messages purged in {messages[0].channel.mention}",
            color=self.bot.COLOR,
            timestamp=dt.datetime.utcnow()
        )
        await deleted_message_channel.send(embed=embed, file=discord.File(fp=bytes_data, filename="purge.json"))
        os.remove("purge.json")

    def permission_string_from_list(self, perms: list[str]) -> str:
        ret = ""
        perm_dict = dict()
        for perm in util.PERMISSION_DICT.keys():
            perm_dict[perm] = util.PERMISSION_DICT[perm] if perm in perms else None
        i = 0
        ret += "```"
        for k, v in perm_dict.items():
            if not v:
                continue
            i += 1
            ret += f"{k} - "
            if (i % 2) == 0:
                ret = ret[:-2]
                ret += "\n"
        ret += "```"
        return ret

    def permission_string(self, role: discord.Role) -> (str, list[str]):
        enabled_permissions = [perm.replace("_", " ").title() for perm, value in role.permissions if value]
        return self.permission_string_from_list(enabled_permissions), enabled_permissions

    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role):
        if not (result := self.guilds.find_one(role.guild.id)):
            return
        if not (logs := result["data"]["log"]):
            return
        if not (role_create_channel_id := logs["role_create_channel"]):
            return
        role_create_channel = self.bot.get_channel(int(role_create_channel_id))

        enabled_permissions = [perm.replace("_", " ").title() for perm, value in role.permissions if value]
        embed = discord.Embed(title="Role created",
                              description=f"**Name**: {role.mention}\n"
                                          f"**ID**: {role.id}\n**Color**: {hex(role.color.value)}\n"
                                          f"**Position**: {role.position}\n"
                                          f"**{len(enabled_permissions)} Permissions**:\n```",
                              color=role.color,
                              timestamp=dt.datetime.now())
        embed.set_footer(text=f"Logging developed by {self.bot.OWNER_USERNAME}", icon_url=self.bot.user.avatar.url)
        embed.set_author(name="Role creation event", icon_url=role.guild.icon.url)

        embed.description += self.permission_string(role)

        if "Administrator" in enabled_permissions:
            warning = "⚠**!WARNING!**⚠\nADMINISTRATOR IS ENABLED FOR THIS ROLE\n\n"
            warning += embed.description
            embed.description = warning
        await role_create_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        if not (result := self.guilds.find_one(role.guild.id)):
            return
        if not (logs := result["data"]["log"]):
            return
        if not (role_delete_channel_id := logs["role_delete_channel"]):
            return
        role_delete_channel = self.bot.get_channel(int(role_delete_channel_id))

        enabled_permissions = [perm.replace("_", " ").title() for perm, value in role.permissions if value]
        embed = discord.Embed(title="Role deleted",
                              description=f"**Name**: {role.name}\n"
                                          f"**ID**: {role.id}\n**Color**: {hex(role.color.value)}\n"
                                          f"**Position**: {role.position}\n"
                                          f"**{len(enabled_permissions)} Permissions**:\n```",
                              color=role.color,
                              timestamp=dt.datetime.now())
        embed.set_footer(text=f"Logging developed by {self.bot.OWNER_USERNAME}", icon_url=self.bot.user.avatar.url)
        embed.set_author(name="Role deletion event", icon_url=role.guild.icon.url)

        embed.description += self.permission_string(role)

        await role_delete_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_update(self, before: discord.Role, after: discord.Role):
        if not (result := self.guilds.find_one(before.guild.id)):
            return
        if not (logs := result["data"]["log"]):
            return
        if not (role_edited_channel_id := logs["role_edited_channel"]):
            return
        role_edited_channel = self.bot.get_channel(int(role_edited_channel_id))
        before_permission_string, before_permissions = self.permission_string(before)
        after_permission_string, after_permissions = self.permission_string(after)

        description = ""
        if after.name != before.name:
            description = f"**Name**: {before.name} -> {after.mention}"
        else:
            description = f"**Name**: {after.name}"
        description += f"\n**ID**: {after.id}\n"
        if after.color.value != before.color.value:
            description += f"**Color**: {hex(before.color.value)} -> {hex(after.color.value)}"
        else:
            description += f"**Color**: {hex(after.color.value)}"
        if after.position != before.position:
            pos = "Moved up" if after.position > before.position else "Moved down"
            description += f"\n**Position**: {before.position} -> {after.position} | {pos}\n"
        else:
            description += f"\n**Position**: {after.position}\n"

        if not (changed_perms := list(set(after_permissions) ^ set(before_permissions))):
            description += f"No permissions changed"
        else:
            description += (f"**{len(changed_perms)} Permissions changed:**\n"
                            f"{self.permission_string_from_list(changed_perms)}")
            if "Administrator" in changed_perms:
                warning = "⚠**!WARNING!**⚠\nADMINISTRATOR IS ENABLED FOR THIS ROLE\n\n"
                warning += description
                description = warning

        embed = discord.Embed(title="Role edited", description=description,
                              color=after.color, timestamp=dt.datetime.now())
        embed.set_author(name="Role changed event", icon_url=after.guild.icon.url)
        embed.set_footer(text=f"Logging developed by {self.bot.OWNER_USERNAME}", icon_url=self.bot.user.avatar.url)
        await role_edited_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        await self.on_member_update(before, after)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if not (result := self.guilds.find_one(before.guild.id)):
            return
        if not (logs := result["data"]["log"]):
            return
        if not (member_general_update_channel_id := logs["member_general_update_channel"]):
            return
        general_update_channel = self.bot.get_channel(int(member_general_update_channel_id))

        title = ""
        embed = discord.Embed(color=self.bot.COLOR, timestamp=dt.datetime.now())
        _and = False
        if before.name != after.name:
            _and = True
            title += "Username "
            embed.add_field(name="Original", value=before.name, inline=True)
            embed.add_field(name="Current", value=after.name, inline=True)
            embed.add_field(name="", value="", inline=True)

        if before.display_name != after.display_name:
            title += "Nickname "
            embed.add_field(name="Original", value=before.display_name, inline=True)
            embed.add_field(name="Current", value=after.display_name, inline=True)
            embed.add_field(name="", value="", inline=True)

        if before.guild_avatar.url != after.guild_avatar.url:
            if _and:
                title += "and "
            title += "Server Profile Picture "
            embed.set_thumbnail(url=before.guild_avatar.url)
            embed.set_image(url=after.guild_avatar.url)

        elif before.avatar.url != after.avatar.url:
            if _and:
                title += "and "
            title += "Profile Picture "
            embed.set_thumbnail(url=before.avatar.url)
            embed.set_image(url=after.avatar.url)

        if title:
            title += "Update"
            embed.title = title
            embed.set_footer(text=f"Logging developed by {self.bot.OWNER_USERNAME}", icon_url=self.bot.user.avatar.url)
            embed.set_author(name="User update event!", icon_url=before.guild.icon.url)
            await general_update_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        if not (result := self.guilds.find_one(channel.guild.id)):
            return
        if not (logs := result["data"]["log"]):
            return
        if not (channel_create_channel_id := logs["channel_create_channel"]):
            return
        channel_create_channel = self.bot.get_channel(int(channel_create_channel_id))
        embed = discord.Embed(title="Channel created!",
                              description=f"A new channel has been created: {channel.mention}\n"
                                          f"Name: {channel.name}\n"
                                          f"Category: {channel.category or 'No category'}\n"
                                          f"ID: {channel.id}\n"
                                          f"Type: {str(channel.type).title()}")
        embed.set_footer(text=f"Logging developed by {self.bot.OWNER_USERNAME}", icon_url=self.bot.user.avatar.url)
        embed.set_author(name=f"Channel creation event in {channel.guild.name}", icon_url=channel.guild.icon.url)
        await channel_create_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        if not (result := self.guilds.find_one(channel.guild.id)):
            return
        if not (logs := result["data"]["log"]):
            return
        if not (channel_delete_channel_id := logs["channel_delete_channel"]):
            return
        channel_delete_channel = self.bot.get_channel(int(channel_delete_channel_id))
        embed = discord.Embed(title="Channel deleted!",
                              description=f"A channel has been deleted!\n"
                                          f"Name: {channel.name}\n"
                                          f"Category: {channel.category or 'No category'}\n"
                                          f"ID: {channel.id}\n"
                                          f"Type: {str(channel.type).title()}")
        embed.set_footer(text=f"Logging developed by {self.bot.OWNER_USERNAME}", icon_url=self.bot.user.avatar.url)
        embed.set_author(name=f"Channel deletion event in {channel.guild.name}", icon_url=channel.guild.icon.url)
        await channel_delete_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel):
        if not (result := self.guilds.find_one(before.guild.id)):
            return
        if not (logs := result["data"]["log"]):
            return
        if not (channel_update_channel_id := logs["channel_update_channel"]):
            return
        channel_update_channel = self.bot.get_channel(int(channel_update_channel_id))

        title = ""
        embed = discord.Embed(color=self.bot.COLOR, timestamp=dt.datetime.now())
        _and = False
        if before.name != after.name:
            _and = True
            title += "Name "
            embed.add_field(name="Original", value=before.name, inline=True)
            embed.add_field(name="Current", value=after.name, inline=True)
            embed.add_field(name="", value="", inline=True)

        if before.category != after.category:
            title += "Category "
            embed.add_field(name="Original", value=before.category, inline=True)
            embed.add_field(name="Current", value=after.category, inline=True)
            embed.add_field(name="", value="", inline=True)

        if before.position != after.position:
            if _and:
                title += "and "
            title += "Position "
            embed.add_field(name="Original", value=before.position, inline=True)
            embed.add_field(name="Current", value=after.position, inline=True)
            embed.add_field(name="", value="", inline=True)

        if title:
            title += "Update"
            embed.title = title
            embed.set_footer(text=f"Logging developed by {self.bot.OWNER_USERNAME}", icon_url=self.bot.user.avatar.url)
            embed.set_author(name=f"Channel deletion event in {before.guild.name}", icon_url=before.guild.icon.url)
            await channel_update_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState,
                                    after: discord.VoiceState):
        if not (result := self.guilds.find_one(member.guild.id)):
            return
        if not (logs := result["data"]["log"]):
            return
        if not (voice_update_channel_id := logs["voice_update_channel"]):
            return
        voice_update_channel = self.bot.get_channel(int(voice_update_channel_id))
        description = ""
        if before.channel is None and after.channel is not None:
            description = f"{member.mention} ({member.id}) has joined {after.channel.mention}."

            # Check if the member left a voice channel
        if before.channel is not None and after.channel is None:
            description = f"{member.mention} ({member.id}) has left  {before.channel.mention}."

            # Check if the member switched voice channels
        if before.channel is not None and after.channel is not None and before.channel.id != after.channel.id:
            description = f"{member.mention} ({member.id}) has left {before.channel} and joined {after.channel}."

        if description:
            embed = discord.Embed(title="Voice State Update", description=description,
                                  color=self.bot.COLOR, timestamp=dt.datetime.now())

            embed.set_footer(text=f"Logging developed by {self.bot.OWNER_USERNAME}", icon_url=self.bot.user.avatar.url)
            guild = (before.channel or after.channel).guild
            embed.set_author(name=f"Channel deletion event in {guild.name}", icon_url=guild.icon.url)
            await voice_update_channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Logger(bot))
