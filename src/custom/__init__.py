# Copyright (c) NiceBots.xyz
# SPDX-License-Identifier: MIT

from logging import getLogger
from typing import Any  # pyright: ignore[reportDeprecated]

import discord
from discord import Message
from discord.ext import bridge
from discord.ext.bridge import (
    BridgeExtContext,  # pyright: ignore [reportMissingTypeStubs]
)
from typing_extensions import override

from src.i18n.classes import ExtensionTranslation, TranslationWrapper, apply_locale

logger = getLogger("bot")


class ApplicationContext(bridge.BridgeApplicationContext):
    def __init__(self, bot: discord.Bot, interaction: discord.Interaction) -> None:
        self.translations: TranslationWrapper = TranslationWrapper({}, "en-US")  # empty placeholder
        super().__init__(bot=bot, interaction=interaction)  # pyright: ignore[reportUnknownMemberType]

    @override
    def __setattr__(self, key: Any, value: Any) -> None:
        if key == "command" and hasattr(value, "translations"):
            self.translations = apply_locale(
                value.translations,
                self.locale,
            )
        super().__setattr__(key, value)


class ExtContext(bridge.BridgeExtContext):
    def __init__(self, **kwargs: Any) -> None:
        self.translations: TranslationWrapper = TranslationWrapper({}, "en-US")  # empty placeholder
        super().__init__(**kwargs)  # pyright: ignore[reportUnknownMemberType]

    def load_translations(self) -> None:
        if hasattr(self.command, "translations") and self.command.translations:  # pyright: ignore[reportUnknownMemberType,reportUnknownArgumentType,reportOptionalMemberAccess,reportAttributeAccessIssue]
            locale: str | None = None
            if guild := self.guild:  # pyright: ignore[reportUnnecessaryComparison] # for some reason pyright thinks guild is function
                locale = guild.preferred_locale  # pyright: ignore[reportFunctionMemberAccess]
            self.translations = apply_locale(
                self.command.translations,  # pyright: ignore[reportUnknownMemberType,reportUnknownArgumentType,reportAttributeAccessIssue,reportOptionalMemberAccess]
                locale,
            )


class Bot(bridge.Bot):
    def __init__(self, *args: Any, **options: Any) -> None:
        self.translations: list[ExtensionTranslation] = options.pop("translations", [])
        super().__init__(*args, **options)  # pyright: ignore[reportUnknownMemberType]

        @self.listen(name="on_ready", once=True)
        async def on_ready() -> None:  # pyright: ignore[reportUnusedFunction]
            logger.success("Bot started successfully")  # pyright: ignore[reportAttributeAccessIssue]

    @override
    async def get_application_context(
        self,
        interaction: discord.Interaction,
        cls: None | type[bridge.BridgeApplicationContext] = None,
    ) -> bridge.BridgeApplicationContext:
        cls = cls if cls is not None else ApplicationContext
        return await super().get_application_context(interaction, cls=cls)  # pyright: ignore [reportUnknownMemberType]

    @override
    async def get_context(
        self,
        message: Message,
        cls: None | type[bridge.BridgeExtContext] = None,
    ) -> BridgeExtContext:
        cls = cls if cls is not None else ExtContext
        ctx = await super().get_context(message, cls=cls)  # pyright: ignore [reportUnknownMemberType]
        if isinstance(ctx, ExtContext):
            ctx.load_translations()
        return ctx


Context = ExtContext | ApplicationContext

__all__ = ["Bot", "Context", "ExtContext", "ApplicationContext"]
