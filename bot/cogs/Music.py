import asyncio
import datetime as dt
import enum
import random
import re
import typing as t

import discord
from discord.ext import commands
import wavelink

import util


URL_REGEX = (r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s("
             r")<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))")

OPTIONS = {
    "1️⃣": 0,
    "2⃣": 1,
    "3⃣": 2,
    "4⃣": 3,
    "5⃣": 4,
}


class AlreadyConnectedToChannel(commands.CommandError):
    pass


class NoVoiceChannel(commands.CommandError):
    pass


class QueueIsEmpty(commands.CommandError):
    pass


class NoTracksFound(commands.CommandError):
    pass


class PlayerAlreadyPaused(commands.CommandError):
    pass


class PlayerAlreadyPlaying(commands.CommandError):
    pass


class NoMoreTracks(commands.CommandError):
    pass


class NoPreviousTracks(commands.CommandError):
    pass


class InvalidRepeatMode(commands.CommandError):
    pass


class InvalidTimeString(commands.CommandError):
    pass


class RepeatMode(enum.Enum):
    NONE = 0
    ONE = 1
    ALL = 2


class Queue:
    _REPEAT_MODES = {
        "none": RepeatMode.NONE,
        "1": RepeatMode.ONE,
        "one": RepeatMode.ONE,
        "all": RepeatMode.ALL
    }

    def __init__(self):
        self._queue = []
        self.pos = 0
        self.repeat_mode = RepeatMode.NONE

    def __len__(self):
        return len(self._queue)

    @property
    def is_empty(self):
        return not self._queue

    @property
    def first_track(self):
        if not self._queue:
            raise QueueIsEmpty
        return self._queue[0]

    @property
    def current_track(self):
        if self.is_empty:
            raise QueueIsEmpty
        if self.pos <= len(self._queue) - 1:
            return self._queue[self.pos]

    @property
    def upcoming_tracks(self):
        if self.is_empty:
            raise QueueIsEmpty
        return self._queue[self.pos + 1:]

    @property
    def previous_tracks(self):
        if self.is_empty:
            raise QueueIsEmpty
        return self._queue[:self.pos]

    @property
    def length(self):
        return len(self._queue)

    def get_next_track(self):
        if not self._queue:
            raise QueueIsEmpty
        self.pos += 1

        if self.pos < 0:
            return None
        elif self.pos > len(self._queue) - 1:
            if self.repeat_mode == RepeatMode.ALL:
                self.pos = 0
            else:
                return None

        return self._queue[self.pos]

    def shuffle(self):
        if not self._queue:
            raise QueueIsEmpty

        upcoming = self.upcoming_tracks
        random.shuffle(upcoming)
        self._queue = self._queue[:self.pos + 1]
        self._queue.extend(upcoming)

    def set_repeat_mode(self, mode: str):
        try:
            self.repeat_mode = self._REPEAT_MODES[mode]
        except KeyError:
            raise InvalidRepeatMode

    def add_track(self, *args):
        self._queue.extend(args)

    def clear(self):
        self.pos = 0
        self._queue.clear()


class Player(wavelink.Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = Queue()

    async def connect(self, ctx, channel=None):
        if self.is_connected:
            raise AlreadyConnectedToChannel

        if not (channel := getattr(ctx.author.voice, "channel", channel)):
            raise NoVoiceChannel

        await super().connect(channel.id)
        return channel

    async def teardown(self):
        try:
            self.queue.clear()
            await self.destroy()
        except KeyError:
            pass

    async def add_tracks(self, ctx, tracks):
        if not tracks:
            raise NoTracksFound

        if isinstance(tracks, wavelink.TrackPlaylist):
            self.queue.add_track(*tracks.tracks)
            await ctx.send(f"Added {len(tracks.tracks)} tracks!")
        elif len(tracks) == 1:
            self.queue.add_track(tracks[0])
            await ctx.send(f"Added [{tracks[0].title}]({tracks[0].uri}) to the queue")
        else:
            if track := await self.choose_track(ctx, tracks):
                self.queue.add_track(track)
                await ctx.send(f"Added {track.title} to the queue")

        if not self.is_playing and not self.queue.is_empty:
            await self.start_playback()

    async def choose_track(self, ctx, tracks):
        def _check(r, u):
            return (
                    r.emoji in OPTIONS.keys()
                    and u == ctx.author
                    and r.message.id == msg.id
            )

        embed = discord.Embed(
            title="Choose a song",
            description=(
                "\n".join(
                    f"**{i + 1}.** {t.title} ({t.length // 60000}:{str(t.length % 60).zfill(2)})"
                    for i, t in enumerate(tracks[:5])
                )
            ),
            color=self.bot.COLOR,
            timestamp=dt.datetime.utcnow()
        )
        embed.set_author(name="Search results", icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f"Queried by {ctx.author.display_name}", icon_url=self.bot.user.avatar.url)

        msg = await ctx.send(embed=embed)
        for emoji in list(OPTIONS.keys())[:min(len(tracks), len(OPTIONS))]:
            await msg.add_reaction(emoji)

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=60.0, check=_check)
        except asyncio.TimeoutError:
            await msg.delete()
            await ctx.message.delete()
            await ctx.send("Selection timed out")
        else:
            await msg.delete()
            return tracks[OPTIONS[reaction.emoji]]

    async def start_playback(self):
        await self.play(self.queue.current_track)

    async def advance(self):
        try:
            if track := self.queue.get_next_track():
                await self.play(track)
        except QueueIsEmpty:
            pass

    async def repeat_track(self):
        await self.play(self.queue.current_track)


class Music(commands.Cog, wavelink.WavelinkMixin):
    """All that high fidelity music stuff"""
    def __init__(self, bot):
        self.bot = bot
        self.wavelink = wavelink.Client(bot=bot)
        self.bot.loop.create_task(self.start_nodes())

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member.bot and after.channel is None:
            if not [m for m in before.channel.members if not m.bot]:
                await self.get_player(member.guild).teardown()

    @wavelink.WavelinkMixin.listener()
    async def on_node_ready(self, node: wavelink.Node):
        self.bot.log(f"Wavelink node ready! Node: {node.identifier}")

    @wavelink.WavelinkMixin.listener("on_track_stuck")
    @wavelink.WavelinkMixin.listener("on_track_end")
    @wavelink.WavelinkMixin.listener("on_track_exception")
    async def on_player_stop(self, node, payload):
        if payload.player.queue.repeat_mode == RepeatMode.ONE:
            await payload.player.repeat_track()
        else:
            await payload.player.advance()

    async def cog_check(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("Music commands are not available in DMs.")
            return False

        return True

    async def start_nodes(self):
        await self.bot.wait_until_ready()

        nodes = {
            "US_EAST": {
                "host": "127.0.0.1",
                "port": "6969",
                "rest_uri": "http://127.0.0.1:6969",
                "password": "TMP_PSWD",
                "identifier": "US_EAST",
                "region": "us_east"
            }
        }

        for node in nodes.values():
            await self.wavelink.initiate_node(**node)

    def get_player(self, obj):
        if isinstance(obj, commands.Context):
            return self.wavelink.get_player(obj.guild.id, cls=Player, context=obj)
        elif isinstance(obj, discord.Guild):
            return self.wavelink.get_player(obj.id, cls=Player)

    @commands.command(name="connect", aliases=["join"],
                      description="Connects the bot to a specified channel or the channel the user is in.")
    async def connect_command(self, ctx, channel: t.Optional[discord.VoiceChannel]):
        player = self.get_player(ctx)
        channel = await player.connect(ctx, channel)
        await ctx.send(f"Connected to {channel.name}")

    @connect_command.error
    async def connect_command_error(self, ctx, exc):
        if isinstance(exc, AlreadyConnectedToChannel):
            await ctx.send("I'm already connected to a channel!")
        elif isinstance(exc, NoVoiceChannel):
            await ctx.send("There's no voice channel to join! Are you in one?")

    @commands.command(name="disconnect", aliases=["dc", "leave"],
                      description="Disconnects the bot from a voice channel and clears the queue")
    async def disconnect_command(self, ctx):
        player = self.get_player(ctx)
        await player.teardown()
        await ctx.send("Disconnected!")

    @commands.command(name="play", aliases=["p"],
                      description="Plays a song. Also works as an unpaused command. Supports youtube searching too.")
    async def play_command(self, ctx, *, query: t.Optional[str]):
        player = self.get_player(ctx)

        if not player.is_connected:
            await player.connect(ctx)

        if query is None:
            if player.queue.is_empty:
                raise QueueIsEmpty
            if not player.is_paused:
                raise PlayerAlreadyPlaying
            await player.set_pause(False)
            await ctx.send("Playback resumed")

        else:
            query = query.strip("<>")
            if not re.match(URL_REGEX, query):
                query = f"ytsearch:{query}"

            await player.add_tracks(ctx, await self.wavelink.get_tracks(query))

    @play_command.error
    async def play_command_error(self, ctx, exc):
        if isinstance(exc, PlayerAlreadyPlaying):
            await ctx.send("Already playing")
        elif isinstance(exc, QueueIsEmpty):
            await ctx.send("The queue is empty")
        elif isinstance(exc, NoVoiceChannel):
            await ctx.send("There's no voice channel to join! Are you in one?")

    @commands.command(name="pause", description="Pauses the current playing track")
    async def pause_command(self, ctx):
        player = self.get_player(ctx)

        if player.is_paused:
            raise PlayerAlreadyPaused

        await player.set_pause(True)
        await ctx.send("Playback is paused")

    @pause_command.error
    async def pause_command_error(self, ctx, exc):
        if isinstance(exc, PlayerAlreadyPaused):
            await ctx.send("Playback is already paused")

    @commands.command(name="stop", description="Stops the playback and clears the queue")
    async def stop_command(self, ctx):
        player = self.get_player(ctx)
        player.queue.clear()
        await player.stop()
        await ctx.send("Playback stopped")

    @commands.command(name="next", aliases=["skip", "s"],
                      description="Skips the song and moves to the next")
    async def next_track_command(self, ctx):
        player = self.get_player(ctx)

        if not player.queue.upcoming_tracks:
            raise NoMoreTracks

        await player.stop()
        await ctx.send("Skipping to next song")

    @next_track_command.error
    async def next_track_command_error(self, ctx, exc):
        if isinstance(exc, NoMoreTracks):
            await ctx.send("There are no more tracks in the queue")
        elif isinstance(exc, QueueIsEmpty):
            await ctx.send("The queue is empty")

    @commands.command(name="previous", description="Moves backwards in the queue")
    async def previous_track_command(self, ctx):
        player = self.get_player(ctx)

        if not player.queue.previous_tracks:
            raise NoPreviousTracks

        # Might be best to figure out a better way to do this
        player.queue.pos -= 2
        await player.stop()
        await ctx.send("Skipping back to previous song")

    @previous_track_command.error
    async def previous_track_command_error(self, ctx, exc):
        if isinstance(exc, NoPreviousTracks):
            await ctx.send("There are no previous tracks in the queue")
        elif isinstance(exc, QueueIsEmpty):
            await ctx.send("The queue is empty")

    @commands.command(name="shuffle", description="Shuffles the queue")
    async def shuffle_queue_command(self, ctx):
        player = self.get_player(ctx)
        player.queue.shuffle()
        await ctx.send("Shuffled the queue")

    @shuffle_queue_command.error
    async def shuffle_queue_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("The queue is empty!")

    @commands.command(name="repeat", description="Set the repeat mode: None, One(1), All")
    async def repeat_track_command(self, ctx, mode: str):
        if mode.lower() not in ("none", "one", "1", "all"):
            raise InvalidRepeatMode

        player = self.get_player(ctx)
        player.queue.set_repeat_mode(mode.lower())
        await ctx.send(f"Set the repeat mode to {mode}.")

    @commands.command(name="queue", aliases=["q"], description="Displays the queue")
    async def queue_command(self, ctx, show: t.Optional[int] = 10):
        player = self.get_player(ctx)
        if player.queue.is_empty:
            raise QueueIsEmpty

        embed = discord.Embed(
            title="Queue",
            description=f"Showing up to {show:,} track(s)",
            color=self.bot.COLOR,
            timestamp=dt.datetime.utcnow()
        )
        embed.set_author(name="Queue Results", icon_url=self.bot.user.avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar.url)
        embed.add_field(name="**Currently playing**",
                        value=f"[{getattr(player.queue.current_track, 'title', 'No tracks playing')}]"
                              f"({getattr(player.queue.current_track, 'uri', '')}) "
                              f"({getattr(player.queue.current_track, 'length', 0) // 60000}:"
                              f"{str(getattr(player.queue.current_track, 'length', 0) % 60).zfill(2)})",
                        inline=False
                        )
        if upcoming := player.queue.upcoming_tracks:
            embed.add_field(
                name="**Next up**",
                value="\n".join(
                    f"[{track.title}]({track.uri}) ({track.length // 60000}:{str(track.length % 60).zfill(2)})"
                    for track in upcoming[:show]) if upcoming else "No upcoming tracks",
                inline=False
            )
        if previous := player.queue.previous_tracks:
            embed.add_field(
                name="**Previous Tracks**",
                value="\n".join(
                    f"[{track.title}]({track.uri}) ({track.length // 60000}:{str(track.length % 60).zfill(2)})"
                    for track in previous[:show // 2]) if previous else "No previous tracks",
                inline=False
            )

        await ctx.send(embed=embed)

    @queue_command.error
    async def queue_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("The queue is empty!")

    @commands.command(name="playing", aliases=["np"], description="Shows information on the current playing song")
    async def now_playing_command(self, ctx):
        num_symbols = 10
        filled_character = ":white_large_square:"
        cursor_character = ":white_square_button:"
        future_character = ":black_large_square:"
        player = self.get_player(ctx)
        if player.queue.is_empty:
            raise QueueIsEmpty
        if player.is_paused:
            raise PlayerAlreadyPaused

        embed = discord.Embed(
            title="Current Track",
            color=self.bot.COLOR,
            timestamp=dt.datetime.utcnow()
        )
        embed.set_author(name="Track Info", icon_url=self.bot.user.avatar.url, url=player.queue.current_track.uri)
        embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar.url)
        embed.set_thumbnail(url=player.queue.current_track.thumb)
        embed.add_field(name="Track title", value=player.queue.current_track.title, inline=False)
        embed.add_field(name="Author", value=player.queue.current_track.author, inline=False)

        position = divmod(player.position, 60000)
        length = divmod(player.queue.current_track.length, 60000)
        num_filled = int((player.position / player.queue.current_track.length) * num_symbols)
        visual_string = filled_character * num_filled + cursor_character + future_character * (num_symbols - num_filled)
        embed.add_field(
            name="Position",
            value=f"{int(position[0])}:{round(position[1]/1000):02}/{int(length[0])}:{round(length[1]/1000):02}"
                  f"\n{visual_string}",
            inline=False
        )

        await ctx.send(embed=embed)

    @now_playing_command.error
    async def now_playing_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("The queue is empty!")
        elif isinstance(exc, PlayerAlreadyPaused):
            await ctx.send("There is no track playing!")

    @commands.command(name="restart", description="Restarts the current track")
    async def restart_track_command(self, ctx):
        player = self.get_player(ctx)
        if player.queue.is_empty:
            raise QueueIsEmpty
        await player.seek(0)
        await ctx.send("Restarted the track!")

    @restart_track_command.error
    async def restart_track_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("The queue is empty!")

    @commands.command(name="seek", description="Seeks to a specific spot in the song. 4 minutes 3 seconds -> 4m3s")
    async def seek_command(self, ctx, pos: str):
        player = self.get_player(ctx)
        if player.queue.is_empty:
            raise QueueIsEmpty

        secs = util.time_string_to_seconds(pos)

        await player.seek(1000 * secs)
        await ctx.send(f"Moved to {secs // 60}:{str(secs % 60).zfill(2)}")

    @commands.command(name="skipto", aliases=["s2", "skip2"], description="Traverse the queue. "
                                                                          "M!skipto 2 will not move forward two, "
                                                                          "it will move to queue position 2")
    async def skipto_track_command(self, ctx, idx: int):
        player = self.get_player(ctx)
        if player.queue.is_empty:
            raise QueueIsEmpty
        if not 0 <= idx <= player.queue.length:
            raise NoMoreTracks

        player.queue.pos = idx - 2
        await player.stop()
        await ctx.send(f"Playing track #{idx}")

    @skipto_track_command.error
    async def skipto_track_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("The queue is empty!")
        elif isinstance(exc, NoMoreTracks):
            await ctx.send("There are no more tracks to play!")


async def setup(bot):
    await bot.add_cog(Music(bot))
