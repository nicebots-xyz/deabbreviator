# Copyright (c) NiceBots.xyz
# SPDX-License-Identifier: MIT

from logging import getLogger
from typing import TYPE_CHECKING, Any, override

import discord
from discord import Message
from discord.ext import bridge
from discord.ext.bridge import (
    BridgeExtContext,
)

from src.i18n.classes import ExtensionTranslation, TranslationWrapper, apply_locale

logger = getLogger("bot")


class ApplicationContext(bridge.BridgeApplicationContext):
    def __init__(self, bot: discord.Bot, interaction: discord.Interaction) -> None:
        self.translations: TranslationWrapper = TranslationWrapper({}, "en-US")  # empty placeholder
        super().__init__(bot=bot, interaction=interaction)

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
        super().__init__(**kwargs)

    def load_translations(self) -> None:
        if hasattr(self.command, "translations") and self.command.translations:  # pyright: ignore[reportUnknownArgumentType,reportOptionalMemberAccess,reportAttributeAccessIssue]
            locale: str | None = None
            if guild := self.guild:  # pyright: ignore[reportUnnecessaryComparison]
                locale = guild.preferred_locale  # pyright: ignore[reportFunctionMemberAccess]
            self.translations = apply_locale(
                self.command.translations,  # pyright: ignore[reportUnknownArgumentType,reportAttributeAccessIssue,reportOptionalMemberAccess]
                locale,
            )


class Bot(bridge.Bot):
    def __init__(self, *args: Any, **options: Any) -> None:
        self.translations: list[ExtensionTranslation] = options.pop("translations", [])
        super().__init__(*args, **options)

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
        return await super().get_application_context(interaction, cls=cls)

    @override
    async def get_context(
        self,
        message: Message,
        cls: None | type[bridge.BridgeExtContext] = None,
    ) -> BridgeExtContext:
        cls = cls if cls is not None else ExtContext
        ctx = await super().get_context(message, cls=cls)
        if isinstance(ctx, ExtContext):
            ctx.load_translations()
        return ctx


Context: ApplicationContext = ApplicationContext  # pyright: ignore [reportRedeclaration]

if TYPE_CHECKING:  # temp fix for https://github.com/Pycord-Development/pycord/pull/2611
    type Context = ExtContext | ApplicationContext

__all__ = ["Bot", "Context", "ExtContext", "ApplicationContext"]
