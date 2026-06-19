<!--
SPDX-License-Identifier: MIT
Copyright: 2024-2026 NiceBots.xyz
-->
# Deabbreviator Bot

A Discord bot that translates common internet abbreviations into their full meanings.

<img src="/examples/message_command_1.png" alt="Example of the Deabbreviator bot in action" width="500"/>

## Add to Your Server/Account

[Click here to add Deabbreviator to your server or account](https://nicebots.xyz/bots/deabbreviator/invite)

## Contributing Abbreviations

To add new abbreviations to the bot:

1. Fork the repository
2. Edit `/src/extensions/deabbreviator/main.py`
3. Add your abbreviations to the `ABBREVIATIONS` dictionary
4. Create a pull request

Example format:

```python
ABBREVIATIONS: Final = {
    "abc": "actual meaning here",
    # Add your abbreviations here
}
```

## About

This bot is maintained by [nicebots.xyz](https://nicebots.xyz) and is based on the
[botkit template](https://github.com/nicebots-xyz/botkit).
