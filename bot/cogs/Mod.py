import datetime as dt
import io
import typing as t

import discord
from discord.ext import commands

import util


class Mod(commands.Cog):
    """Handles moderation commands and lets people abuse their power."""
    def __init__(self, bot):
        self.bot = bot
        self.guilds = self.bot.MONGO_DB["Guilds"]

    async def timeout_user(self, user, guild, time):
        headers = {"Authorization", f"Bot: {self.bot.http.token}"}
        url = f"https://discord.com/api/v9/guilds/{guild.id}/members/{user.id}"
        timeout = (dt.datetime.utcnow() + dt.timedelta(seconds=time)).isoformat()
        json = {"communication_disabled_until": timeout}
        async with self.bot.session.path(url, json=json, headers=headers) as session:
            if session.status in range(200, 299):
                return True
            return False

    @commands.command(name="ban", description="Bans the mentioned users. Can accept multiple users at once.")
    @commands.has_permissions(ban_members=True)
    async def ban_user_command(self, ctx, targets: commands.Greedy[discord.User], *,
                               reason: t.Optional[str] = "No reason"):
        if not len(targets):
            return await ctx.send("Missing required argument -> target(s)")

        banned = ""
        colorAvg = ctx.author.id
        for target in targets:
            guild = ctx.guild
            member = guild.get_member(target.id)
            banned += f"{target.name}\n"
            if member:
                if ctx.guild.me.top_role.position > target.top_role.position and not target.guild_permissions.administrator:
                    await target.ban(reason=reason)

                elif ctx.guild.me.top_role.position < target.top_role.position or target.guild_permissions.administrator:
                    await ctx.send(f"I can't ban {target.name}")

            else:
                await guild.ban(target, reason=reason)

            await self.on_member_ban(guild, target, reason, ctx.author)

            colorAvg += (ctx.author.id + target.id) / 2

        if len(targets) == 1:
            msg = f"1 member banned for {reason.lower()}"
        else:
            msg = f"{len(targets)} members banned {reason.lower()}"

        embed = discord.Embed(
            title=msg,
            description=f"{ctx.author.mention} had {msg}:\n{banned}",
            color=discord.Color.random(seed=colorAvg),
            timestamp=dt.datetime.utcnow()
        )
        embed.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}",
                         icon_url=ctx.author.avatar_url)
        embed.set_footer(text="Imagine being a loser.")
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User, reason: t.Optional[str],
                            moderator: t.Optional[discord.Member]):
        if not (result := self.guilds.find_one(guild.id)):
            return
        logs = result["data"]["logs"]
        if not (ban_channel := logs["member_ban_channel"]):
            return

        embed = discord.Embed(
            title="Member Banned",
            description=f"**Offender:** {user.name}\n"
                        f"**Reason:** {reason or 'not banned from bot'}\n"
                        f"**Responsible moderator:** {moderator.mention or 'not banned from bot'}",
            color=self.bot.COLOR,
            timestamp=dt.datetime.utcnow()
        )
        embed.set_footer(text=f"ID: {user.id}")
        embed.set_author(icon_url=moderator.avatar.url or "", name=moderator.name or "Not banned from bot")
        await ban_channel.send(embed=embed)

    @commands.command(name="unban", description="Unbans the mentioned users. Can accept multiple users at once.")
    @commands.has_permissions(ban_members=True)
    async def unban_member_command(self, ctx, targets: commands.Greedy[discord.User], *,
                                   reason: t.Optional[str] = "No reason"):
        if not len(targets):
            return await ctx.send("Missing required argument -> target(s)")

        unbanned = ""
        for target in targets:
            await ctx.guild.unban(target, reason=reason)
            unbanned += f"{target.name}\n"

        if len(targets) == 1:
            msg = f"1 member unbanned for {reason.lower()}"
        else:
            msg = f"{len(targets)} members unbanned for {reason.lower()}"

        embed = discord.Embed(
            title=msg,
            description=f"{ctx.author.mention} had {msg}:\n{unbanned}",
            color=discord.Color.random(seed=ctx.author.id),
            timestamp=dt.datetime.utcnow()
        )
        embed.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}",
                         icon_url=ctx.author.avatar_url)
        embed.set_footer(text="No longer losers.")
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User, reason: t.Optional[str],
                              moderator: t.Optional[discord.Member]):
        if not (result := self.guilds.find_one(guild.id)):
            return
        logs = result["data"]["logs"]
        if not (ban_channel := logs["member_ban_channel"]):
            return

        embed = discord.Embed(
            title="Member Unbanned",
            description=f"**User:** {user.name}\n"
                        f"**Reason:** {reason or 'not unbanned from bot'}\n"
                        f"**Responsible moderator:** {moderator.mention or 'not unbanned from bot'}",
            color=self.bot.COLOR,
            timestamp=dt.datetime.utcnow()
        )
        embed.set_footer(text=f"ID: {user.id}")
        embed.set_author(icon_url=moderator.avatar.url or "", name=moderator.name or "Not banned from bot")
        await ban_channel.send(embed=embed)

    @commands.command(name="purge", description="Deletes the amount of messages specified up to 2 weeks")
    @commands.has_permissions(manage_messages=True)
    async def purge_message_command(self, ctx: commands.Context, count: int, targets: commands.Greedy[discord.User], *,
                                    reason: t.Optional[str] = "No reason"):
        def _check(msg: discord.Message):
            return not targets or msg.author in targets

        if count <= 0:
            return await ctx.send("Please enter a positive number")

        async with ctx.typing():
            deleted = await ctx.channel.purge(limit=count + 1, check=_check)
        await ctx.send(f"{len(deleted) - 1} messages were purged from the channel")

        if not (result := self.guilds.find_one(ctx.guild.id)):
            return
        if not (deleted_message_channel_id := result["data"]["log"]["deleted_message_channel"]):
            return
        deleted_message_channel = self.bot.get_channel(int(deleted_message_channel_id))

        deleted_messages = [(f"({msg.id} {msg.author.name}) {msg.author.display_name}: {msg.content} "
                             f"{' '.join([attachment.url for attachment in msg.attachments])}") for msg in deleted]
        log_message = "\n".join(deleted_messages)
        text_file = io.StringIO(log_message)
        text_file = discord.File(fp=text_file, filename=f"{ctx.channel.name}_{len(deleted)}_purged_messages.txt")
        await deleted_message_channel.send(f"{len(deleted)} messaged purged from {ctx.channel.mention}", file=text_file)

    @commands.command(name="mute", aliases=["timeout"],
                      description="Times out the mentioned users. Can accept multiple users at once")
    @commands.has_permissions(manage_roles=True)
    async def mute_member_command(self, ctx, targets: commands.Greedy[discord.User],
                                  time: t.Optional[str], *, reason: t.Optional[str] = "No reason"):
        if not len(targets):
            return await ctx.send("Please specify at least one member to mute")
        if not time:
            return await ctx.send("Please specify a maximum time")

        seconds = util.time_string_to_seconds(time)

        muted = ""
        for target in targets:
            handshake = await self.timeout_user(target, ctx.guild, seconds)
            if handshake:
                muted += f"{target.name}\n"
            else:
                await ctx.send(f"I could not mute {target.mention}")

        if len(targets) == 1:
            msg = f"1 member muted for {reason.lower()}"
        else:
            msg = f"{len(targets)} members muted for {reason.lower()}"

        embed = discord.Embed(
            title=msg,
            description=f"{ctx.author.mention} had {msg}:\n{muted}",
            color=self.bot.COLOR,
            timestamp=dt.datetime.utcnow()
        )
        embed.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}",
                         icon_url=ctx.author.avatar_url)
        embed.set_footer(text="Imagine being losers.")
        return await ctx.send(embed=embed)

    @commands.command(name="unmute",
                      description="Removes the time out from the mentioned users. Can accept multiple users at once.")
    @commands.has_permissions(manage_roles=True)
    async def unmute_member_command(self, ctx, targets: commands.Greedy[discord.User], *,
                                    reason: t.Optional[str] = "No reason"):
        if not len(targets):
            return await ctx.send("You must specify a target member!")

        unmuted = ""
        for target in targets:
            handshake = await self.timeout_user(target, ctx.guild, 0)
            if handshake:
                unmuted += f"{target.name}#{target.discriminator}\n"
            else:
                await ctx.send(f"I could not unmute {target.mention}")

        if len(targets) == 1:
            msg = f"1 member unmuted for {reason.lower()}"
        else:
            msg = f"{len(targets)} members unmuted for {reason.lower()}"

        embed = discord.Embed(
            title=msg,
            description=f"{ctx.author.mention} had {msg}:\n{unmuted}",
            color=self.bot.COLOR,
            timestamp=dt.datetime.utcnow()
        )
        embed.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}",
                         icon_url=ctx.author.avatar_url)
        embed.set_footer(text="No longer losers.")
        await ctx.send(embed=embed)

    @commands.command(name="change_prefix", aliases=["prefix"], description="Changes the server prefix of the bot")
    @commands.has_permissions(manage_guild=True)
    async def change_guild_prefix(self, ctx: commands.Context, prefix: str):
        if not (result := self.guilds.find_one(ctx.guild.id)):
            return await ctx.send("There was an issue and I could not find your server in my database!")

        self.guilds.update_one({"_id": ctx.guild.id}, {"$set": {"server_prefix": prefix}})
        await ctx.send(f"Alright! I changed the server prefix from {result['server_prefix']} to {prefix}!")


async def setup(bot):
    await bot.add_cog(Mod(bot))
