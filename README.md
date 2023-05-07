# Arcipelago
A moderated event platform for Telegram.

## Setup

### Linux
1. This project is packaged using Poetry: install it following the steps described in the [official website](https://python-poetry.org/docs/#installation)
2. `git clone` this repository on your machine
3. `cd arcipelago` and `poetry install`
4. Edit `arcipelago/config.py` with your information
5. `poetry run arcipelago:init-db`
6. `poetry run arcipelago:run`

## How it works
This software powers a virtual event wall on Telegram.
Through the Telegram bot, users can propose events to a group of admins who can accept or reject publication.
Events are published on a public channel, where subscribed users also receive reminders about daily events.
Optionally, events can be published on a shared Google Calendar.

## Instances
This software powers the following Telegram events channels:
- [Apuliacore](https://t.me/apuliacore) | Puglia, IT

## Support
If this software is useful for you or you would simply like to show us your support, you could [buy us a coffee](https://ko-fi.com/apuliacore) 😊
