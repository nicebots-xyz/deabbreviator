# Copyright (c) NiceBots.xyz
# SPDX-License-Identifier: MIT

from typing import Any

import aiohttp
import discord
from discord.ext import commands, tasks
from schema import Optional, Schema
from typing_extensions import override

from src.log import logger

TOPGG_BASE_URL = "https://top.gg/api"
DISCORDSCOM_BASE_URL = "https://discords.com/bots/api/bot"

default = {
    "enabled": False,
}

schema = Schema(
    {
        Optional("topgg_token"): str,
        Optional("discordscom_token"): str,
        "enabled": bool,
    },
)


async def post_request(url: str, headers: dict[Any, Any], payload: dict[Any, Any]) -> None:
    async with aiohttp.ClientSession() as session, session.post(url, headers=headers, json=payload) as resp:
        # raise the eventual status code
        resp.raise_for_status()


async def try_post_request(url: str, headers: dict[Any, Any], payload: dict[Any, Any]) -> None:
    try:
        await post_request(url, headers, payload)
    except aiohttp.ClientResponseError as e:
        if e.status == 401:  # noqa: PLR2004
            logger.error("Invalid token")
        else:
            logger.error(e)
    except Exception:  # noqa: BLE001
        logger.exception(f"Failed to post request to {url}")


class Listings(commands.Cog):
    def __init__(self, bot: discord.Bot, config: dict[Any, Any]) -> None:
        self.bot: discord.Bot = bot
        self.config: dict = config
        self.topgg = bool(config.get("topgg_token"))
        self.discordscom = bool(config.get("discordscom_token"))

    @commands.Cog.listener("on_ready")
    async def on_ready(self) -> None:
        self.update_count_loop.start()

    @override
    def cog_unload(self) -> None:
        self.update_count_loop.cancel()

    @tasks.loop(minutes=30)
    async def update_count_loop(self) -> None:
        try:
            if self.topgg:
                await self.update_count_topgg()
            if self.discordscom:
                await self.update_count_discordscom()
        except Exception:  # noqa: BLE001
            logger.exception("Failed to update count")

    async def update_count_discordscom(self) -> None:
        headers = {
            "Authorization": self.config["discordscom_token"],
            "Content-Type": "application/json",
        }
        payload = {"server_count": len(self.bot.guilds)}
        url = f"{DISCORDSCOM_BASE_URL}/{self.bot.user.id}/setservers"
        await try_post_request(url, headers, payload)
        logger.info("Updated discords.com count")

    async def update_count_topgg(self) -> None:
        headers = {"Authorization": self.config["topgg_token"]}
        payload = {"server_count": len(self.bot.guilds)}
        url = f"{TOPGG_BASE_URL}/bots/{self.bot.user.id}/stats"
        await try_post_request(url, headers, payload)
        logger.info("Updated top.gg count")


def setup(bot: discord.Bot, config: dict) -> None:
    if not config.get("topgg_token") and not config.get("discordscom_token"):
        logger.error("Top.gg or Discords.com token not found")
        return

    bot.add_cog(Listings(bot, config))
