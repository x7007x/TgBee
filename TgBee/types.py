from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass, field
import json

class JSONSerializable:
    def to_json(self):
        return json.dumps(self, default=lambda o: {k: v for k, v in o.__dict__.items() if v is not None}, 
                          ensure_ascii=False, indent=2)

@dataclass
class User(JSONSerializable):
    id: int
    is_bot: bool
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None
    can_join_groups: Optional[bool] = None
    can_read_all_group_messages: Optional[bool] = None
    supports_inline_queries: Optional[bool] = None

    @property
    def mention(self):
        return f'<a href="tg://user?id={self.id}">{self.first_name}</a>'

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})

@dataclass
class Chat(JSONSerializable):
    id: int
    type: str
    title: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})

@dataclass
class PhotoSize(JSONSerializable):
    file_id: str
    file_unique_id: str
    width: int
    height: int
    file_size: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})

@dataclass
class Message(JSONSerializable):
    message_id: int
    date: int
    chat: Chat
    from_user: Optional[User] = None
    text: Optional[str] = None
    caption: Optional[str] = None
    reply_to_message: Optional['Message'] = None
    new_chat_members: Optional[List[User]] = None
    left_chat_member: Optional[User] = None
    forward_date: Optional[int] = None
    audio: Optional[Dict[str, Any]] = None
    document: Optional[Dict[str, Any]] = None
    photo: Optional[List[PhotoSize]] = None
    sticker: Optional[Dict[str, Any]] = None
    video: Optional[Dict[str, Any]] = None
    voice: Optional[Dict[str, Any]] = None
    video_note: Optional[Dict[str, Any]] = None
    contact: Optional[Dict[str, Any]] = None
    location: Optional[Dict[str, Any]] = None
    venue: Optional[Dict[str, Any]] = None
    web_page: Optional[Dict[str, Any]] = None
    game: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        if 'from' in data:
            data['from_user'] = User.from_dict(data.pop('from'))
        if 'chat' in data:
            data['chat'] = Chat.from_dict(data['chat'])
        if 'reply_to_message' in data:
            data['reply_to_message'] = Message.from_dict(data['reply_to_message'])
        if 'new_chat_members' in data:
            data['new_chat_members'] = [User.from_dict(user) for user in data['new_chat_members']]
        if 'left_chat_member' in data:
            data['left_chat_member'] = User.from_dict(data['left_chat_member'])
        if 'photo' in data:
            data['photo'] = [PhotoSize.from_dict(photo) for photo in data['photo']]
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})

    async def reply_text(self, text: str, **kwargs):
        from .bot import Bot
        return await Bot.get_current().send_message(chat_id=self.chat.id, text=text, reply_to_message_id=self.message_id, **kwargs)

    async def reply_photo(self, photo: str, **kwargs):
        from .bot import Bot
        return await Bot.get_current().send_photo(chat_id=self.chat.id, photo=photo, reply_to_message_id=self.message_id, **kwargs)

    async def reply_audio(self, audio: str, **kwargs):
        from .bot import Bot
        return await Bot.get_current().send_audio(chat_id=self.chat.id, audio=audio, reply_to_message_id=self.message_id, **kwargs)

    async def reply_document(self, document: str, **kwargs):
        from .bot import Bot
        return await Bot.get_current().send_document(chat_id=self.chat.id, document=document, reply_to_message_id=self.message_id, **kwargs)

    async def reply_video(self, video: str, **kwargs):
        from .bot import Bot
        return await Bot.get_current().send_video(chat_id=self.chat.id, video=video, reply_to_message_id=self.message_id, **kwargs)

    async def reply_animation(self, animation: str, **kwargs):
        from .bot import Bot
        return await Bot.get_current().send_animation(chat_id=self.chat.id, animation=animation, reply_to_message_id=self.message_id, **kwargs)

    async def reply_voice(self, voice: str, **kwargs):
        from .bot import Bot
        return await Bot.get_current().send_voice(chat_id=self.chat.id, voice=voice, reply_to_message_id=self.message_id, **kwargs)

    async def reply_video_note(self, video_note: str, **kwargs):
        from .bot import Bot
        return await Bot.get_current().send_video_note(chat_id=self.chat.id, video_note=video_note, reply_to_message_id=self.message_id, **kwargs)

@dataclass
class CallbackQuery(JSONSerializable):
    id: str
    from_user: User
    chat_instance: str
    message: Optional[Message] = None
    data: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        if 'from' in data:
            data['from_user'] = User.from_dict(data.pop('from'))
        if 'message' in data:
            data['message'] = Message.from_dict(data['message'])
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})

    async def answer(self, text: str = None, show_alert: bool = False, **kwargs):
        from .bot import Bot
        return await Bot.get_current().answer_callback_query(self.id, text=text, show_alert=show_alert, **kwargs)

@dataclass
class InlineQuery(JSONSerializable):
    id: str
    from_user: User
    query: str
    offset: str
    chat_type: Optional[str] = None
    location: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        if 'from' in data:
            data['from_user'] = User.from_dict(data.pop('from'))
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})

@dataclass
class ChosenInlineResult(JSONSerializable):
    result_id: str
    from_user: User
    query: str
    location: Optional[Dict[str, Any]] = None
    inline_message_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        if 'from' in data:
            data['from_user'] = User.from_dict(data.pop('from'))
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})

@dataclass
class ShippingQuery(JSONSerializable):
    id: str
    from_user: User
    invoice_payload: str
    shipping_address: Dict[str, Any]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        if 'from' in data:
            data['from_user'] = User.from_dict(data.pop('from'))
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})

@dataclass
class PreCheckoutQuery(JSONSerializable):
    id: str
    from_user: User
    currency: str
    total_amount: int
    invoice_payload: str
    shipping_option_id: Optional[str] = None
    order_info: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        if 'from' in data:
            data['from_user'] = User.from_dict(data.pop('from'))
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})

@dataclass
class Poll(JSONSerializable):
    id: str
    question: str
    options: List[Dict[str, Any]]
    total_voter_count: int
    is_closed: bool
    is_anonymous: bool
    type: str
    allows_multiple_answers: bool
    correct_option_id: Optional[int] = None
    explanation: Optional[str] = None
    explanation_entities: Optional[List[Dict[str, Any]]] = None
    open_period: Optional[int] = None
    close_date: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})

@dataclass
class PollAnswer(JSONSerializable):
    poll_id: str
    user: User
    option_ids: List[int]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        if 'user' in data:
            data['user'] = User.from_dict(data['user'])
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})

@dataclass
class ChatMemberUpdated(JSONSerializable):
    chat: Chat
    from_user: User
    date: int
    old_chat_member: Dict[str, Any]
    new_chat_member: Dict[str, Any]
    invite_link: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        if 'chat' in data:
            data['chat'] = Chat.from_dict(data['chat'])
        if 'from' in data:
            data['from_user'] = User.from_dict(data.pop('from'))
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})

@dataclass
class ChatJoinRequest(JSONSerializable):
    chat: Chat
    from_user: User
    date: int
    bio: Optional[str] = None
    invite_link: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        if 'chat' in data:
            data['chat'] = Chat.from_dict(data['chat'])
        if 'from' in data:
            data['from_user'] = User.from_dict(data.pop('from'))
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})

@dataclass
class Update(JSONSerializable):
    update_id: int
    message: Optional[Message] = None
    edited_message: Optional[Message] = None
    channel_post: Optional[Message] = None
    edited_channel_post: Optional[Message] = None
    inline_query: Optional[InlineQuery] = None
    chosen_inline_result: Optional[ChosenInlineResult] = None
    callback_query: Optional[CallbackQuery] = None
    shipping_query: Optional[ShippingQuery] = None
    pre_checkout_query: Optional[PreCheckoutQuery] = None
    poll: Optional[Poll] = None
    poll_answer: Optional[PollAnswer] = None
    my_chat_member: Optional[ChatMemberUpdated] = None
    chat_member: Optional[ChatMemberUpdated] = None
    chat_join_request: Optional[ChatJoinRequest] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        update = cls(update_id=data['update_id'])
        if 'message' in data:
            update.message = Message.from_dict(data['message'])
        if 'edited_message' in data:
            update.edited_message = Message.from_dict(data['edited_message'])
        if 'channel_post' in data:
            update.channel_post = Message.from_dict(data['channel_post'])
        if 'edited_channel_post' in data:
            update.edited_channel_post = Message.from_dict(data['edited_channel_post'])
        if 'inline_query' in data:
            update.inline_query = InlineQuery.from_dict(data['inline_query'])
        if 'chosen_inline_result' in data:
            update.chosen_inline_result = ChosenInlineResult.from_dict(data['chosen_inline_result'])
        if 'callback_query' in data:
            update.callback_query = CallbackQuery.from_dict(data['callback_query'])
        if 'shipping_query' in data:
            update.shipping_query = ShippingQuery.from_dict(data['shipping_query'])
        if 'pre_checkout_query' in data:
            update.pre_checkout_query = PreCheckoutQuery.from_dict(data['pre_checkout_query'])
        if 'poll' in data:
            update.poll = Poll.from_dict(data['poll'])
        if 'poll_answer' in data:
            update.poll_answer = PollAnswer.from_dict(data['poll_answer'])
        if 'my_chat_member' in data:
            update.my_chat_member = ChatMemberUpdated.from_dict(data['my_chat_member'])
        if 'chat_member' in data:
            update.chat_member = ChatMemberUpdated.from_dict(data['chat_member'])
        if 'chat_join_request' in data:
            update.chat_join_request = ChatJoinRequest.from_dict(data['chat_join_request'])
        return update

