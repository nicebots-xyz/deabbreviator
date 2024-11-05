# Copyright (c) NiceBots.xyz
# SPDX-License-Identifier: MIT

import aiohttp
import discord
from discord.ext import commands, tasks
from schema import Schema

from src.log import logger

default = {
    "enabled": False,
    "url": "",
    "every": 60,
}

schema = Schema(
    {
        "enabled": bool,
        "url": str,
        "every": int,
    },
)


class Status(commands.Cog):
    def __init__(self, bot: discord.Bot, config: dict) -> None:
        self.bot = bot
        self.config = config
        self.push_status_loop = tasks.loop(seconds=self.config["every"])(self.push_status_loop)

    @commands.Cog.listener(once=True)
    async def on_ready(self) -> None:
        self.push_status_loop.start()

    async def push_status_loop(self) -> None:
        try:
            await self.push_status()
            logger.info("Pushed status.")
        except Exception:  # noqa: BLE001
            logger.exception("Failed to push status.")

    async def push_status(self) -> None:
        ping = str(round(self.bot.latency * 1000))
        async with aiohttp.ClientSession() as session, session.get(self.config["url"] + ping) as resp:
            resp.raise_for_status()


def setup(bot: discord.Bot, config: dict) -> None:
    bot.add_cog(Status(bot, config))
