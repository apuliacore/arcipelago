# Arcipelago
A moderated event platform for Telegram.

## How it works
This software powers a virtual event wall on Telegram.
Through the Telegram bot, users can propose events to a group of admins who can accept or reject publication.
Events are published on a public channel, where subscribed users also receive reminders about daily events.
Optionally, events can be published on a shared Google Calendar.

## Setup

Follow these steps if you want to run a new instance of the bot.
In order to run the instance, you will need to create a new bot via [BotFather](https://telegram.me/BotFather), as well as a channel (i.e., the public event wall) and a group for admins.
You will need to add the bot token and the chat IDs for the public channel and the admin group in the config file.

Currently, the installation process has only been tested on Ubuntu Linux 20.04.3 LTS.

### Ubuntu Linux
1. This project is packaged using Poetry: install it following the steps described in the [official website](https://python-poetry.org/docs/#installation)
2. `git clone` this repository on your machine
3. `cd arcipelago` and `poetry install`
4. Edit `arcipelago/config.py` with your information
5. `poetry run arcipelago:init-db`
6. `nohup poetry run arcipelago:run &` to run the bot in background

## Contributing
If you want to contribute to the project you can understand more of how it works [reading the wiki](https://github.com/apuliacore/arcipelago/wiki/Arcipelago-Wiki).
Then you can have a look at [open issues](https://github.com/apuliacore/arcipelago/issues).

## Instances
This software powers the following Telegram events channels:
- [Apuliacore](https://t.me/apuliacore) | Puglia, IT

## Support
If this software is useful for you or you would simply like to show us your support, you could [buy us a coffee](https://ko-fi.com/apuliacore) 😊
