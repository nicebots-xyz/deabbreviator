# Copyright (c) NiceBots all rights reserved - refer to LICENSE file in the root

# ruff: noqa: S101
import pytest

from src import custom
from src.extensions.deabbreviator.main import Deabbreviator


@pytest.fixture
def deabbreviator() -> Deabbreviator:
    return Deabbreviator(custom.Bot())


def test_all_keys(deabbreviator: Deabbreviator) -> None:
    """Test all the keys that are present in the abbreviation dictionary."""
    for key, value in deabbreviator.ABBREVIATIONS.items():
        assert deabbreviator.translate_string(key) == value
        assert deabbreviator.translate_string(key.upper()) == value.upper()
        if key.upper() != key.capitalize():
            assert deabbreviator.translate_string(key.capitalize()) == value.capitalize()


def test_basic_abbreviations(deabbreviator: Deabbreviator) -> None:
    """Test basic abbreviation expansion."""
    assert deabbreviator.translate_string("btw") == "by the way"
    assert deabbreviator.translate_string("asap") == "as soon as possible"
    assert deabbreviator.translate_string("fyi") == "for your information"


def test_case_sensitivity(deabbreviator: Deabbreviator) -> None:
    """Test case sensitivity handling."""
    assert deabbreviator.translate_string("BTW") == "BY THE WAY"
    assert deabbreviator.translate_string("Btw") == "By the way"
    assert deabbreviator.translate_string("bTw") == "by the way"


def test_punctuation(deabbreviator: Deabbreviator) -> None:
    """Test handling of punctuation around abbreviations."""
    assert deabbreviator.translate_string("Hello, btw!") == "Hello, by the way!"
    assert deabbreviator.translate_string("(btw)") == "(by the way)"
    assert deabbreviator.translate_string("btw...") == "by the way..."
    assert deabbreviator.translate_string("...btw") == "...by the way"


def test_multiple_abbreviations(deabbreviator: Deabbreviator) -> None:
    """Test handling multiple abbreviations in one text."""
    assert deabbreviator.translate_string("btw idk what happened") == "by the way I don't know what happened"
    assert deabbreviator.translate_string("fyi asap!") == "for your information as soon as possible!"


def test_mixed_text(deabbreviator: Deabbreviator) -> None:
    """Test mixed normal text and abbreviations."""
    assert (
        deabbreviator.translate_string("Hey there! btw, I'll be late idk maybe 30min?")
        == "Hey there! by the way, I'll be late I don't know maybe 30min?"
    )


def test_special_characters(deabbreviator: Deabbreviator) -> None:
    """Test handling of special characters and unicode."""
    assert deabbreviator.translate_string("btw → idk") == "by the way → I don't know"
    assert deabbreviator.translate_string("¿btw?") == "¿by the way?"
    assert deabbreviator.translate_string("btw: ümlaut") == "by the way: ümlaut"


def test_no_abbreviations(deabbreviator: Deabbreviator) -> None:
    """Test text without any abbreviations."""
    original = "This is a normal sentence without abbreviations."
    assert deabbreviator.translate_string(original) == original


def test_edge_cases(deabbreviator: Deabbreviator) -> None:
    """Test edge cases."""
    assert deabbreviator.translate_string("") == ""
    assert deabbreviator.translate_string(" btw ") == " by the way "
    assert deabbreviator.translate_string("btw.btw") == "by the way.by the way"


if __name__ == "__main__":
    pytest.main([__file__])
