# Copyright (c) NiceBots all rights reserved
from collections import defaultdict
from functools import cached_property
from typing import Any, Final, final, override

import discord
from discord.ext import commands
from discord.ext import pages as paginator

from src import custom
from src.extensions.help.pages.classes import (
    HelpCategoryTranslation,
)
from src.i18n.classes import RawTranslation, TranslationWrapper, apply_locale

from .pages import help_translation


def get_gradient_color(shade_index: int, color_index: int, max_shade: int = 50, max_color: int = 10) -> int:
    """Generate a color from a two-dimensional gradient system using bright pastel colors.

    Args:
    ----
        shade_index (int): Index for shade selection (0 to max_shade)
        color_index (int): Index for base color selection (0 to max_color)
        max_shade (int): Maximum value for shade_index (default 50)
        max_color (int): Maximum value for color_index (default 10)

    Returns:
    -------
        int: Color as a 24-bit integer

    """
    # Normalize indices to 0-1 range
    shade_factor = max(0, min(1, shade_index / max_shade))
    color_factor = max(0, min(1, color_index / max_color))

    # Bright pastel base colors
    base_colors = [
        (179, 229, 252),  # Bright light blue
        (225, 190, 231),  # Bright lilac
        (255, 209, 220),  # Bright pink
        (255, 224, 178),  # Bright peach
        (255, 255, 198),  # Bright yellow
        (200, 230, 201),  # Bright mint
        (178, 255, 255),  # Bright turquoise
        (187, 222, 251),  # Bright baby blue
        (225, 190, 231),  # Bright lavender
        (255, 236, 179),  # Bright cream
        (200, 230, 255),  # Bright sky blue
    ]

    # Interpolate between colors based on color_factor
    color_index_float = color_factor * (len(base_colors) - 1)
    color_index_low = int(color_index_float)
    color_index_high = min(color_index_low + 1, len(base_colors) - 1)
    color_blend = color_index_float - color_index_low

    c1 = base_colors[color_index_low]
    c2 = base_colors[color_index_high]

    # Interpolate between the two closest base colors
    base_color = tuple(int(c1[i] * (1 - color_blend) + c2[i] * color_blend) for i in range(3))

    # Modified shading approach for brighter colors
    if shade_factor < 0.5:
        # Darker shades: interpolate towards a very light gray instead of black
        shade_factor_adjusted = shade_factor * 2
        # Increase minimum brightness (was 120, now 180)
        darker_tone = tuple(max(c * 0.8, 180) for c in base_color)
        final_color = tuple(
            int(darker_tone[i] + (base_color[i] - darker_tone[i]) * shade_factor_adjusted) for i in range(3)
        )
    else:
        # Lighter shades: interpolate towards white
        shade_factor_adjusted = (shade_factor - 0.5) * 2
        final_color = tuple(
            int(base_color[i] * (1 - shade_factor_adjusted) + 255 * shade_factor_adjusted) for i in range(3)
        )

    # Convert to 24-bit integer
    return (final_color[0] << 16) | (final_color[1] << 8) | final_color[2]


class PageIndicatorButton(paginator.PaginatorButton):
    def __init__(self) -> None:
        super().__init__(button_type="page_indicator", disabled=True, label="", style=discord.ButtonStyle.gray)


@final
class HelpView(paginator.Paginator):
    def __init__(
        self,
        embeds: dict[str, list[discord.Embed]],
        ui_translations: TranslationWrapper[dict[str, RawTranslation]],
        bot: custom.Bot,
    ) -> None:
        self.bot = bot

        the_pages: list[paginator.PageGroup] = [
            paginator.PageGroup(
                [paginator.Page(embeds=[embed]) for embed in data[1]],
                label=data[0],
                default=i == 0,
            )
            for i, data in enumerate(embeds.items())
        ]

        self.embeds = embeds
        self.ui_translations = ui_translations
        self.page_indicator = PageIndicatorButton()
        super().__init__(
            the_pages,
            show_menu=True,
            menu_placeholder=ui_translations.select_category,
            custom_buttons=[
                paginator.PaginatorButton("first", emoji="⏮️", style=discord.ButtonStyle.blurple),
                paginator.PaginatorButton("prev", emoji="◀️", style=discord.ButtonStyle.red),
                self.page_indicator,
                paginator.PaginatorButton("next", emoji="▶️", style=discord.ButtonStyle.green),
                paginator.PaginatorButton("last", emoji="⏭️", style=discord.ButtonStyle.blurple),
            ],
            use_default_buttons=False,
        )

    @override
    def update_buttons(self) -> dict:  # pyright: ignore [reportMissingTypeArgument, reportUnknownParameterType]
        r = super().update_buttons()  # pyright: ignore [reportUnknownVariableType]
        if self.show_indicator:
            self.buttons["page_indicator"]["object"].label = self.ui_translations.page_indicator.format(
                current=self.current_page + 1, total=self.page_count + 1
            )
        return r  # pyright: ignore [reportUnknownVariableType]


def get_categories_embeds(
    ui_translations: TranslationWrapper[dict[str, RawTranslation]],
    categories: dict[str, TranslationWrapper[HelpCategoryTranslation]],
    bot: custom.Bot,
) -> dict[str, list[discord.Embed]]:
    embeds: defaultdict[str, list[discord.Embed]] = defaultdict(list)
    for i, category in enumerate(categories):
        for j, page in enumerate(category.pages.values()):  # pyright: ignore [reportUnknownArgumentType, reportUnknownVariableType, reportAttributeAccessIssue]
            embed = discord.Embed(
                title=f"{category.name} - {page.title}",  # pyright: ignore [reportAttributeAccessIssue]
                description=page.description,  # pyright: ignore [reportUnknownArgumentType]
                color=discord.Color(get_gradient_color(i, j)),
            )
            if page.quick_tips:
                embed.add_field(name=ui_translations.quick_tips_title, value="- " + "\n- ".join(page.quick_tips))  # pyright: ignore [reportUnknownArgumentType]
            if page.examples:
                embed.add_field(name=ui_translations.examples_title, value="- " + "\n- ".join(page.examples))  # pyright: ignore [reportUnknownArgumentType]
            if page.related_commands:
                embed.add_field(
                    name=ui_translations.related_commands_title,
                    value="- "
                    + "\n- ".join(bot.get_application_command(name).mention for name in page.related_commands),  # pyright: ignore [reportUnknownArgumentType, reportUnknownVariableType, reportAttributeAccessIssue, reportOptionalMemberAccess]
                )
            embeds[category.name].append(embed)  # pyright: ignore [reportAttributeAccessIssue]
    return dict(embeds)


@final
class Help(commands.Cog):
    def __init__(self, bot: custom.Bot, ui_translations: dict[str, RawTranslation], locales: set[str]) -> None:
        self.bot = bot
        self.ui_translations = ui_translations
        self.locales = locales

    @cached_property
    async def embeds(self) -> dict[str, dict[str, list[discord.Embed]]]:
        embeds: defaultdict[str, dict[str, list[discord.Embed]]] = defaultdict(dict)
        for locale in self.locales:
            t = help_translation.get_for_locale(locale)
            ui = apply_locale(self.ui_translations, locale)
            embeds[locale] = get_categories_embeds(ui, t.categories, self.bot)
        return dict(embeds)

    @discord.slash_command(
        name="help",
        integration_types={discord.IntegrationType.user_install, discord.IntegrationType.guild_install},
        contexts={
            discord.InteractionContextType.guild,
            discord.InteractionContextType.private_channel,
            discord.InteractionContextType.bot_dm,
        },
    )
    async def help_slash(self, ctx: custom.ApplicationContext) -> None:
        paginator = HelpView(
            embeds=self.embeds[ctx.locale],
            ui_translations=apply_locale(self.ui_translations, ctx.locale),
            bot=self.bot,
        )
        await paginator.respond(ctx.interaction, ephemeral=True)


def setup(bot: custom.Bot, config: dict[str, Any]) -> None:  # pyright: ignore [reportExplicitAny]
    bot.add_cog(Help(bot, config["translations"], set(config["locales"])))


default: Final = {"enabled": False}
__all__ = ["default", "setup"]
