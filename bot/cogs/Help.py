import typing as t
import datetime as dt

import discord
from discord.ext.menus import MenuPages, ListPageSource
from discord.ext import commands

DENY_COGS = ["WebsiteUpkeep"]

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
        prefix = self.bot.MONGO_DB["Guilds"].find_one(ctx.guild.id)["server_prefix"]

        # Module not supplied
        if not module:
            embed = discord.Embed(
                title="Welcome to the Matrixine Help Menu!",
                description=f"Use `{prefix}help module` to gain more information about that module!"
                            f"\nThe prefix is case insensitive.",
                colour=self.bot.COLOR,
                timestamp=dt.datetime.now()
            )
            embed.set_thumbnail(url=self.bot.user.avatar.url)
            embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar.url)
            embed.add_field(name="About", value=f"*{self.bot.BOT_INFO.name}* is developed in Discord.py v2.3.2 "
                                                f"by `{self.bot.OWNER_USERNAME}`\n*{self.bot.BOT_INFO.name}* "
                                                f"is running on {self.bot.VERSION}",
                            inline=False)
            value = []
            for cog in self.bot.cogs:
                if cog in DENY_COGS:
                    continue
                value.append(
                    f"`{cog}`: {self.bot.cogs[cog].__doc__ or 'No description'}")
                msg = "\n".join(value)
            embed.add_field(name="Modules", value=msg, inline=False)
            return await ctx.send(embed=embed)

        # Module supplied
        cog = module.capitalize()
        if cog in self.bot.cogs and cog not in DENY_COGS:
            if not command:
                if self.bot.get_cog(cog).get_commands():
                    menu = MenuPages(source=HelpMenu(ctx, list(self.bot.get_cog(cog).get_commands()), cog, self.bot),
                                     delete_message_after=True,
                                     timeout=60.0)
                    return await menu.start(ctx)

                elif not self.bot.get_cog(cog).get_commands():
                    embed = discord.Embed(
                        title=f"Help {cog}!",
                        description=f"{self.bot.cogs[cog].__doc__ if self.bot.cogs[cog].__doc__ else 'No description.'}\n",
                        colour=self.bot.COLOR,
                        timestamp=dt.datetime.now()
                    )
                    embed.set_thumbnail(url=self.bot.user.avatar.url)
                    embed.set_footer(text=f"Requested by {ctx.author.display_name}")
                    embed.add_field(name="This module has no commands.",
                                    value="This module is purely functional and contains no commands.", inline=False)
                    return await ctx.send(embed=embed)

                else:
                    return await ctx.send("That module doesn't have any commands")

            if not (cmd := self.get_subcommand(command)):
                return await ctx.send("I couldn't find that command!")
            if isinstance(cmd, commands.Group):
                menu = MenuPages(source=HelpMenu(ctx, list(cmd.commands), cmd, self.bot),
                                 delete_message_after=True,
                                 timeout=60.0)
                return await menu.start(ctx)
            return await self.cmd_help(ctx, cmd)

        elif cog not in self.bot.cogs:
            await ctx.send("That module does not exist.")

    def get_subcommand(self, command):
        parts = command.split(" ")
        found_command = self.bot
        for part in parts:
            if isinstance(found_command, commands.Bot):
                found_command = found_command.get_command(part)
            elif isinstance(found_command, commands.Group):
                found_command = found_command.get_command(part)
            if not found_command:
                return None

        return found_command


async def setup(bot):
    await bot.add_cog(Help(bot))
