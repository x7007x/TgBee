import asyncio
import aiohttp
import importlib
import os
import logging
import json
import time
from typing import List, Optional, Callable, Any, Dict, Union
from .types import Update, User, Message, CallbackQuery
from .methods import Methods
from aiohttp import web

logger = logging.getLogger(__name__)

class Client:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Client, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self, token: str = None, plugins_dir: str = None):
        if hasattr(self, 'initialized') and self.initialized:
            return
            
        self.token = token
        self.plugins_dir = plugins_dir
        self.handlers = []
        self.session = None
        self.me = None
        self.methods = Methods()
        self.webhook_app = None
        self.webhook_url = None
        self.webhook_path = None
        self.webhook_port = None
        self.processing = False
        self.max_connections = 100
        self.update_queue = asyncio.Queue()
        self.worker_tasks = []
        self.worker_count = 10  # Default number of workers
        self.last_request_time = 0
        self.request_interval = 0.05  # Minimum interval between API requests (50ms)
        self.rate_limiter = asyncio.Semaphore(30)  # Rate limiting for Telegram API
        
        if self.token:
            self.set_token(self.token)
        if self.plugins_dir:
            self.load_plugins(self.plugins_dir)
        self.initialized = True

    def set_token(self, token: str):
        self.token = token
        self.methods.set_token(token)
        logger.info("Bot token set successfully")

    @classmethod
    def get_current(cls):
        return cls._instance

    def __getattr__(self, name):
        return getattr(self.methods, name)

    def set_worker_count(self, count: int):
        """Set the number of concurrent update processing workers"""
        self.worker_count = max(1, count)
        logger.info(f"Set worker count to {self.worker_count}")
        return self

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

    # Lambda shortcuts for different update types
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

    async def _rate_limited_api_call(self, coro):
        """Execute API calls with rate limiting to avoid Telegram's limits"""
        async with self.rate_limiter:
            # Ensure minimum interval between API requests
            now = time.time()
            since_last = now - self.last_request_time
            if since_last < self.request_interval:
                await asyncio.sleep(self.request_interval - since_last)
            
            result = await coro
            self.last_request_time = time.time()
            return result

    async def process_update(self, update: Update):
        """Process a single update through all matching handlers"""
        matched_handlers = []
        
        # First collect all matching handlers
        for handler in self.handlers:
            if handler.check(update):
                matched_handlers.append(handler)
        
        # Then execute them concurrently
        if matched_handlers:
            await asyncio.gather(
                *(handler.handle(self, update) for handler in matched_handlers)
            )

    async def _update_worker(self):
        """Worker to process updates from the queue"""
        while True:
            try:
                update = await self.update_queue.get()
                update_obj = Update.from_dict(update) if isinstance(update, dict) else update
                
                try:
                    await self.process_update(update_obj)
                except Exception as e:
                    logger.exception(f"Error processing update: {e}")
                
                self.update_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.exception(f"Error in update worker: {e}")

    async def _queue_update(self, update: Union[Dict[str, Any], Update]):
        """Add update to the processing queue"""
        await self.update_queue.put(update)

    async def start_workers(self):
        """Start update processing workers"""
        self.worker_tasks = []
        for _ in range(self.worker_count):
            task = asyncio.create_task(self._update_worker())
            self.worker_tasks.append(task)
        logger.info(f"Started {self.worker_count} update processing workers")

    async def stop_workers(self):
        """Stop all update processing workers"""
        for task in self.worker_tasks:
            task.cancel()
        
        if self.worker_tasks:
            await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        self.worker_tasks = []
        logger.info("All update processing workers stopped")

    async def start_polling(self, timeout: int = 30, limit: int = 100):
        """Start polling for updates"""
        offset = 0
        max_retries = 5
        retry_delay = 5
        backoff_factor = 1.5
        
        # Start workers
        await self.start_workers()
        
        try:
            while True:
                for attempt in range(max_retries):
                    try:
                        updates = await self._rate_limited_api_call(
                            self.methods.get_updates(offset=offset, timeout=timeout, limit=limit)
                        )
                        
                        for update in updates:
                            if isinstance(update, dict) and 'update_id' in update:
                                await self._queue_update(update)
                                offset = int(update['update_id']) + 1
                            else:
                                logger.warning(f"Received invalid update: {update}")
                        
                        # Reset retry delay on success
                        retry_delay = 5
                        break  # If successful, break the retry loop
                        
                    except aiohttp.ClientError as e:
                        wait_time = retry_delay * (backoff_factor ** attempt)
                        logger.error(f"Connection error while polling (attempt {attempt + 1}/{max_retries}): {e}. Retrying in {wait_time:.1f}s")
                        
                        if attempt < max_retries - 1:
                            await asyncio.sleep(wait_time)
                        else:
                            logger.error("Max retries reached. Restarting polling loop.")
                            await asyncio.sleep(retry_delay * 2)
                            retry_delay = min(retry_delay * backoff_factor, 60)  # Cap at 60 seconds
                            
                    except Exception as e:
                        logger.exception(f"Error while polling: {e}")
                        await asyncio.sleep(retry_delay)
                        retry_delay = min(retry_delay * backoff_factor, 60)
        
        except asyncio.CancelledError:
            logger.info("Polling task cancelled")
        finally:
            await self.stop_workers()

    async def _handle_webhook_request(self, request):
        """Handle incoming webhook requests"""
        try:
            if request.method != 'POST':
                return web.Response(text='Method not allowed', status=405)
                
            if request.path != self.webhook_path:
                return web.Response(text='Not found', status=404)
                
            update_data = await request.json()
            
            # Queue the update for processing
            await self._queue_update(update_data)
            
            # Immediately return 200 OK to Telegram
            return web.Response(text='OK', status=200)
        except Exception as e:
            logger.exception(f"Error handling webhook request: {e}")
            return web.Response(text='Internal Server Error', status=500)

    async def setup_webhook(self, webhook_url: str, webhook_path: str = '/webhook', 
                           port: int = 8443, cert_path: str = None,
                           ip_address: str = None, max_connections: int = 100):
        """Setup webhook for receiving updates"""
        self.webhook_url = webhook_url
        self.webhook_path = webhook_path
        self.webhook_port = port
        self.max_connections = max_connections
        
        # Create the aiohttp web application
        self.webhook_app = web.Application()
        self.webhook_app.router.add_post(webhook_path, self._handle_webhook_request)
        
        # Set webhook with Telegram
        params = {
            'url': webhook_url,
            'max_connections': max_connections
        }
        
        if cert_path:
            with open(cert_path, 'rb') as cert_file:
                params['certificate'] = cert_file.read()
                
        if ip_address:
            params['ip_address'] = ip_address
            
        await self._rate_limited_api_call(self.methods.set_webhook(**params))
        logger.info(f"Webhook set to {webhook_url}")
        
        # Start workers
        await self.start_workers()
        
        return self.webhook_app

    async def remove_webhook(self):
        """Remove webhook from Telegram servers"""
        await self._rate_limited_api_call(self.methods.delete_webhook())
        logger.info("Webhook removed")

    async def start_webhook(self, webhook_url: str, webhook_path: str = '/webhook', 
                           port: int = 8443, ssl_context=None, host: str = '0.0.0.0',
                           cert_path: str = None, ip_address: str = None,
                           max_connections: int = 100):
        """Start webhook server for receiving updates"""
        app = await self.setup_webhook(
            webhook_url=webhook_url,
            webhook_path=webhook_path,
            port=port,
            cert_path=cert_path,
            ip_address=ip_address,
            max_connections=max_connections
        )
        
        runner = web.AppRunner(app)
        await runner.setup()
        
        # Create site and start it
        site = web.TCPSite(runner, host, port, ssl_context=ssl_context)
        await site.start()
        
        logger.info(f"Webhook server started at {host}:{port}{webhook_path}")
        return runner, site

    async def initialize(self):
        """Initialize the bot by getting bot information"""
        if not self.token:
            raise ValueError("Bot token not set. Please provide a valid token when initializing the Client.")
        
        try:
            me_dict = await self._rate_limited_api_call(self.methods.get_me())
            self.me = User.from_dict(me_dict)
            logger.info(f"Bot initialized: @{self.me.username}")
            return self.me
        except Exception as e:
            logger.exception(f"Error initializing bot: {e}")
            raise

    async def run_polling(self, skip_updates: bool = False):
        """Run the bot using polling mode"""
        try:
            await self.initialize()
            
            if skip_updates:
                updates = await self._rate_limited_api_call(self.methods.get_updates(offset=-1, limit=1))
                if updates:
                    offset = updates[-1]['update_id'] + 1
                    await self._rate_limited_api_call(self.methods.get_updates(offset=offset, limit=1))
                    logger.info("Skipped pending updates")
            
            polling_task = asyncio.create_task(self.start_polling())
            
            try:
                # Keep running until cancelled
                await polling_task
            except asyncio.CancelledError:
                polling_task.cancel()
                try:
                    await polling_task
                except asyncio.CancelledError:
                    pass
                logger.info("Bot stopped")
        except Exception as e:
            logger.exception(f"Error running bot: {e}")
            raise

    async def run_webhook(self, webhook_url: str, webhook_path: str = '/webhook', 
                         port: int = 8443, ssl_context=None, host: str = '0.0.0.0',
                         cert_path: str = None, ip_address: str = None,
                         max_connections: int = 40, drop_pending_updates: bool = False):
        """Run the bot using webhook mode"""
        try:
            await self.initialize()
            
            if drop_pending_updates:
                await self._rate_limited_api_call(self.methods.delete_webhook(drop_pending_updates=True))
                logger.info("Dropped pending updates")
            
            runner, site = await self.start_webhook(
                webhook_url=webhook_url,
                webhook_path=webhook_path,
                port=port,
                ssl_context=ssl_context,
                host=host,
                cert_path=cert_path,
                ip_address=ip_address,
                max_connections=max_connections
            )
            
            return runner, site
        except Exception as e:
            logger.exception(f"Error running webhook server: {e}")
            raise

    def run(self, polling: bool = True, **kwargs):
        """Run the bot (synchronous wrapper)"""
        if polling:
            return asyncio.run(self.run_polling(**kwargs))
        else:
            return asyncio.run(self.run_webhook(**kwargs))

    def load_plugins(self, plugins_dir: str):
        """Load all plugins from the specified directory"""
        if not os.path.exists(plugins_dir):
            logger.warning(f"Plugins directory '{plugins_dir}' not found.")
            return

        for root, dirs, files in os.walk(plugins_dir):
            for file in files:
                if file.endswith(".py") and not file.startswith("__"):
                    module_path = os.path.join(root, file)
                    module_name = os.path.splitext(os.path.relpath(module_path, os.getcwd()))[0].replace(os.path.sep, '.')
                    try:
                        spec = importlib.util.spec_from_file_location(module_name, module_path)
                        module = importlib.util.module_from_spec(spec)
                        
                        # Set the bot instance in the module's global namespace
                        module.bot = self
                        module.get_file = self.methods.get_file_path
                        
                        spec.loader.exec_module(module)
                        logger.info(f"Loaded plugin: {module_name}")
                    except Exception as e:
                        logger.exception(f"Error loading plugin {module_name}: {e}")


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
        try:
            # Extract the specific update type object to pass to the handler
            update_obj = getattr(update, self.update_type) if self.update_type else update
            await self.callback(bot, update_obj)
        except Exception as e:
            logger.exception(f"Error in handler {self.callback.__name__}: {e}")


# Create singleton instance
bot = Client()
