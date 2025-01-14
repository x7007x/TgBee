# TgBee

TgBee is an asynchronous Python wrapper for the Telegram Bot API. It provides a simple and intuitive interface for creating Telegram bots using modern Python features.

## Features

- Asynchronous API calls using `aiohttp`
- Easy-to-use decorator-based handler system
- Support for inline keyboards and callback queries
- Plugin system for modular bot development
- FastAPI integration for webhook support

## Installation

You can install TgBee using pip: 
```bash
pip3 install TgBee
```

## Example

```python
import asyncio
from TgBee import Client, filters

bot = Client(
    bot_token = "YOUR_BOT_TOKEN",
    plugins_dir = "source/plugins"
)

@bot.on_message(filters.command("start"))
async def start_command(client, message):
    reply_markup = {
        "inline_keyboard": [
            [
                {"text": "Button 1", "callback_data": "button1"},
                {"text": "Button 2", "callback_data": "button2"}
            ]
        ]
    }

    mention = message.from_user.mention
    sent_message = await client.send_message(
        chat_id=message.chat.id,
        text=f"Welcome {mention} to the bot! Here's a message with some buttons:",
        parse_mode="HTML",
        reply_markup=reply_markup
    )

if __name__ == "__main__":
    asyncio.run(main())

```
