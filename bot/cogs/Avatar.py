import io
import typing as t
import random as r
import datetime as dt

import discord
import requests
from PIL import Image
from discord.ext import commands
from pixelsort import pixelsort as pxs


class Avatar(commands.Cog):
    """Some interesting commands to mess around with a user's profile picture!"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="glitch", description="Messes with the user's pfp to add a glitchy look")
    async def glitch_avatar_command(self, ctx: commands.Context, target: t.Optional[discord.User]):
        if target is None:
            target = ctx.author

        async with ctx.typing():
            re = requests.get(f"{target.avatar.url}".replace("webp", "png").replace("gif", "png"))
            img = Image.open(io.BytesIO(re.content))
            glitch = pxs(img, lower_threshold=0.1, upper_threshold=0.85, sorting_function="saturation", randomness=1)
            img_bin = io.BytesIO()
            glitch.save(img_bin, "PNG")
            img_bin.seek(0)
            await ctx.send(
                "Here is your a̶̩͇͛̎̽̉̉̚v̷̞͖̣͊̇̆͆͘ą̴̪͈͚̓̊̎͌̽͆̀͒̎̽͒̉̕͘͜ţ̸̲̗͇̯̼̱̱͊͗̋͆̋͐͘a̶̓͗̅͒͑̈́̾͜͝r̸̬̪̬͊̀",
                file=discord.File(fp=img_bin, filename="image.txt"))

    @commands.command(name="sort", description="Sorts the user's pfp.\nThere are 5 sort choices: Lightness, Hue, "
                                               "Intensity, Minimum, and Saturation.\nThresholds describe the bounds of "
                                               "the sort, and are limited to 0 through 1.\nThe angle determines at what"
                                               " angle the sort starts.\nThe randomness controls how accurate the "
                                               "sort is.")
    async def pixel_sort_command(self, ctx: commands.Context, sort: t.Optional[str],
                                 low_threshold: t.Optional[float], up_threshold: t.Optional[float],
                                 angle: t.Optional[float], randomness: t.Optional[float],
                                 target: t.Optional[discord.User]):
        if target is None:
            target = ctx.author

        if not low_threshold:
            low_threshold = 0
        if not up_threshold:
            up_threshold = 1
        if not angle:
            angle = 0
        if not randomness:
            randomness = 0

        if 0 > up_threshold or up_threshold > 1:
            return await ctx.send("The upper threshold must be within 0 and 1!")
        if 0 > low_threshold or low_threshold > 1:
            return await ctx.send("The lower threshold must be within 0 and 1!")

        from pixelsort.sorting import choices
        choices = list(choices.keys())
        if sort is None:
            sort = r.choice(choices)
        elif sort.lower() not in choices:
            return await ctx.send("You have to choose one of the viable sorts! " + ", ".join(choices).capitalize())

        sort = sort.lower()
        async with ctx.typing():
            re = requests.get(f"{target.avatar.url}".replace("webp", "png").replace("gif", "png"))
            img = Image.open(io.BytesIO(re.content))
            sortedImg = pxs(img, lower_threshold=low_threshold if low_threshold is not None else 0.0,
                            upper_threshold=up_threshold if up_threshold is not None else 1.0,
                            sorting_function=sort, angle=abs(angle), randomness=abs(randomness))

            img_bin = io.BytesIO()
            sortedImg.save(img_bin, "PNG")
            img_bin.seek(0)
            await ctx.send("Here is your sorted profile!",
                           file=discord.File(fp=img_bin, filename="image.txt"))

    @commands.command(name="blur", description="Blurs the user's profile picture.")
    async def blur_avatar_command(self, ctx: commands.Context, target: t.Optional[discord.Member]):
        if target is None:
            target = ctx.author

        embed = discord.Embed(title="Blur!",
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.utcnow())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text="API: some-random-api.com/canvas/misc/blur")
        embed.set_image(url="https://some-random-api.com/canvas/misc/blur/?avatar="
                            f"{target.avatar.replace(format='png', size=1024)}")
        await ctx.send(embed=embed)

    @commands.command(name="pixelate", description="Pixelates the user's profile picture.")
    async def pixelate_command(self, ctx, target: t.Optional[discord.Member]):
        if not target:
            target = ctx.author

        embed = discord.Embed(title="Pixelate!",
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.utcnow())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_image(
            url="https://some-random-api.com/canvas/misc/pixelate?avatar="
                f"{target.avatar.replace(format='png', size=1024)}")
        await ctx.send(embed=embed)

    @commands.command(name="simp", aliases=["simpcard"], description="Calls the mentioned a user a simp.")
    async def simpcard_avatar_command(self, ctx: commands.Context, target: t.Optional[discord.User]):
        if target is None:
            target = ctx.author

        embed = discord.Embed(title="SIMP!",
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.utcnow())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text="API: some-random-api.com/canvas/misc/simpcard")
        embed.set_image(url=f"https://some-random-api.com/canvas/misc/simpcard?avatar={target.avatar.url}")
        await ctx.send(embed=embed)

    @commands.command(name="horny", description="Proves the mentioned user is a horny bastard.")
    async def horny_avatar_command(self, ctx: commands.Context, target: t.Optional[discord.User]):
        if target is None:
            target = ctx.author

        embed = discord.Embed(title="Horny.",
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.utcnow())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text="API: some-random-api.com/canvas/misc/horny")
        embed.set_image(url=f"https://some-random-api.com/canvas/misc/horny?avatar={target.avatar.url}")
        await ctx.send(embed=embed)

    @commands.command(name="Lolice", description="Call the loli police on a user.")
    async def lolice_avatar_command(self, ctx: commands.Context, target: t.Optional[discord.User]):
        if target is None:
            target = ctx.author

        embed = discord.Embed(title="Lolice!",
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.utcnow())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text="API: some-random-api.com/canvas/misc/lolice")
        embed.set_image(url=f"https://some-random-api.com/canvas/misc/lolice?avatar={target.avatar.url}")
        await ctx.send(embed=embed)

    @commands.command(name="gay-bg", description="Adds a gay border to a user's profile picture.")
    async def pixelate_avatar_command(self, ctx: commands.Context, target: t.Optional[discord.User]):
        if target is None:
            target = ctx.author

        embed = discord.Embed(title="G A Y!",
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.utcnow())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text="API: some-random-api.com/canvas/misc/lgbt")
        embed.set_image(url=f"https://some-random-api.com/canvas/misc/lgbt?avatar={target.avatar.url}")
        await ctx.send(embed=embed)

    @commands.command(name="pansexual-bg", description="Adds a pansexual border to a user's profile picture.")
    async def pan_the_avatar_command(self, ctx: commands.Context, target: t.Optional[discord.User]):
        if target is None:
            target = ctx.author

        embed = discord.Embed(title="Pan 🍳",
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.utcnow())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text="API: some-random-api.com/canvas/misc/pansexual")
        embed.set_image(url=f"https://some-random-api.com/canvas/misc/pansexual?avatar={target.avatar.url}")
        await ctx.send(embed=embed)

    @commands.command(name="nonbinary-bg", description="Adds a nonbinary border to a user's profile picture.")
    async def nonbinary_avatar_command(self, ctx: commands.Context, target: t.Optional[discord.User]):
        if target is None:
            target = ctx.author

        embed = discord.Embed(title="Nonbinary",
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.utcnow())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text="API: some-random-api.com/canvas/misc/nonbinary")
        embed.set_image(url=f"https://some-random-api.com/canvas/misc/nonbinary?avatar={target.avatar.url}")
        await ctx.send(embed=embed)

    @commands.command(name="lesbian-bg", description="Adds a lesbian border to a user's profile picture.")
    async def lesbian_avatar_command(self, ctx: commands.Context, target: t.Optional[discord.User]):
        if target is None:
            target = ctx.author

        embed = discord.Embed(title="Lesbian",
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.utcnow())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text="API: some-random-api.com/canvas/misc/lesbian")
        embed.set_image(
            url=f"https://some-random-api.com/canvas/misc/lesbian?avatar={target.avatar.url}")
        await ctx.send(embed=embed)

    @commands.command(name="bisexual-bg", description="Adds a bisexual border to a user's profile picutre.")
    async def bisexual_avatar_command(self, ctx: commands.Context, target: t.Optional[discord.User]):
        if target is None:
            target = ctx.author

        embed = discord.Embed(title="Bisexual",
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.utcnow())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text="API: some-random-api.com/canvas/misc/bisexual")
        embed.set_image(url=f"https://some-random-api.com/canvas/misc/bisexual?avatar={target.avatar.url}")
        await ctx.send(embed=embed)

    @commands.command(name="trans-bg", description="Adds a trans border to a user's profile picture.")
    async def transgender_avatar_command(self, ctx: commands.Context, target: t.Optional[discord.User]):
        if target is None:
            target = ctx.author

        embed = discord.Embed(title="Transgender",
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.utcnow())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text="API: some-random-api.com/canvas/misc/transgender")
        embed.set_image(url=f"https://some-random-api.com/canvas/misc/transgender?avatar={target.avatar.url}")
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Avatar(bot))
