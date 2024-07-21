"""We define the `bot` instance here."""

import discord
from discord.ext import commands

from .__version__ import __version__
from .settings import settings


# Use this hacks to prevent the commands from being added multiple times
__VERSION_COMMAND_ENABLED = False
__PING_COMMAND_ENABLED = False

intents = discord.Intents.default()
# noinspection PyDunderSlots, PyUnresolvedReferences
intents.members = True
# noinspection PyDunderSlots, PyUnresolvedReferences
intents.message_content = True
bot = commands.Bot(command_prefix=settings.BOT_COMMAND_PREFIX, intents=intents)

# Enable the `!version` and `!ping` commands on the lower level than the `electro` Framework does
if not __VERSION_COMMAND_ENABLED:
    @bot.command(name="version")
    async def get_version(ctx):
        await ctx.send(f"Version: {__version__}")


    __VERSION_COMMAND_ENABLED = True

if not __PING_COMMAND_ENABLED:
    @bot.command(name="ping")
    async def ping(ctx):
        await ctx.send("Pong!")


    __PING_COMMAND_ENABLED = True
