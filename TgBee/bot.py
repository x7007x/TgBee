import asyncio
import aiohttp
import importlib
import os
import json

from typing import List, Optional, Callable, Any, Dict
from .types import Update, User, Message, CallbackQuery
from .methods import Methods
from .filters import Filters

class SkipHandler(Exception):
    pass

class Bot(Methods):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Bot, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if not self.initialized:
            super().__init__()
            self.token = None
            self.handlers = []
            self.session = None
            self.me = None
            self.initialized = True

    @classmethod
    def get_current(cls):
        return cls._instance

    def set_token(self, token: str):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}/"

    def on_update(self, update_type: str, filters=None):
        def decorator(func):
            handler = Handler(func, filters, update_type=update_type)
            self.handlers.append(handler)
            return func
        return decorator

    on_message = lambda self, filters=None: self.on_update('message', filters)
    on_edited_message = lambda self, filters=None: self.on_update('edited_message', filters)
    on_channel_post = lambda self, filters=None: self.on_update('channel_post', filters)
    on_edited_channel_post = lambda self, filters=None: self.on_update('edited_channel_post', filters)
    on_inline_query = lambda self, filters=None: self.on_update('inline_query', filters)
    on_chosen_inline_result = lambda self, filters=None: self.on_update('chosen_inline_result', filters)
    on_callback_query = lambda self, filters=None: self.on_update('callback_query', filters)
    on_shipping_query = lambda self, filters=None: self.on_update('shipping_query', filters)
    on_pre_checkout_query = lambda self, filters=None: self.on_update('pre_checkout_query', filters)
    on_poll = lambda self, filters=None: self.on_update('poll', filters)
    on_poll_answer = lambda self, filters=None: self.on_update('poll_answer', filters)
    on_my_chat_member = lambda self, filters=None: self.on_update('my_chat_member', filters)
    on_chat_member = lambda self, filters=None: self.on_update('chat_member', filters)
    on_chat_join_request = lambda self, filters=None: self.on_update('chat_join_request', filters)

    async def process_update(self, update: Update):
        print(f"Received update: {update.to_json()}")
        for handler in self.handlers:
            try:
                if handler.check(update):
                    await handler.handle(self, update)
            except SkipHandler:
                print(f"Skipping rest of handler {handler}")
            except Exception as e:
                print(f"Error in handler {handler}: {e}")

    async def start_polling(self):
        offset = 0
        while True:
            try:
                updates = await self.get_updates(offset=offset, timeout=30)
                for update in updates:
                    update_obj = Update.from_dict(update)
                    asyncio.create_task(self.process_update(update_obj))
                    offset = update['update_id'] + 1
            except aiohttp.ClientError as e:
                print(f"Connection error while polling: {e}")
                await asyncio.sleep(5)
            except Exception as e:
                print(f"Error while polling: {e}")
                await asyncio.sleep(5)

    async def initialize(self):
        me_dict = await self.get_me()
        self.me = User.from_dict(me_dict)
        print(f"Bot initialized: @{self.me.username}")

    def run(self, plugins_dir: str = None):
        if plugins_dir:
            self.load_plugins(plugins_dir)
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.initialize())
            loop.run_until_complete(self.start_polling())
        except KeyboardInterrupt:
            pass
        finally:
            loop.close()

    def load_plugins(self, plugins_dir: str):
        if not os.path.exists(plugins_dir):
            print(f"Warning: Plugins directory '{plugins_dir}' not found.")
            return

        for filename in os.listdir(plugins_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]
                module = importlib.import_module(f"{plugins_dir}.{module_name}")
                for name, obj in module.__dict__.items():
                    if callable(obj) and hasattr(obj, "_handler"):
                        self.handlers.append(obj._handler)


class Handler:
    def __init__(self, callback: Callable, filters=None, update_type=None):
        self.callback = callback
        self.filters = filters
        self.update_type = update_type

    def check(self, update: Update) -> bool:
        if self.update_type:
            if not hasattr(update, self.update_type) or getattr(update, self.update_type) is None:
                return False
        if self.filters:
            return self.filters(update)
        return True

    async def handle(self, bot, update: Update):
        await self.callback(bot, getattr(update, self.update_type))

class BotException(Exception):
    pass

