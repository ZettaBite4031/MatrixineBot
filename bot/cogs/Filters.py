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
                                  timestamp=dt.datetime.now())
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
            embed.set_footer(text=f"API: some-random-api.com/canvas/{overlay}")
            embed.set_image(url=url)
            await ctx.send(embed=embed)

    @overlay_group.command(name="gay", description="Adds a gay filter")
    async def gay_overlay(self, ctx: commands.Context, target: t.Optional[discord.User]):
        if target is None:
            target = ctx.author
        url = f"https://some-random-api.com/canvas/gay?avatar={target.avatar.replace(format='png', size=1024)}"
        embed = discord.Embed(title=target.display_name,
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.now())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f"API: some-random-api.com/canvas/gay")
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @overlay_group.command(name="glass", description="Adds a glass filter")
    async def glass_overlay(self, ctx: commands.Context, target: t.Optional[discord.User]):
        if target is None:
            target = ctx.author
        url = f"https://some-random-api.com/canvas/glass?avatar={target.avatar.replace(format='png', size=1024)}"
        embed = discord.Embed(title=target.display_name,
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.now())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f"API: some-random-api.com/canvas/glas")
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @overlay_group.command(name="wasted", description="Adds a GTA wasted filter")
    async def wasted_overlay(self, ctx: commands.Context, target: t.Optional[discord.User]):
        if target is None:
            target = ctx.author
        url = f"https://some-random-api.com/canvas/wasted?avatar={target.avatar.replace(format='png', size=1024)}"
        embed = discord.Embed(title=target.display_name,
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.now())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f"API: some-random-api.com/canvas/wasted")
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @overlay_group.command(name="passed", description="Adds a GTA mission passed filter")
    async def passed_overlay(self, ctx: commands.Context, target: t.Optional[discord.User]):
        if target is None:
            target = ctx.author
        url = f"https://some-random-api.com/canvas/passed?avatar={target.avatar.replace(format='png', size=1024)}"
        embed = discord.Embed(title=target.display_name,
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.now())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f"API: some-random-api.com/canvas/passed")
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @overlay_group.command(name="jail", description="Adds a jail filter")
    async def jail_overlay(self, ctx: commands.Context, target: t.Optional[discord.User]):
        if target is None:
            target = ctx.author
        url = f"https://some-random-api.com/canvas/jail?avatar={target.avatar.replace(format='png', size=1024)}"
        embed = discord.Embed(title=target.display_name,
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.now())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f"API: some-random-api.com/canvas/jail")
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @overlay_group.command(name="comrade", description="Adds a soviet flag filter")
    async def comrade_overlay(self, ctx: commands.Context, target: t.Optional[discord.User]):
        if target is None:
            target = ctx.author
        url = f"https://some-random-api.com/canvas/comrade?avatar={target.avatar.replace(format='png', size=1024)}"
        embed = discord.Embed(title=target.display_name,
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.now())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f"API: some-random-api.com/canvas/comrade")
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @overlay_group.command(name="triggered", description="Adds a triggered filter")
    async def triggered_overlay(self, ctx: commands.Context, target: t.Optional[discord.User]):
        if target is None:
            target = ctx.author
        url = f"https://some-random-api.com/canvas/triggered?avatar={target.avatar.replace(format='png', size=1024)}"
        embed = discord.Embed(title=target.display_name,
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.now())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f"API: some-random-api.com/canvas/triggered")
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @overlay_group.command(name="filter", description="Adds a random filter")
    async def filter_overlay(self, ctx: commands.Context, target: t.Optional[discord.User]):
        if target is None:
            target = ctx.author
        choices = ["greyscale", "invert", "invertgreyscale", "sepia", "red", "green", "blue", "blurple", "blurple2"]
        filter = r.choice(choices)
        url = f"https://some-random-api.com/canvas/{filter}?avatar={target.avatar.replace(format='png', size=1024)}"
        embed = discord.Embed(title=f"{target.display_name} {filter.capitalize()}",
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.now())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f"API: some-random-api.com/canvas/{filter}")
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @overlay_group.command(name="greyscale", description="Adds a greyscale filter")
    async def greyscale_overlay(self, ctx: commands.Context, target: t.Optional[discord.User]):
        if target is None:
            target = ctx.author
        url = f"https://some-random-api.com/canvas/greyscale?avatar={target.avatar.replace(format='png', size=1024)}"
        embed = discord.Embed(title=target.display_name,
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.now())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f"API: some-random-api.com/canvas/greyscale")
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @overlay_group.command(name="invert", description="Inverts the colors")
    async def invert_overlay(self, ctx: commands.Context, target: t.Optional[discord.User]):
        if target is None:
            target = ctx.author
        url = f"https://some-random-api.com/canvas/invert?avatar={target.avatar.replace(format='png', size=1024)}"
        embed = discord.Embed(title=target.display_name,
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.now())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f"API: some-random-api.com/canvas/invert")
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @overlay_group.command(name="invertgreyscale", description="Inverts the colors and adds a greyscale filter")
    async def invertgreyscale_overlay(self, ctx: commands.Context, target: t.Optional[discord.User]):
        if target is None:
            target = ctx.author
        url = f"https://some-random-api.com/canvas/invertgreyscale?avatar={target.avatar.replace(format='png', size=1024)}"
        embed = discord.Embed(title=target.display_name,
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.now())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f"API: some-random-api.com/canvas/invertgreyscale")
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @overlay_group.command(name="sepia", description="Adds a sepia filter")
    async def sepia_overlay(self, ctx: commands.Context, target: t.Optional[discord.User]):
        if target is None:
            target = ctx.author
        url = f"https://some-random-api.com/canvas/sepia?avatar={target.avatar.replace(format='png', size=1024)}"
        embed = discord.Embed(title=target.display_name,
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.now())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f"API: some-random-api.com/canvas/sepia")
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @overlay_group.command(name="red", description="Adds a red filter")
    async def red_overlay(self, ctx: commands.Context, target: t.Optional[discord.User]):
        if target is None:
            target = ctx.author
        url = f"https://some-random-api.com/canvas/red?avatar={target.avatar.replace(format='png', size=1024)}"
        embed = discord.Embed(title=target.display_name,
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.now())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f"API: some-random-api.com/canvas/red")
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @overlay_group.command(name="green", description="Adds a green filter")
    async def green_overlay(self, ctx: commands.Context, target: t.Optional[discord.User]):
        if target is None:
            target = ctx.author
        url = f"https://some-random-api.com/canvas/green?avatar={target.avatar.replace(format='png', size=1024)}"
        embed = discord.Embed(title=target.display_name,
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.now())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f"API: some-random-api.com/canvas/green")
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @overlay_group.command(name="blue", description="Adds a blue filter")
    async def blue_overlay(self, ctx: commands.Context, target: t.Optional[discord.User]):
        if target is None:
            target = ctx.author
        url = f"https://some-random-api.com/canvas/blue?avatar={target.avatar.replace(format='png', size=1024)}"
        embed = discord.Embed(title=target.display_name,
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.now())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f"API: some-random-api.com/canvas/blue")
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @overlay_group.command(name="blurple", description="Adds a blurple filter")
    async def blurple_overlay(self, ctx: commands.Context, target: t.Optional[discord.User]):
        if target is None:
            target = ctx.author
        url = f"https://some-random-api.com/canvas/blurple?avatar={target.avatar.replace(format='png', size=1024)}"
        embed = discord.Embed(title=target.display_name,
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.now())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f"API: some-random-api.com/canvas/blurple")
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @overlay_group.command(name="blurple2", description="Adds a different blurple filter")
    async def blurple2_overlay(self, ctx: commands.Context, target: t.Optional[discord.User]):
        if target is None:
            target = ctx.author
        url = f"https://some-random-api.com/canvas/blurple2?avatar={target.avatar.replace(format='png', size=1024)}"
        embed = discord.Embed(title=target.display_name,
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.now())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f"API: some-random-api.com/canvas/blurple2")
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @overlay_group.command(name="brightness", description="Brightens your avatar")
    async def brightness_overlay(self, ctx, brightness: t.Optional[float], target: t.Optional[discord.Member]):
        target = target or ctx.author
        url = ("https://some-random-api.com/canvas/filter/brightness?avatar="
               f"{target.avatar.replace(format='png', size=1024)}")
        if brightness:
            url += f"&brightness={brightness}"

        embed = discord.Embed(title=target.display_name,
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.now())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f"API: some-random-api.com/canvas/filter/brightness")
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @overlay_group.command(name="tint", description="Adds a specified tint")
    async def tint_overylay(self, ctx, tint: str, target: t.Optional[discord.Member]):
        target = target or ctx.author
        try:
            tint = hex(int(tint.strip("0x"), 16))
        except ValueError:
            return await ctx.send("Please supply valid hexadecimal! (0xFFFFFF)")

        url = (f"https://some-random-api.com/canvas/color?color={str(tint)}&avatar="
               f"{target.avatar.replace(format='png', size=1024)}").replace("0x", "")
        embed = discord.Embed(title=target.display_name,
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.now())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f"API: some-random-api.com/canvas/color")
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @overlay_group.command(name="threshold", description="Thresholds your avatar")
    async def brightness_overlay(self, ctx, threshold: t.Optional[float], target: t.Optional[discord.Member]):
        target = target or ctx.author
        url = ("https://some-random-api.com/canvas/filter/threshold?avatar="
               f"{target.avatar.replace(format='png', size=1024)}")
        if threshold:
            url += f"&threshold={threshold}"

        embed = discord.Embed(title=target.display_name,
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.now())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f"API: some-random-api.com/canvas/filter/threshold")
        embed.set_image(url=url)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Filters(bot))
