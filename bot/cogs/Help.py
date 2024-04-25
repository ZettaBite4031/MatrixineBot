import typing as t
import datetime as dt

import discord
from discord.ext.menus import MenuPages, ListPageSource
from discord.ext import commands


def syntax(command):
    cmd_and_aliases = "|".join([str(command), *command.aliases])
    params = []

    for k, v in command.params.items():
        if k not in ("self", "ctx"):
            params.append(f"[{k}]" if "NoneType" in str(v) else f"<{k}>")

    params = " ".join(params)
    return f'`{cmd_and_aliases}{f" {params}" if params != "" else ""}`'


class HelpMenu(ListPageSource):
    def __init__(self, ctx, data, cog, bot):
        self.ctx = ctx
        self.bot = bot
        self.cog = cog
        super().__init__(data, per_page=3)

    async def write_page(self, menu, fields=[]):
        offset = (menu.current_page * self.per_page) + 1
        len_data = len(self.entries)

        embed = discord.Embed(title=f"Help {self.cog}",
                              description=f"Welcome to the Matrixine help menu!\nPrefix is {self.bot.PREFIX}",
                              color=self.bot.COLOR)
        embed.set_thumbnail(url=self.ctx.guild.me.avatar.url)
        embed.set_footer(text=f"{offset:,} - {min(len_data, offset + self.per_page - 1):,} of {len_data:,} commands.")

        for v, n in fields:
            embed.add_field(name=n, value=f"**{v}**", inline=False)

        return embed

    async def format_page(self, menu, entries):
        fields = []
        for e in entries:
            fields.append((e.description or "No description", syntax(e)))
        return await self.write_page(menu, fields)


class Help(commands.Cog):
    """Specifically just for the help command. Only holds the help command"""
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command("help")

    async def cmd_help(self, ctx, command):
        embed = discord.Embed(title=f"Help with `{command}`",
                              description=syntax(command),
                              color=self.bot.COLOR)
        embed.add_field(name="Command description",
                        value=command.description if command.description else "No description",
                        inline=False)
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="help", aliases=["h"], description="Shows this message")
    async def show_help(self, ctx, module: t.Optional[str], *, command: t.Optional[str]):
        prefix = "M!"

        # Module not supplied
        if not module:
            embed = discord.Embed(
                title="Welcome to the Matrixine Help Menu!",
                description=f"Use `{prefix}help module` to gain more information about that module!"
                            f"\nThe prefix is case insensitive.",
                colour=self.bot.COLOR,
                timestamp=dt.datetime.utcnow()
            )
            embed.set_thumbnail(url=self.bot.user.avatar.url)
            embed.set_footer(text=f"Requested by {ctx.author.display_name}")
            embed.add_field(name="About", value=f"*Matrixine* is developed in Discord.py v1.7.3 by {self.bot.OWNER_USERNAME}\n\
                                                            *{self.bot.BOT_INFO.name}* is running on {self.bot.VERSION}",
                            inline=False)
            value = []
            for cog in self.bot.cogs:
                value.append(
                    f"`{cog}`: {self.bot.cogs[cog].__doc__ if self.bot.cogs[cog].__doc__ else 'No description'}")
                msg = "\n".join(value)
            embed.add_field(name="Modules", value=msg, inline=False)
            return await ctx.send(embed=embed)

        # Module supplied
        cog = module.capitalize()
        if cog in self.bot.cogs:
            if not command:
                if self.bot.get_cog(cog).get_commands():
                    menu = MenuPages(source=HelpMenu(ctx, list(self.bot.get_cog(cog).get_commands()), cog, self.bot),
                                     delete_message_after=True,
                                     timeout=60.0)
                    await menu.start(ctx)

                elif not self.bot.get_cog(cog).get_commands():
                    embed = discord.Embed(
                        title=f"Help {cog}!",
                        description=f"{self.bot.cogs[cog].__doc__ if self.bot.cogs[cog].__doc__ else 'No description.'}\n",
                        colour=self.bot.COLOR,
                        timestamp=dt.datetime.utcnow()
                    )
                    embed.set_thumbnail(url=self.bot.user.avatar.url)
                    embed.set_footer(text=f"Requested by {ctx.author.display_name}")
                    embed.add_field(name="This module has no commands.",
                                    value="This module is purely functional and contains no commands.", inline=False)
                    await ctx.send(embed=embed)

                else:
                    await ctx.send("That module doesn't have any commands")

            else:
                if cmd := discord.utils.get(self.bot.commands, name=command):
                    if isinstance(cmd, commands.Group):
                        menu = MenuPages(source=HelpMenu(ctx, list(cmd.commands), cmd, self.bot),
                                         delete_message_after=True,
                                         timeout=60.0)
                        await menu.start(ctx)
                    else:
                        await self.cmd_help(ctx, cmd)
                else:
                    if " " in command:
                        group = command.split(" ")[0]
                        subcommand = command.split(" ")[1]
                        for cmd in self.bot.commands:
                            if group in cmd.aliases or group in cmd.name:
                                if not hasattr(cmd, "commands"):
                                    return await ctx.send(f"{group} doesn't have any subcommands!")
                                for subcmd in cmd.commands:
                                    if subcmd.name == subcommand:
                                        return await self.cmd_help(ctx, subcmd)
                                return await ctx.send(f"{group} doesn't have any subcommands named {subcommand}")
                    else:
                        for cmd in self.bot.commands:
                            if command in cmd.aliases or command in cmd.name:
                                return await self.cmd_help(ctx, cmd)
                    await ctx.send("That command does not exist")

        elif cog not in self.bot.cogs:
            await ctx.send("That module does not exist.")


async def setup(bot):
    await bot.add_cog(Help(bot))
