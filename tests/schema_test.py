# Copyright (c) NiceBots.xyz
# SPDX-License-Identifier: MIT

import importlib
from glob import iglob
from os.path import basename, splitext

from src.utils import validate_module


def test_ext_schemas() -> None:
    """Test the schemas of all extensions."""
    for ext in iglob("src/extensions/*"):
        name = splitext(basename(ext))[0]
        if name.endswith(("_", "_/", ".py")):
            continue
        module = importlib.import_module(f"src.extensions.{name}")
        validate_module(module)
        del module


if __name__ == "__main__":
    test_ext_schemas()
