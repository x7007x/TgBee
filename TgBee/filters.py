import re
from typing import Callable, Any, List, Union
from .types import Update, Message, User, Chat

class Filter:
    def __init__(self, func: Callable[[Update], bool]):
        self.func = func

    def __call__(self, update: Update) -> bool:
        return self.func(update)

    def __and__(self, other):
        return Filter(lambda update: self(update) and other(update))

    def __or__(self, other):
        return Filter(lambda update: self(update) or other(update))

    def __invert__(self):
        return Filter(lambda update: not self(update))

class Filters:
    @staticmethod
    def create(func: Callable[[Update], bool]) -> Filter:
        return Filter(func)

    @staticmethod
    def text(pattern: str = None) -> Filter:
        if pattern is None:
            return Filter(lambda u: u.message and u.message.text is not None)
        return Filter(lambda u: u.message and u.message.text and pattern in u.message.text)

    @staticmethod
    def command(commands: Union[str, List[str]], prefixes: Union[str, List[str]] = "/") -> Filter:
        if isinstance(commands, str):
            commands = [commands]
        if isinstance(prefixes, str):
            prefixes = [prefixes]
        return Filter(lambda u: u.message and u.message.text and any(u.message.text.lower().startswith(f"{prefix}{cmd.lower()}") for prefix in prefixes for cmd in commands))

    @staticmethod
    def regex(pattern: str) -> Filter:
        regex = re.compile(pattern)
        return Filter(lambda u: u.message and u.message.text and regex.search(u.message.text))

    @staticmethod
    def user(users: Union[int, str, List[Union[int, str]]]) -> Filter:
        if isinstance(users, (int, str)):
            users = [users]
        return Filter(lambda u: u.message and u.message.from_user and (u.message.from_user.id in users or u.message.from_user.username in users))

    @staticmethod
    def chat(chats: Union[int, str, List[Union[int, str]]]) -> Filter:
        if isinstance(chats, (int, str)):
            chats = [chats]
        return Filter(lambda u: u.message and (u.message.chat.id in chats or u.message.chat.username in chats))

    @staticmethod
    def private() -> Filter:
        return Filter(lambda u: u.message and u.message.chat.type == "private")

    @staticmethod
    def group() -> Filter:
        return Filter(lambda u: u.message and u.message.chat.type in ["group", "supergroup"])

    @staticmethod
    def channel() -> Filter:
        return Filter(lambda u: u.message and u.message.chat.type == "channel")

    @staticmethod
    def new_chat_members() -> Filter:
        return Filter(lambda u: u.message and u.message.new_chat_members)

    @staticmethod
    def left_chat_member() -> Filter:
        return Filter(lambda u: u.message and u.message.left_chat_member)

    @staticmethod
    def poll() -> Filter:
        return Filter(lambda u: u.poll)

    @staticmethod
    def reply() -> Filter:
        return Filter(lambda u: u.message and u.message.reply_to_message)

    @staticmethod
    def forwarded() -> Filter:
        return Filter(lambda u: u.message and u.message.forward_date)

    @staticmethod
    def caption(pattern: str = None) -> Filter:
        if pattern is None:
            return Filter(lambda u: u.message and u.message.caption is not None)
        return Filter(lambda u: u.message and u.message.caption and pattern in u.message.caption)

    @staticmethod
    def audio() -> Filter:
        return Filter(lambda u: u.message and u.message.audio)

    @staticmethod
    def document() -> Filter:
        return Filter(lambda u: u.message and u.message.document)

    @staticmethod
    def photo() -> Filter:
        return Filter(lambda u: u.message and u.message.photo)

    @staticmethod
    def sticker() -> Filter:
        return Filter(lambda u: u.message and u.message.sticker)

    @staticmethod
    def video() -> Filter:
        return Filter(lambda u: u.message and u.message.video)

    @staticmethod
    def voice() -> Filter:
        return Filter(lambda u: u.message and u.message.voice)

    @staticmethod
    def video_note() -> Filter:
        return Filter(lambda u: u.message and u.message.video_note)

    @staticmethod
    def contact() -> Filter:
        return Filter(lambda u: u.message and u.message.contact)

    @staticmethod
    def location() -> Filter:
        return Filter(lambda u: u.message and u.message.location)

    @staticmethod
    def venue() -> Filter:
        return Filter(lambda u: u.message and u.message.venue)

    @staticmethod
    def web_page() -> Filter:
        return Filter(lambda u: u.message and u.message.web_page)

    @staticmethod
    def game() -> Filter:
        return Filter(lambda u: u.message and u.message.game)

text = Filters.text()
command = Filters.command
regex = Filters.regex
user = Filters.user
chat = Filters.chat
private = Filters.private()
group = Filters.group()
channel = Filters.channel()
new_chat_members = Filters.new_chat_members()
left_chat_member = Filters.left_chat_member()
poll = Filters.poll()
reply = Filters.reply()
forwarded = Filters.forwarded()
caption = Filters.caption()
audio = Filters.audio()
document = Filters.document()
photo = Filters.photo()
sticker = Filters.sticker()
video = Filters.video()
voice = Filters.voice()
video_note = Filters.video_note()
contact = Filters.contact()
location = Filters.location()
venue = Filters.venue()
web_page = Filters.web_page()
game = Filters.game()

