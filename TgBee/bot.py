import asyncio
import aiohttp
import importlib
import os
import logging
from typing import List, Optional, Callable, Any, Dict
from .types import Update, User, Message, CallbackQuery
from .methods import Methods

logger = logging.getLogger(__name__)

class Client:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Client, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self, token: str = None, plugins_dir: str = None):
        self.token = token
        self.plugins_dir = plugins_dir
        self.handlers = []
        self.session = None
        self.me = None
        self.methods = Methods()
        if token:
            self.methods.set_token(token)
        if plugins_dir:
            self.load_plugins(plugins_dir)

    @classmethod
    def get_current(cls):
        return cls._instance

    def __getattr__(self, name):
        return getattr(self.methods, name)

    def on_message(self, filters=None):
        def decorator(func):
            handler = Handler(func, filters, update_type='message')
            self.handlers.append(handler)
            return func
        return decorator

    def on_update(self, update_type: str, filters=None):
        def decorator(func):
            handler = Handler(func, filters, update_type=update_type)
            self.handlers.append(handler)
            return func
        return decorator

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
        for handler in self.handlers:
            try:
                if handler.check(update):
                    await handler.handle(self, update)
            except Exception as e:
                logger.exception(f"Error in handler {handler}: {e}")

    async def _process_update_thread(self, update: Dict[str, Any]):
        try:
            update_obj = Update.from_dict(update)
            await self.process_update(update_obj)
        except Exception as e:
            logger.exception(f"Error processing update: {e}")

    async def start_polling(self):
        offset = 0
        max_retries = 5
        retry_delay = 5

        while True:
            for attempt in range(max_retries):
                try:
                    updates = await self.methods.get_updates(offset=offset, timeout=30)
                    for update in updates:
                        if isinstance(update, dict) and 'update_id' in update:
                            await self._process_update_thread(update)
                            offset = int(update['update_id']) + 1
                        else:
                            logger.warning(f"Received invalid update: {update}")
                    break  # If successful, break the retry loop
                except aiohttp.ClientError as e:
                    logger.error(f"Connection error while polling (attempt {attempt + 1}/{max_retries}): {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay)
                    else:
                        logger.error("Max retries reached. Restarting polling loop.")
                        await asyncio.sleep(retry_delay * 2)
                except Exception as e:
                    logger.exception(f"Error while polling: {e}")
                    await asyncio.sleep(retry_delay)

    async def initialize(self):
        if not self.token:
            raise ValueError("Bot token not set. Please provide a valid token when initializing the Client.")
        try:
            me_dict = await self.methods.get_me()
            self.me = User.from_dict(me_dict)
            logger.info(f"Bot initialized: @{self.me.username}")
        except Exception as e:
            logger.exception(f"Error initializing bot: {e}")
            raise

    async def run(self):
        try:
            await self.initialize()
            await self.start_polling()
        except Exception as e:
            logger.exception(f"Error running bot: {e}")

    def load_plugins(self, plugins_dir: str):
        if not os.path.exists(plugins_dir):
            logger.warning(f"Plugins directory '{plugins_dir}' not found.")
            return

        for root, dirs, files in os.walk(plugins_dir):
            for file in files:
                if file.endswith(".py") and not file.startswith("__"):
                    module_path = os.path.join(root, file)
                    module_name = os.path.splitext(os.path.relpath(module_path, os.getcwd()))[0].replace(os.path.sep, '.')
                    spec = importlib.util.spec_from_file_location(module_name, module_path)
                    module = importlib.util.module_from_spec(spec)
                    
                    # Set the bot instance in the module's global namespace
                    module.bot = self
                    module.get_file = self.methods.get_file_path
                    
                    spec.loader.exec_module(module)
                    logger.info(f"Loaded plugin: {module_name}")

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

bot = Client()