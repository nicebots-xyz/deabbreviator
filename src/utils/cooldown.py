# Copyright (c) NiceBots
# SPDX-License-Identifier: MIT

import time
from collections.abc import Awaitable, Callable, Coroutine
from functools import wraps
from inspect import isawaitable
from typing import Any, Concatenate, cast

from discord.ext import commands

from src import custom

type ReactiveCooldownSetting[T] = T | Callable[[custom.Bot, custom.Context], T | Coroutine[Any, Any, T]]
type CogCommandFunction[T: commands.Cog, **P] = Callable[Concatenate[T, custom.ApplicationContext, P], Awaitable[None]]


async def parse_reactive_setting[T](value: ReactiveCooldownSetting[T], bot: custom.Bot, ctx: custom.Context) -> T:
    if callable(value):
        value = value(bot, ctx)  # pyright: ignore [reportAssignmentType]
        if isawaitable(value):
            value = await value
    return value  # pyright: ignore [reportReturnType]


class CooldownExceeded(commands.CheckFailure):
    def __init__(self, retry_after: float) -> None:
        self.retry_after: float = retry_after
        super().__init__("You are on cooldown")


# inspired by https://github.com/ItsDrike/code-jam-2024/blob/main/src/utils/ratelimit.py


def cooldown[C: commands.Cog, **P](
    key: ReactiveCooldownSetting[str],
    *,
    limit: ReactiveCooldownSetting[int],
    per: ReactiveCooldownSetting[int],
    strong: ReactiveCooldownSetting[bool] = False,
    cls: ReactiveCooldownSetting[type[CooldownExceeded]] = CooldownExceeded,
) -> Callable[[CogCommandFunction[C, P]], CogCommandFunction[C, P]]:
    def inner(func: CogCommandFunction[C, P]) -> CogCommandFunction[C, P]:
        @wraps(func)
        async def wrapper(self: C, ctx: custom.ApplicationContext, *args: P.args, **kwargs: P.kwargs) -> None:
            cache = ctx.bot.cache
            key_value = await parse_reactive_setting(key, ctx.bot, ctx)
            limit_value = await parse_reactive_setting(limit, ctx.bot, ctx)
            per_value = await parse_reactive_setting(per, ctx.bot, ctx)
            strong_value = await parse_reactive_setting(strong, ctx.bot, ctx)
            cls_value = await parse_reactive_setting(cls, ctx.bot, ctx)

            now = time.time()
            time_stamps = cast(tuple[float, ...], await cache.get(key_value, default=(), namespace="cooldown"))
            time_stamps = tuple(filter(lambda x: x > now - per_value, time_stamps))
            time_stamps = time_stamps[-limit_value:]
            if len(time_stamps) < limit_value or strong_value:
                time_stamps = (*time_stamps, now)
                await cache.set(key_value, time_stamps, namespace="cooldown", ttl=per_value)
                limit_value += 1  # to account for the current command

            if len(time_stamps) >= limit_value:
                raise cls_value(min(time_stamps) - now + per_value)
            await func(self, ctx, *args, **kwargs)

        return wrapper

    return inner
