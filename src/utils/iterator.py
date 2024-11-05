# Copyright (c) NiceBots.xyz
# SPDX-License-Identifier: MIT

from collections.abc import Iterator
from typing import TypeVar

T = TypeVar("T")
V = TypeVar("V")


def next_default(iterator: Iterator[T], default: V = None) -> T | V:
    try:
        return next(iterator)
    except StopIteration:
        return default
