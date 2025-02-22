# Copyright (c) NiceBots.xyz
# SPDX-License-Identifier: MIT

from abc import ABC, abstractmethod

import nodriver as uc
from bs4 import BeautifulSoup


class BaseError(Exception):
    pass


class NotFoundError(BaseError):
    pass


def normalize_soup(soup: BeautifulSoup) -> str:
    """Normalize the text from a BeautifulSoup object."""
    return soup.get_text().strip().replace("’", "'").replace("\n", "")  # noqa: RUF001


class Listing(ABC):
    """Represents a Discord Bot listing website."""

    def __init__(self, browser: uc.Browser) -> None:
        self.browser = browser

    def normalize_soup(self, soup: BeautifulSoup) -> str:
        """Normalize the text from a BeautifulSoup object."""
        return normalize_soup(soup)

    @abstractmethod
    async def fetch_raw_description(self) -> str:
        """Fetch the raw description of the bot from the website.

        :raises NotFoundError: If the bot is not found
        :return: The raw description of the bot
        """
