# Copyright (c) NiceBots.xyz
# SPDX-License-Identifier: MIT

import contextlib
import difflib
from collections.abc import Callable, Coroutine
from typing import Any, TypeVar, final, override

import discord
from discord.ext import bridge, commands

from src import custom
from src.i18n import apply_locale
from src.i18n.classes import RawTranslation, TranslationWrapper

sentry_sdk = None

with contextlib.suppress(ImportError):
    import sentry_sdk


class RunInsteadButton(discord.ui.Button[discord.ui.View]):
    def __init__(
        self,
        label: str,
        *,
        ctx: custom.ExtContext,
        instead: bridge.BridgeExtCommand | commands.Command[Any, Any, Any],
    ) -> None:
        self.ctx = ctx
        self.instead = instead
        super().__init__(style=discord.ButtonStyle.green, label=label)

    @override
    async def callback(self, interaction: discord.Interaction) -> None:
        if (
            not interaction.user
            or not self.ctx.author  # pyright: ignore[reportUnnecessaryComparison]
            or interaction.user.id != self.ctx.author.id  # pyright: ignore[reportFunctionMemberAccess]
        ):
            await interaction.respond(":x: Nope", ephemeral=True)
            return
        await self.instead.invoke(self.ctx)
        await interaction.response.defer()
        if interaction.message:
            with contextlib.suppress(discord.HTTPException):
                await interaction.message.delete()


def find_most_similar(word: str, word_list: list[str]) -> str | None:
    if result := difflib.get_close_matches(word, word_list, n=1, cutoff=0.6):
        return result[0]
    return None


def find_similar_command(
    ctx: custom.ExtContext,
) -> bridge.BridgeExtCommand | commands.Command[Any, Any, Any] | None:
    command: str | None = ctx.invoked_with
    if not command:
        return None
    if not isinstance(ctx.bot, custom.Bot):
        return None
    command_list: dict[str, bridge.BridgeExtCommand | commands.Command[Any, Any, Any]] = {
        cmd.name: cmd
        for cmd in ctx.bot.commands  # pyright: ignore[reportUnknownVariableType]
    }
    similar_command: str | None = find_most_similar(command, list(command_list.keys()))
    if similar_command:
        return command_list.get(similar_command)
    return None


def get_locale(ctx: custom.Context | discord.Interaction) -> str | None:
    locale: str | None = None
    if isinstance(ctx, custom.ApplicationContext):
        locale = ctx.locale or ctx.guild_locale
    elif isinstance(ctx, custom.ExtContext):
        if ctx.guild:  # pyright: ignore[reportUnnecessaryComparison] # for some reason pyright thinks guild is function
            locale = ctx.guild.preferred_locale  # pyright: ignore[reportFunctionMemberAccess]
    elif isinstance(ctx, discord.Interaction):  # pyright: ignore[reportUnnecessaryIsInstance]
        locale = ctx.locale or ctx.guild_locale
    return locale


T = TypeVar("T", bound=Coroutine[Any, Any, Any])
type ErrorHandlersIType[T] = Callable[
    [Exception, discord.Interaction | custom.Context, TranslationWrapper, dict[str, Any], str, bool], T
]
type ErrorHandlerRType = tuple[bool, bool, str, dict[str, Any]]
type ErrorHandlerType = ErrorHandlersIType[Coroutine[Any, Any, ErrorHandlerRType]]
type ErrorHandlersType = dict[
    type[Exception],
    ErrorHandlerType,
]


async def handle_command_not_found(  # noqa: PLR0913
    error: Exception,  # noqa: ARG001
    ctx: custom.Context | discord.Interaction,
    translations: TranslationWrapper,
    sendargs: dict[str, Any],
    message: str,
    report: bool,
) -> ErrorHandlerRType:
    if not isinstance(ctx, custom.ExtContext):
        return False, report, message, sendargs
    if similar_command := find_similar_command(ctx):
        message = translations.error_command_not_found.format(similar_command=similar_command.name)
        view = discord.ui.View(
            RunInsteadButton(
                translations.run_x_instead.format(command=similar_command.name),
                ctx=ctx,
                instead=similar_command,
            ),
            disable_on_timeout=True,
            timeout=60,  # 1 minute
        )
        sendargs["view"] = view
        return False, False, message, sendargs
    return True, False, message, sendargs


DEFAULT_ERROR_HANDLERS: ErrorHandlersType = {
    commands.CommandNotFound: handle_command_not_found,
}


@final
class ErrorHandler:
    def __init__(self, error_handlers: ErrorHandlersType | None = None) -> None:
        if error_handlers:
            self.error_handlers = DEFAULT_ERROR_HANDLERS | error_handlers
        else:
            self.error_handlers = DEFAULT_ERROR_HANDLERS

    def _get_handler(self, error: Exception) -> ErrorHandlerType | None:
        if handler := self.error_handlers.get(type(error)):  # faster but might miss subclasses
            return handler
        for error_type, handler in self.error_handlers.items():  # slower but catches subclasses
            if issubclass(type(error), error_type):
                return handler
        return None

    async def handle_error(
        self,
        error: Exception | discord.ApplicationCommandInvokeError,
        ctx: discord.Interaction | custom.Context,
        /,
        raw_translations: dict[str, RawTranslation],
        use_sentry_sdk: bool = False,
    ) -> None:
        original_error = error
        report: bool = True
        sendargs: dict[str, Any] = {}
        translations = apply_locale(raw_translations, get_locale(ctx))
        message: str = ""
        if isinstance(error, discord.ApplicationCommandInvokeError):
            original_error = error.original

        if handler := self._get_handler(original_error):
            handled, report, message, sendargs = await handler(
                original_error,
                ctx,
                translations,
                sendargs,
                str(error),
                report,
            )
            if handled:
                return
        elif isinstance(error, discord.Forbidden):
            message = translations.error_missing_permissions + f"\n`{original_error.args[0].split(':')[-1].strip()}`"
        else:
            message = translations.error_generic
        if report and use_sentry_sdk and sentry_sdk:
            out = sentry_sdk.capture_exception(error)
            message += f"\n\n-# {translations.reported_to_devs} - `{out}`"
        await ctx.respond(message, ephemeral=True, **sendargs)
        if report:
            raise error

    def add_error_handler(self, error: type[Exception], handler: ErrorHandlerType) -> None:
        self.error_handlers[error] = handler


error_handler = ErrorHandler()
