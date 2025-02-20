# Deabbreviator Bot

A Discord bot that translates common internet abbreviations into their full meanings.

>[!WARNING]
>This Discord bot is subject to special licensing terms. Please read the full NiceBots Discord Bot License Agreement Version 1.0 for complete details.

>[!IMPORTANT]
>**Key License Points:**
>- Personal or internal business use only
>- No commercial or economic gain (including donations)
>- All modifications must be publicly shared
>- Clear attribution required
>- Contributions grant full rights to NiceBots.xyz
>- License termination upon legal dispute
>- No use of NiceBots.xyz trademarks

>[!NOTE]
>This summary is not legally binding. Refer to the full license text for all terms and conditions.

## Add to Your Server/Account

[Click here to add Deabbreviator to your server or account](https://discord.com/oauth2/authorize?client_id=1342236118212673537)

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

This bot is maintained by [nicebots.xyz](https://nicebots.xyz) and is based on the [botkit template](https://github.com/nicebots-xyz/botkit).

Note: By using, modifying, or distributing this bot, you agree to the terms of the NiceBots Discord Bot License Agreement Version 1.0.
