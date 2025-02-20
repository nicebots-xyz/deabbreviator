# Copyright (c) NiceBots
# SPDX-License-Identifier: MIT

from discord.ext import commands

from src import custom
from src.database.models import Guild, User


async def _preload_user(ctx: custom.Context) -> bool:
    """Preload the user object into the context object.

    Args:
    ----
        ctx: The context object to preload the user object into.

    Returns:
    -------
        bool: (True) always.

    """
    if isinstance(ctx, custom.ExtContext):
        ctx.user_obj = await User.get_or_none(id=ctx.author.id) if ctx.author else None
    else:
        ctx.user_obj = await User.get_or_none(id=ctx.user.id) if ctx.user else None
    return True


preload_user = commands.check(_preload_user)  # pyright: ignore [reportArgumentType]


async def _preload_guild(ctx: custom.Context) -> bool:
    """Preload the guild object into the context object.

    Args:
    ----
        ctx: The context object to preload the guild object into.

    Returns:
    -------
        bool: (True) always.

    """
    ctx.guild_obj = await Guild.get_or_none(id=ctx.guild.id) if ctx.guild else None
    return True


preload_guild = commands.check(_preload_guild)  # pyright: ignore [reportArgumentType]


async def _preload_or_create_user(ctx: custom.Context) -> bool:
    """Preload or create the user object into the context object. If the user object does not exist, create it.

    Args:
    ----
        ctx: The context object to preload or create the user object into.

    Returns:
    -------
        bool: (True) always.

    """
    ctx.user_obj, _ = await User.get_or_create(id=ctx.author.id) if ctx.author else (None, None)
    return True


preload_or_create_user = commands.check(_preload_or_create_user)


async def _preload_or_create_guild(ctx: custom.Context) -> bool:
    """Preload or create the guild object into the context object. If the guild object does not exist, create it.

    Args:
    ----
        ctx: The context object to preload or create the guild object into.

    Returns:
    -------
        bool: (True) always.

    """
    ctx.guild_obj, _ = await Guild.get_or_create(id=ctx.guild.id) if ctx.guild else (None, None)
    return True


preload_or_create_guild = commands.check(_preload_or_create_guild)  # pyright: ignore [reportArgumentType]
