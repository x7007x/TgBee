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
pip3 install -U TgBee
```

## Example

```python
import asyncio
from TgBee import Client, filters

bot = Client(token="YOUR_BOT_TOKEN")

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

@bot.on_callback_query()
async def handle_callback(client, callback_query):
    callback_query_id = callback_query.id
    data = callback_query.data

    if data == "button1":
        await client.answer_callback_query(callback_query_id=callback_query_id, text="You pressed Button 1!", show_alert=True)
    elif data == "button2":
        await client.answer_callback_query(callback_query_id=callback_query_id, text="You pressed Button 2!", show_alert=True)
    else:
        await client.answer_callback_query(callback_query_id=callback_query_id, text="Unknown button pressed", show_alert=True)

async def main():
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())
```
