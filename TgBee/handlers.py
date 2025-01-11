from typing import Callable, Any
from .types import Update

class Handler:
    def __init__(self, callback: Callable, filters=None, update_type=None):
        self.callback = callback
        self.filters = filters
        self.update_type = update_type

    def check(self, update: Update) -> bool:
        if self.update_type:
            if not hasattr(update, self.update_type):
                return False
        if self.filters:
            return self.filters(update)
        return True

    async def handle(self, bot, update: Update):
        await self.callback(bot, getattr(update, self.update_type, update))

