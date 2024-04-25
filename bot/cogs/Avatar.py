import io
import typing as t
import random as r
import datetime as dt
from urllib.parse import quote

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
            glitch = pxs(img, lower_threshold=0.1, upper_threshold=0.85, sorting_function="saturation", randomness=10)
            img_bin = io.BytesIO()
            glitch.save(img_bin, "PNG")
            img_bin.seek(0)
            await ctx.send(
                "Here is your a̶̩͇͛̎̽̉̉̚v̷̞͖̣͊̇̆͆͘ą̴̪͈͚̓̊̎͌̽͆̀͒̎̽͒̉̕͘͜ţ̸̲̗͇̯̼̱̱͊͗̋͆̋͐͘a̶̓͗̅͒͑̈́̾͜͝r̸̬̪̬͊̀",
                file=discord.File(fp=img_bin, filename="image.png"))

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

    @commands.group(name="avatar")
    async def avatar_command_group(self, ctx, target: t.Optional[discord.Member]):
        pass

    @avatar_command_group.command(name="blur", description="Blurs the user's profile picture.")
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

    @avatar_command_group.command(name="pixelate", description="Pixelates the user's profile picture.")
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

    @avatar_command_group.command(name="simp", aliases=["simpcard"], description="Calls the mentioned a user a simp.")
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

    @avatar_command_group.command(name="horny", description="Proves the mentioned user is a horny bastard.")
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

    @avatar_command_group.command(name="Lolice", description="Call the loli police on a user.")
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

    @avatar_command_group.command(name="gay-bg", description="Adds a gay border to a user's profile picture.")
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

    @avatar_command_group.command(name="pansexual-bg", description="Adds a pansexual border to a user's profile picture.")
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

    @avatar_command_group.command(name="nonbinary-bg", description="Adds a nonbinary border to a user's profile picture.")
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

    @avatar_command_group.command(name="lesbian-bg", description="Adds a lesbian border to a user's profile picture.")
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

    @avatar_command_group.command(name="bisexual-bg", description="Adds a bisexual border to a user's profile picutre.")
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

    @avatar_command_group.command(name="trans-bg", description="Adds a trans border to a user's profile picture.")
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

    @avatar_command_group.command(name="circle", description="Crops the avatar to a circle")
    async def crop_circle_avatar_command(self, ctx, target: t.Optional[discord.User]):
        target = target or ctx.author
        embed = discord.Embed(title="Snip! Cropped to a circle!",
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.utcnow())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text="API: some-random-api.com/canvas/misc/circle")
        embed.set_image(url=f"https://some-random-api.com/canvas/misc/circle?avatar={target.avatar.url}")
        await ctx.send(embed=embed)

    @avatar_command_group.command(name="stupid", description="Someone's kinda stupid..")
    async def its_so_stupid_avatar_command(self, ctx, target: t.Optional[discord.Member]):
        target = target or ctx.author
        embed = discord.Embed(title="It's so stupid!",
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.utcnow())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text="API: some-random-api.com/canvas/misc/its-so-stupid")
        embed.set_image(url=f"https://some-random-api.com/canvas/misc/its-so-stupid?avatar={target.avatar.url}")
        await ctx.send(embed=embed)

    # @avatar_command_group.command(name="liar", description="Liar")
    async def its_so_stupid_avatar_command(self, ctx, target: t.Optional[discord.Member]):
        target = target or ctx.author
        embed = discord.Embed(title="Liar!",
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.utcnow())
        url = (f"https://some-random-api.com/canvas/misc/lied?avatar={target.avatar.url}"
               f"&username={target.name}").replace(" ", "-")
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text="API: some-random-api.com/canvas/misc/lied")
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @avatar_command_group.command(name="genshin", description="Target is a genshin player")
    async def genshin_namecard_avatar_command(self, ctx, target: t.Optional[discord.Member]):
        target = target or ctx.author
        url = (f"https://some-random-api.com/canvas/misc/namecard?avatar={target.avatar.url}"
               f"&birthday={target.created_at.strftime('%Y/%m/%d %H:%M:%S')}&username={target.name}")
        embed = discord.Embed(title="Gayshit Infact",
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.utcnow())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text="API: some-random-api.com/canvas/misc/namecard")
        embed.set_image(url=url.replace(" ", "%20"))
        await ctx.send(embed=embed)

    # @avatar_command_group.command(name="spin", description="You spin me right round baby right round")
    async def genshin_namecard_avatar_command(self, ctx, target: t.Optional[discord.Member]):
        target = target or ctx.author
        url = f"https://some-random-api.com/canvas/misc/spin?avatar={target.avatar.url}"
        embed = discord.Embed(title="Spin",
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.utcnow())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text="API: some-random-api.com/canvas/misc/spin")
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @avatar_command_group.command(name="DVD", description="Scene from Tonikawa")
    async def tonikawa_scene_avatar_command(self, ctx, target: t.Optional[discord.Member]):
        target = target or ctx.author
        url = f"https://some-random-api.com/canvas/misc/tonikawa?avatar={target.avatar.url}"
        embed = discord.Embed(title="D V D",
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.utcnow())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text="API: some-random-api.com/canvas/misc/tonikawa")
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @avatar_command_group.command(name="tweet", description="What has this user tweeted?")
    async def tweet_avatar_command(self, ctx, target: discord.Member, *, comment: str):
        print(target)
        url = f"https://some-random-api.com/canvas/tweet"
        url += f"?avatar={quote(target.avatar.url)}"
        url += f"&comment={quote(comment)}"
        url += f"&displayname={quote(target.display_name)}"
        url += f"&username={quote(target.name)}"
        url += f"&replies={r.randint(-1, 1000)}"
        url += f"&likes={r.randint(-1, 100000)}"
        url += f"&retweets={r.randint(-1, 50000)}"
        url += f"&theme={r.choice(['light', 'dim', 'dark'])}"
        embed = discord.Embed(title=f"New tweet from {target.name}!",
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.utcnow())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text="API: some-random-api.com/canvas/misc/tweet")
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @avatar_command_group.command(name="youtube", aliases=["comment"], description="What has this user commented?")
    async def tweet_avatar_command(self, ctx, target: discord.Member, *, comment: str):
        print(target)
        url = f"https://some-random-api.com/canvas/youtube-comment"
        url += f"?avatar={quote(target.avatar.url)}"
        url += f"&comment={quote(comment)}"
        url += f"&username={quote(target.name)}"
        embed = discord.Embed(title=f"{target.name} commented",
                              color=self.bot.COLOR,
                              timestamp=dt.datetime.utcnow())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text="API: some-random-api.com/canvas/misc/youtube-comment")
        embed.set_image(url=url)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Avatar(bot))
