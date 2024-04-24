import random as r
import datetime as dt
import typing as t

import discord
from discord.ext import commands


class Filters(commands.Cog):
    """Filter commands for a user's pfp."""
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="overlay",
                      description="Adds overlays onto the specified user's avatar; "
                                  "if none is provided, it will use the user's profile.")
    async def overlay_group(self, ctx, target: t.Optional[discord.User]):
        if target is None:
            target = ctx.author
        if not ctx.invoked_subcommand:
            overlays = ["gay", "glass", "wasted", "passed", "jail", "comrade", "triggered"]
            overlay = r.choice(overlays)
            url = f"https://some-random-api.com/canvas/{overlay}?avatar={target.avatar.replace(format='png', size=1024)}"
            embed = discord.Embed(title=target.display_name,
                                  color=self.bot.COLOR,
                                  timestamp=dt.datetime.utcnow())
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
            embed.set_footer(text=f"API: some-random-api.com/canvas/{overlay}")
            embed.set_image(url=url)
            await ctx.send(embed=embed)

    @overlay_group.command(name="gay")
    async def gay_overlay(self, ctx: commands.Context, target: t.Optional[discord.User]):
        if target is None:
            target = ctx.author
        url = f"https://some-random-api.com/canvas/gay?avatar={target.avatar.replace(format='png', size=1024)}"
        embed = discord.Embed(title=target.display_name,
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.utcnow())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f"API: some-random-api.com/canvas/gay")
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @overlay_group.command(name="glass")
    async def glass_overlay(self, ctx: commands.Context, target: t.Optional[discord.User]):
        if target is None:
            target = ctx.author
        url = f"https://some-random-api.com/canvas/glass?avatar={target.avatar.replace(format='png', size=1024)}"
        embed = discord.Embed(title=target.display_name,
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.utcnow())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f"API: some-random-api.com/canvas/glas")
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @overlay_group.command(name="wasted")
    async def wasted_overlay(self, ctx: commands.Context, target: t.Optional[discord.User]):
        if target is None:
            target = ctx.author
        url = f"https://some-random-api.com/canvas/wasted?avatar={target.avatar.replace(format='png', size=1024)}"
        embed = discord.Embed(title=target.display_name,
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.utcnow())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f"API: some-random-api.com/canvas/wasted")
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @overlay_group.command(name="passed")
    async def passed_overlay(self, ctx: commands.Context, target: t.Optional[discord.User]):
        if target is None:
            target = ctx.author
        url = f"https://some-random-api.com/canvas/passed?avatar={target.avatar.replace(format='png', size=1024)}"
        embed = discord.Embed(title=target.display_name,
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.utcnow())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f"API: some-random-api.com/canvas/passed")
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @overlay_group.command(name="jail")
    async def jail_overlay(self, ctx: commands.Context, target: t.Optional[discord.User]):
        if target is None:
            target = ctx.author
        url = f"https://some-random-api.com/canvas/jail?avatar={target.avatar.replace(format='png', size=1024)}"
        embed = discord.Embed(title=target.display_name,
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.utcnow())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f"API: some-random-api.com/canvas/jail")
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @overlay_group.command(name="comrade")
    async def comrade_overlay(self, ctx: commands.Context, target: t.Optional[discord.User]):
        if target is None:
            target = ctx.author
        url = f"https://some-random-api.com/canvas/comrade?avatar={target.avatar.replace(format='png', size=1024)}"
        embed = discord.Embed(title=target.display_name,
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.utcnow())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f"API: some-random-api.com/canvas/comrade")
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @overlay_group.command(name="triggered")
    async def triggered_overlay(self, ctx: commands.Context, target: t.Optional[discord.User]):
        if target is None:
            target = ctx.author
        url = f"https://some-random-api.com/canvas/triggered?avatar={target.avatar.replace(format='png', size=1024)}"
        embed = discord.Embed(title=target.display_name,
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.utcnow())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f"API: some-random-api.com/canvas/triggered")
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @overlay_group.command(name="filter")
    async def filter_overlay(self, ctx: commands.Context, target: t.Optional[discord.User]):
        if target is None:
            target = ctx.author
        choices = ["greyscale", "invert", "invertgreyscale", "sepia", "red", "green", "blue", "blurple", "blurple2"]
        filter = r.choice(choices)
        url = f"https://some-random-api.com/canvas/{filter}?avatar={target.avatar.replace(format='png', size=1024)}"
        embed = discord.Embed(title=f"{target.display_name} {filter.capitalize()}",
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.utcnow())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f"API: some-random-api.com/canvas/{filter}")
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @overlay_group.command(name="greyscale")
    async def greyscale_overlay(self, ctx: commands.Context, target: t.Optional[discord.User]):
        if target is None:
            target = ctx.author
        url = f"https://some-random-api.com/canvas/greyscale?avatar={target.avatar.replace(format='png', size=1024)}"
        embed = discord.Embed(title=target.display_name,
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.utcnow())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f"API: some-random-api.com/canvas/greyscale")
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @overlay_group.command(name="invert")
    async def invert_overlay(self, ctx: commands.Context, target: t.Optional[discord.User]):
        if target is None:
            target = ctx.author
        url = f"https://some-random-api.com/canvas/invert?avatar={target.avatar.replace(format='png', size=1024)}"
        embed = discord.Embed(title=target.display_name,
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.utcnow())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f"API: some-random-api.com/canvas/invert")
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @overlay_group.command(name="invertgreyscale")
    async def invertgreyscale_overlay(self, ctx: commands.Context, target: t.Optional[discord.User]):
        if target is None:
            target = ctx.author
        url = f"https://some-random-api.com/canvas/invertgreyscale?avatar={target.avatar.replace(format='png', size=1024)}"
        embed = discord.Embed(title=target.display_name,
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.utcnow())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f"API: some-random-api.com/canvas/invertgreyscale")
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @overlay_group.command(name="sepia")
    async def sepia_overlay(self, ctx: commands.Context, target: t.Optional[discord.User]):
        if target is None:
            target = ctx.author
        url = f"https://some-random-api.com/canvas/sepia?avatar={target.avatar.replace(format='png', size=1024)}"
        embed = discord.Embed(title=target.display_name,
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.utcnow())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f"API: some-random-api.com/canvas/sepia")
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @overlay_group.command(name="red")
    async def red_overlay(self, ctx: commands.Context, target: t.Optional[discord.User]):
        if target is None:
            target = ctx.author
        url = f"https://some-random-api.com/canvas/red?avatar={target.avatar.replace(format='png', size=1024)}"
        embed = discord.Embed(title=target.display_name,
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.utcnow())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f"API: some-random-api.com/canvas/red")
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @overlay_group.command(name="green")
    async def green_overlay(self, ctx: commands.Context, target: t.Optional[discord.User]):
        if target is None:
            target = ctx.author
        url = f"https://some-random-api.com/canvas/green?avatar={target.avatar.replace(format='png', size=1024)}"
        embed = discord.Embed(title=target.display_name,
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.utcnow())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f"API: some-random-api.com/canvas/green")
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @overlay_group.command(name="blue")
    async def blue_overlay(self, ctx: commands.Context, target: t.Optional[discord.User]):
        if target is None:
            target = ctx.author
        url = f"https://some-random-api.com/canvas/blue?avatar={target.avatar.replace(format='png', size=1024)}"
        embed = discord.Embed(title=target.display_name,
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.utcnow())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f"API: some-random-api.com/canvas/blue")
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @overlay_group.command(name="blurple")
    async def blurple_overlay(self, ctx: commands.Context, target: t.Optional[discord.User]):
        if target is None:
            target = ctx.author
        url = f"https://some-random-api.com/canvas/blurple?avatar={target.avatar.replace(format='png', size=1024)}"
        embed = discord.Embed(title=target.display_name,
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.utcnow())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f"API: some-random-api.com/canvas/blurple")
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @overlay_group.command(name="blurple2")
    async def blurple2_overlay(self, ctx: commands.Context, target: t.Optional[discord.User]):
        if target is None:
            target = ctx.author
        url = f"https://some-random-api.com/canvas/blurple2?avatar={target.avatar.replace(format='png', size=1024)}"
        embed = discord.Embed(title=target.display_name,
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.utcnow())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f"API: some-random-api.com/canvas/blurple2")
        embed.set_image(url=url)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Filters(bot))
