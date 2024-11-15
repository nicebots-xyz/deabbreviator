# Copyright (c) NiceBots.xyz
# SPDX-License-Identifier: MIT

from typing import TYPE_CHECKING, Any

from .handlers import error_handler


async def patch(config: dict[str, Any]) -> None:
    sentry_sdk = None
    if config.get("sentry", {}).get("dsn"):
        import sentry_sdk
        from sentry_sdk.integrations.asyncio import AsyncioIntegration
        from sentry_sdk.integrations.logging import LoggingIntegration
        from sentry_sdk.scrubber import (
            DEFAULT_DENYLIST,
            DEFAULT_PII_DENYLIST,
            EventScrubber,
        )

        sentry_sdk.init(
            dsn=config["sentry"]["dsn"],
            integrations=[
                AsyncioIntegration(),
                LoggingIntegration(),
            ],
            event_scrubber=EventScrubber(
                denylist=[*DEFAULT_DENYLIST, "headers", "kwargs"],
                pii_denylist=[*DEFAULT_PII_DENYLIST, "headers", "kwargs"],
            ),
        )

    from discord.ui import View

    if TYPE_CHECKING:
        from discord import Interaction
        from discord.ui import Item

    async def on_error(
        self: View,  # noqa: ARG001
        error: Exception,
        item: "Item[View]",  # noqa: ARG001
        interaction: "Interaction",
    ) -> None:
        await error_handler.handle_error(
            error,
            interaction,
            raw_translations=config["translations"],
            use_sentry_sdk=bool(sentry_sdk),
        )

    View.on_error = on_error
