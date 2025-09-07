# Copyright (c) NiceBots.xyz
# SPDX-License-Identifier: MIT

from typing import TYPE_CHECKING, Any

from src.log import logger as base_logger

from .handlers import error_handler

logger = base_logger.getChild("nice_errors")


async def patch(config: dict[str, Any]) -> None:
    sentry_sdk = None
    if (sentry_config := config.get("sentry", {})).get("dsn"):
        import sentry_sdk  # noqa: PLC0415
        from sentry_sdk.integrations.asyncio import AsyncioIntegration  # noqa: PLC0415
        from sentry_sdk.integrations.logging import LoggingIntegration  # noqa: PLC0415
        from sentry_sdk.scrubber import (  # noqa: PLC0415
            DEFAULT_DENYLIST,
            DEFAULT_PII_DENYLIST,
            EventScrubber,
        )

        sentry_sdk.init(
            dsn=sentry_config["dsn"],
            environment=sentry_config.get("environment", "production"),
            integrations=[
                AsyncioIntegration(),
                LoggingIntegration(),
            ],
            event_scrubber=EventScrubber(
                denylist=[*DEFAULT_DENYLIST, "headers", "kwargs"],
                pii_denylist=[*DEFAULT_PII_DENYLIST, "headers", "kwargs"],
            ),
        )
        logger.success("Sentry SDK initialized")

    from discord.ui import View  # noqa: PLC0415

    if TYPE_CHECKING:
        from discord import Interaction  # noqa: PLC0415
        from discord.ui import Item  # noqa: PLC0415

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
