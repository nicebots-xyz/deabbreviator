# Copyright (c) NiceBots all rights reserved - refer to LICENSE file in the root

import re
from functools import cached_property
from typing import Any, Final, cast, final

import discord
from discord.ext import commands

from src import custom
from src.utils.cooldown import BucketType, cooldown

default: Final = {"enabled": True}


@final
class Deabbreviator(commands.Cog):
    ABBREVIATIONS: Final = {
        "ngl": "not gonna lie",
        "nvm": "nevermind",
        "idk": "I don't know",
        "brb": "be right back",
        "btw": "by the way",
        "ty": "thank you",
        "thy": "thank you",
        "tx": "thanks",
        "thx": "thanks",
        "yw": "you're welcome",
        "asap": "as soon as possible",
        "fyi": "for your information",
        "np": "no problem",
        "omw": "on my way",
        "lmk": "let me know",
        "afaik": "as far as I know",
        "nafaik": "not as far as I know",
        "b4": "before",
        "bc": "because",
        "td": "today",
        "tmr": "tomorrow",
        "tmrw": "tomorrow",
        "tmoro": "tomorrow",
        "yd": "yesterday",
        "msg": "message",
        "abt": "about",
        "dm": "direct message",
        "pm": "private message",
        "irl": "in real life",
        "imo": "in my opinion",
        "smh": "shaking my head",
        "sm": "so much",
        "lol": "laughing out loud",
        "rofl": "rolling on the floor laughing",
        "grl": "girl",
        "ur": "you're",
        "qt": "cutie",
        "fr": "for real",
        "gf": "girlfriend",
        "bf": "boyfriend",
        "rn": "right now",
        "l8r": "later",
        "wtf": "what the f***",
        "omg": "oh my god",
        "ily": "I love you",
        "ily2": "I love you too",
        "ilym": "I love you more",
        "ilyt": "I love you too",
        "afk": "away from keyboard",
        "bbl": "be back later",
        "bbs": "be back soon",
        "g2g": "got to go",
        "gtg": "got to go",
        "dms": "direct messages",
        "pls": "please",
        "u": "you",
        "bst": "bestie",
        "gae": "good at everything",
        "dw": "don't worry",
        "dwab": "don't worry about it",
        "fs": "for sure",
        "stfu": "shut the f*** up",
        "ong": "oh my god",
        "eg": "example",
        "aka": "also known as",
        "tldr": "too long didn't read",
        "tmi": "too much information",
        "ttyl": "talk to you later",
        "tysm": "thank you so much",
        "wbu": "what about you",
        "wfh": "work from home",
        "wym": "what do you mean",
        "wyd": "what you doing",
        "wya": "where you at",
        "u2": "you too",
        "wb": "welcome back",
        "gn": "good night",
        "gm": "good morning",
        "gd": "good",
        "gj": "good job",
        "gg": "good game",
        "gl": "good luck",
        "ilysm": "I love you so much",
        "k": "okay",
        "kk": "okay",
        "ok": "okay",
        "pfp": "profile picture",
        "fu": "f*** you",
        "fml": "f*** my life",
        "ffs": "for f***'s sake",
        "fgs": "for god's sake",
        "smth": "something",
        "idw": "it doesn't work",
        "idc": "I don't care",
        "nbd": "no big deal",
        "nfs": "not for sale",
        "lgtm": "looks good to me",
        "lmao": "laughing my a** off",
        "l8": "late",
        "sys": "see you soon",
        "sry": "sorry",
        "ss": "screenshot",
        "bff": "best friend forever",
        "sya": "see you again",
        "sup": "what's up",
        "bro": "brother",
    }

    def __init__(self, bot: custom.Bot) -> None:
        self.bot = bot

    def replace_match(self, match: re.Match[str]) -> str:
        original_word = match.group()
        translated_word = self.ABBREVIATIONS[original_word.lower()]
        if original_word.isupper():
            return translated_word.upper()
        if original_word[0].isupper():
            return translated_word.capitalize()
        return translated_word

    def translate_string(self, text: str) -> str:
        return self.translation_pattern.sub(self.replace_match, text)

    @cached_property
    def translation_pattern(self) -> re.Pattern[str]:
        # Escape each word to handle regex special characters and sort by descending length
        escaped_words = [re.escape(word) for word in self.ABBREVIATIONS]
        escaped_words.sort(key=lambda x: len(x), reverse=True)
        # Create the regex pattern to match word boundaries and include word breaks
        pattern = r"\b(" + "|".join(escaped_words) + r")\b"
        return re.compile(pattern, flags=re.IGNORECASE)

    async def async_translate_string(self, text: str) -> str:
        t: Any = None  # pyright: ignore[reportExplicitAny]
        if t := await self.bot.botkit_cache.get(text, namespace="deabbreviator"):
            return cast(str, t)
        t = self.translate_string(text)
        await self.bot.botkit_cache.set(text, t, namespace="deabbreviator", ttl=60 * 60)
        return cast(str, t)

    @discord.message_command(  # pyright: ignore[reportUntypedFunctionDecorator]
        name="Deabbreviate message",
        integration_types={discord.IntegrationType.guild_install, discord.IntegrationType.user_install},
        contexts={
            discord.InteractionContextType.guild,
            discord.InteractionContextType.bot_dm,
            discord.InteractionContextType.private_channel,
        },
    )
    @cooldown(key="deabbreviate_message", limit=1, per=5, bucket_type=BucketType.USER)
    async def deabbreviate_message(self, ctx: custom.ApplicationContext, message: discord.Message) -> None:
        a: str = await self.async_translate_string(message.content)
        if a == message.content:
            await ctx.respond(ctx.translations.no_abbreviations)
            return
        await ctx.respond(
            ctx.translations.success.format(message=a, user=message.author.display_name, message_link=message.jump_url)
        )

    @discord.slash_command(  # pyright: ignore[reportUntypedFunctionDecorator]
        name="deabbreviate",
        integration_types={discord.IntegrationType.guild_install, discord.IntegrationType.user_install},
        contexts={
            discord.InteractionContextType.guild,
            discord.InteractionContextType.bot_dm,
            discord.InteractionContextType.private_channel,
        },
    )
    @cooldown(key="deabbreviate", limit=1, per=5, bucket_type=BucketType.USER)
    async def deabbreviate(self, ctx: custom.ApplicationContext, text: str) -> None:
        a: str = await self.async_translate_string(text)
        if a == text:
            await ctx.respond(ctx.translations.no_abbreviations)
            return
        await ctx.respond(a)  # slash commands do not have an original message to reference


def setup(bot: custom.Bot) -> None:
    bot.add_cog(Deabbreviator(bot))
