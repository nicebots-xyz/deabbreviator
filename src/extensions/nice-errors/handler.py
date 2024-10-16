# Copyright (c) NiceBots.xyz
# SPDX-License-Identifier: MIT

import discord
from discord.ext import commands
from discord.interactions import Interaction
from src.i18n.classes import RawTranslation
from src.i18n import apply_locale
from src import custom
import difflib

sentry_sdk = None

try:
    import sentry_sdk
except ImportError:
    pass


def find_most_similar(word: str, word_list: list[str]) -> str | None:
    if result := difflib.get_close_matches(word, word_list, n=1, cutoff=0.6):
        return result[0]
    return None


def find_similar_command(ctx: custom.ExtContext) -> str | None:
    command: str | None = ctx.invoked_with
    if not command:
        return None
    if not isinstance(ctx.bot, custom.Bot):  # pyright: ignore[reportUnknownMemberType]
        return None
    command_list: list[str] = [cmd.name for cmd in ctx.bot.commands]  # pyright: ignore[reportUnknownMemberType,reportUnknownVariableType]
    similar_command: str | None = find_most_similar(command, command_list)
    return similar_command


def get_locale(ctx: custom.Context | Interaction) -> str | None:
    locale: str | None = None
    if isinstance(ctx, custom.ApplicationContext):
        locale = ctx.locale or ctx.guild_locale
    elif isinstance(ctx, custom.ExtContext):
        if ctx.guild:  # pyright: ignore[reportUnnecessaryComparison] # for some reason pyright thinks guild is function
            locale = ctx.guild.preferred_locale  # pyright: ignore[reportFunctionMemberAccess]
    elif isinstance(ctx, Interaction):  # pyright: ignore[reportUnnecessaryIsInstance] # we want to really make sure
        locale = ctx.locale or ctx.guild_locale
    return locale


async def handle_error(
    error: Exception | discord.ApplicationCommandInvokeError,
    ctx: discord.Interaction | custom.Context,
    /,
    raw_translations: dict[str, RawTranslation],
    use_sentry_sdk: bool = False,
):
    original_error = error
    report: bool = True
    translations = apply_locale(raw_translations, get_locale(ctx))
    if isinstance(error, discord.ApplicationCommandInvokeError):
        original_error = error.original
    if isinstance(error, commands.CommandNotFound) and isinstance(
        ctx, custom.ExtContext
    ):
        if similar_command := find_similar_command(ctx):
            message = translations.error_command_not_found.format(
                similar_command=similar_command
            )
            report = False  # this is not an error in the program
        else:
            return  # this is not an error in the program
    elif isinstance(error, discord.Forbidden):
        message = (
            translations.error_missing_permissions
            + f"\n`{original_error.args[0].split(':')[-1].strip()}`"
        )
    else:
        message = translations.error_generic
    if report and use_sentry_sdk and sentry_sdk:
        out = sentry_sdk.capture_exception(error)
        message += f"\n\n-# {translations.reported_to_devs} - `{out}`"
    # capture the error *before* sending the message to avoid errors in the error handlers
    await ctx.respond(message, ephemeral=True)  # pyright: ignore[reportUnknownMemberType]
    if report:
        raise error
