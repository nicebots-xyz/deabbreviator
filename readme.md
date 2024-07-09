# Botkit: A Framework for Building Discord Bots with py-cord

## What is Botkit?

Botkit is a framework for building Discord bots.
It is designed to simplify the process of creating and managing Discord bots,
by providing a modular architecture and a set of useful tools and utilities
so that you can focus on building your bot's functionality.
We use it ourselves to build our own bots, and we hope you find it useful too!

## What Botkit is NOT

Botkit is not a pre-built Discord bot. Instead, it is a starting point for building your own custom Discord bot. You’re expected to edit and modify the provided code to suit your specific requirements.

## Features

- **Modular Design**: The bot is designed with a modular architecture, allowing you to easily enable or disable specific extensions or features.
- **Extensible**: The bot is built around the extensions located in the `src/extensions` directory. There you can find useful and example extensions to get you started.
- **Configurable**: The bot's configuration, including enabled extensions and bot token, is managed through a `config.yml` file.
- **Easy Setup**: Botkit simplifies the setup process by providing a well-structured project template and configuration management.
- **Integrated Backend**: Botkit provides an easy way of having a Quart (flask-like) webserver running alongside your bot, with the ability to add routes and endpoints.
- **Useful Scripts**: Botkit includes useful scripts for managing your bot's listing on top.gg and other bot lists, such as discord's app directory. 

## Requirements

- [pdm](https://pdm-project.org/en/latest/) - A modern Python packaging and dependency management tool.
- Python 3.11
- A Discord bot. You can create a new bot and get a token from the [Discord Developer Portal](https://discord.com/developers/applications).

## Installation

1. Clone the repository and navigate to the project directory.
2. Install the required dependencies using `pdm`:

```
pdm install
```

## Getting Started
When creating your own features, you’re supposed to create a new extension in the `src/extensions` directory for each feature you want to add.
You can use the provided extensions as a reference to get started, and follow the guidelines provided in the [Creating Extensions](#creating-extensions) section.

## Setup

### Automatic Extensions Configuration
Every extension in the `src/extensions` directory will automatically be loaded,
and if its default config is set to `enabled: true`, it will be enabled by default.
This allows you to add an extension that you found online simply by adding the file to the `src/extensions` directory.
The settings are automatically added to the `config.yml` file if you didn't provide them, after running the bot.

### Yaml Configuration
You can set up the `config.yml` file with your bot token and desired extensions. There, or trough environment variables, you can enable or disable extensions, set up the bot token, and configure other options.
You’re required to at least provide the bot token. Here's an example configuration:

```yaml
extensions:
  topgg:
    enabled: false
    token: "your_top.gg_token"
  ping:
    enabled: true
bot:
  token: "your_bot_token"
logging:
  level: INFO
```

### Environment Variables
Alternatively, you can set the bot token and other configuration options using environment variables. You can set any variable as you would in the `config.yml` file, but with the `BOTKIT__` prefix, and `__` to separate nested keys. To set lists, use regular json syntax.
```env
BOTKIT__bot__token=your_bot_token
BOTKIT__extensions__topgg__enabled=false
BOTKIT__extensions__topgg__token=your_top.gg_token
BOTKIT__extensions__ping__enabled=true
BOTKIT__logging__level=INFO
```

## Creating Extensions

Extensions are in truth just python located in the `src/extensions` directory.
When creating an extension, it is crucial to follow the following guidelines:
- You should keep only one feature per extension.
- Creating multiple files and submodules is allowed.
- Use the provided `logger` (`from src.logging import logger`) for logging messages.
  - You have five log levels available: `DEBUG`, `INFO`, `WARNING`, `ERROR`, and `CRITICAL`, use them accordingly.

Moreover, each extension is required to export different objects and functions to work properly. These are:
- `setup`: A function that sets up the extension. It CAN accept any of the following arguments, in the order you prefer, and you can safely omit any of them if you don't need them:
  - `bot`: The Discord bot instance.
  - `config`: The configuration dictionary for the extension. All config keys will always be lowercased for compatibility with environment variables.


- `setup_webserver`: A function for adding webserver routes. It CAN accept any of the following arguments, in the order you prefer, and you can safely omit any of them if you don't need them:
  - `app`: The Quart app instance.
  - `bot`: The Discord bot instance.
  - `config`: The configuration dictionary for the extension.

> [!NOTE]
> Either `setup` or `setup_webserver` is required for the extension to work properly. You can also provide both.

- `on_startup` (optional): An asynchronous function that is called when the bot starts. It CAN accept any of the following arguments, in the order you prefer, and you can safely omit any of them if you don't need them:
  - `app`: The Quart app instance.
  - `bot`: The Discord bot instance. :warning: The bot is not yet logged in, so you won't be able to send messages or interact with the Discord API.
  - `config`: The configuration dictionary for the extension.


- `default`: A dictionary containing the default configuration for the extension. This is used to populate the `config.yml` file with the default values if they aren’t already present. It is required to have AT MINIMAL the `enabled` key set to `False` or `True` (you generally want to prefer `True` for a more intuitive experience to new users, but it is not required, especially if you code just for yourself).
- `schema`: A dictionary (or a `schema.Schema`, if you want more granular control) containing the schema for the extension's configuration. This is used to validate the configuration in the `config.yml` file. The schema should be a dictionary where the keys are the configuration keys, and the values are the types of the values. For example:
```python
schema = {
    "enabled": bool,
    "token": str,
    "prefix": str,
    "channel": int,
    "role": int,
    "users": list,
    "options": dict,
}
```
We really encourage you to follow these instructions, even if you’re coding privately, as it will make your code more readable and maintainable in the long run.

## Using scripts

### `check-listings`
This script checks the publishing status of your bot on various bot listing websites, as well as if its description is up to date with one provided.
To use it:

0. Have Google Chrome installed. This is required web scraping.
1. Install the development dependencies using `pdm install -d`.
2. Create a file called `description.md` in the root directory of the project, containing your bot's description.
3. Create a file called `listings.yml` in the root directory of the project, containing your bot's application id and url for *some* listing websites, if you want to check them. Here's an example:
```yaml
application_id: 1234567891011121314

DiscordBotListCom: # add this section if you want to check discordbotlist.com
  url: https://discordbotlist.com/bots/my-bot

DisforgeCom: # add this section if you want to check disforge.com
  url: https://disforge.com/bot/1234-my-bot

DiscordMe: # add this section if you want to check discord.me
  url: https://discord.me/my-bot`
```
4. Run the script using `pdm run check-listings`.

## Provided Extensions
We provide multiple extensions directly within this project to get you started. These are:

- [`ping`](src/extensions/ping/readme.md): A simple ping command and an http endpoint to test whether the bot is online.
- [`topgg`](src/extensions/topgg/readme.md): An extension to post server count to [top.gg](https://top.gg/).
- [`branding`](src/extensions/branding/readme.md): An extension to customize the bot's presence and status, and embed aesthetics.
- [`add-dm`](src/extensions/add-dm/readme.md): An extension to send a direct message to the user who adds the bot to a guild.
- [`nice-errors`](src/extensions/nice-errors/readme.md): An extension to provide user-friendly error messages during command execution.

Read the provided documentation for each extension to learn more about their features and how to configure them.

## Contributing

We welcome contributions to this project! Please follow the [gitmoji.dev](https://gitmoji.dev) convention for commit messages and submit pull requests with descriptive commit messages.

## Built With

- Love :yellow_heart:
- [py-cord](https://github.com/Pycord-Development/pycord)
- [Quart](https://github.com/pallets/quart/)
- [pdm](https://pdm-project.org/en/latest/)

## Code Style and Linting

This project follows the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide for Python code. We recommend using a linter like [black](https://github.com/psf/black) to ensure your code adheres to the style guidelines.
We provide a command to lint the code using `pdm run lint`. For this to work you have to install the development dependencies using `pdm install -d` if you haven't already.

## Deployment

Botkit is designed to be deployed on various platforms, including cloud services like [Heroku](https://www.heroku.com/) or [DigitalOcean](https://www.digitalocean.com/). Refer to the documentation of your preferred hosting platform for deployment instructions.
A `Dockerfile` is included in the project for containerized deployments, as well as a GitHub action including tests and linting.
You can export the requirements to a `requirements.txt` file using `pdm run export`, run the tests using `pdm run tests` and lint the code using `pdm run lint`.
In order for the GitHub tests to pass, you need to make sure you linted your code, that the tests pass and that you exported the requirements if you made changes to the dependencies.

## Support and Resources

If you encounter any issues or have questions about Botkit, feel free to open an issue on the [GitHub repository](https://github.com/nicebots-xyz/botkit). You can also join the [official Discord server](https://paill.at/OjTuQ) for support and discussions.

## License

This project is licensed under the [MIT License](LICENSE).
