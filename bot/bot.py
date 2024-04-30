import asyncio
import pprint
import json
import os
import datetime as dt
import pathlib as pl

import aiohttp
import discord
from pymongo import MongoClient
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler


class Matrixine(commands.Bot):
    def __init__(self):
        self.COLOR = 0x1EACC4
        self.OWNER_ID = [901689854411300904]
        self.OWNER_USERNAME = "zettabitep"
        self.VERSION = "0.1.0b"
        self.PREFIX = "M!"
        self.API_BASE = "https://discord.com/api/v9/"
        self.AIOHTTP_SESSION = aiohttp.ClientSession()
        self.APSCHEDULER = AsyncIOScheduler
        self.MONGO_CLIENT = MongoClient(os.getenv("MONGO_URI"))
        self.MONGO_DB = self.MONGO_CLIENT["MatrixineDB"]
        self.stdout_id = 1230708641481363538
        self.STDOUT = None
        self.BOT_INFO = None
        self.CLIENT_ID = None

        self._cogs = [p.stem for p in pl.Path(".").glob("./bot/cogs/*.py")]
        super().__init__(command_prefix=self.prefix,
                         owner_ids=self.OWNER_ID,
                         case_insensitive=True,
                         intents=discord.Intents.all())

    def log(self, msg):
        print(f"[{dt.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}] | {msg}")

    @property
    def latency(self):
        return F"{super().latency * 1000:,.2f}ms"

    async def setup_hook(self):
        self.log("Beginning Setup...")

        for cog in self._cogs:
            await self.load_extension(f"bot.cogs.{cog}")
            self.log(f"Loaded {cog} cog...")

        self.log("Setup finished...")

    def run(self, **kwargs):
        self.log("Running Bot...")
        super().run(token=kwargs["token"], reconnect=True)

    async def close(self):
        self.log("Closing connection to Discord...")
        self.MONGO_CLIENT.close()
        await self.AIOHTTP_SESSION.close()
        await super().close()

    async def on_connect(self):
        self.log(f"Bot connected to Discord API. Latency: {self.latency}")

    async def on_resumed(self):
        self.log(f"Connection resumed. Latency: {self.latency}")

    async def on_error(self, err, *args, **kwargs):
        raise

    async def on_command_error(self, ctx: commands.Context, exc):
        self.log(f"Encountered error while running '{ctx.command}' from {ctx.guild.name} ({ctx.guild.id})")
        if isinstance(exc, commands.MissingRequiredArgument):
            self.log("Error: MissingRequiredArgument")
            await ctx.send("You're missing a required argument!")
            return
        elif hasattr(exc, "original"):
            raise exc.original
        raise exc

    async def on_ready(self):
        await self.change_presence(activity=discord.Game("music | m!help"))
        self.BOT_INFO = await self.application_info()
        self.CLIENT_ID = self.BOT_INFO.id
        self.STDOUT = self.get_channel(self.stdout_id)
        await self.STDOUT.send(
            f"`{dt.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}` | Bot ready! Latency: {self.latency}.")
        self.log(f"Bot ready... Latency: {self.latency}")
        await self.get_bot_info()

    def prefix(self, bot, msg):
        result = self.MONGO_DB["Guilds"].find_one({"_id": msg.guild.id})
        if result:
            prefix = str(result["server_prefix"])
        else:
            prefix = self.PREFIX

        prefixes = commands.when_mentioned_or(prefix)(bot, msg)
        prefixes.append(prefix.lower())
        return prefixes

    async def process_commands(self, msg):
        ctx = await self.get_context(msg, cls=commands.Context)

        if ctx.command is not None:
            self.log(f"Processing command, '{ctx.command.name}', "
                     f"from {ctx.guild.name} ({ctx.guild.id})")
            await self.invoke(ctx)

    async def on_message(self, msg):
        if not msg.author.bot:
            await self.process_commands(msg)

    def get_command_info(self, cmd):
        command_info = {
            "aliases": cmd.aliases,
            "parameters": [param.name for param in cmd.clean_params.values()],
            "description": cmd.description or "No description provided"
        }

        if isinstance(cmd, commands.Group):
            subcommands_info = {}
            for subcommand in cmd.commands:
                subcommands_info[subcommand.name] = self.get_command_info(subcommand)

            command_info["subcommands"] = subcommands_info

        return command_info

    def get_cog_info(self, cog: commands.Cog):
        cog_info = {}

        for cmd in cog.get_commands():
            cog_info[cmd.name] = self.get_command_info(cmd)

        return cog_info

    async def get_bot_info(self):
        bot_info = {
            "name": self.user.name,
            "color": str(hex(self.COLOR)).upper().replace("X", "x"),
            "owner": (self.OWNER_USERNAME, self.OWNER_ID[0]),
            "version": self.VERSION,
            "cogs": {}
        }

        for cog_name, cog in self.cogs.items():
            bot_info["cogs"][cog_name] = self.get_cog_info(cog)

        with open("bot_info.json", "w") as fp:
            json.dump(bot_info, fp, indent=2)

