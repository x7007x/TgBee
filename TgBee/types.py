from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, field, asdict
import json

class DotDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, value in self.items():
            if isinstance(value, dict):
                self[key] = DotDict(value)
            elif isinstance(value, list):
                self[key] = [DotDict(item) if isinstance(item, dict) else item for item in value]

    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        self[name] = value

class JSONSerializable:
    def to_dict(self):
        return {k: v for k, v in asdict(self).items() if v is not None}

    def __str__(self):
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

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
        def HTML(self):
            return f'<a href="tg://user?id={self.id}">{self.first_name}</a>'
        def MARKDOWN(self):
            return f'[{self.id}]({self.first_name})'
        return self.first_name

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

    async def add_members(self, user_ids: Union[int, List[int]], **kwargs):
        from .methods import Methods
        return await Methods.get_current().add_chat_members(self.id, user_ids, **kwargs)

    async def archive(self, **kwargs):
        from .methods import Methods
        return await Methods.get_current().archive_chat(self.id, **kwargs)

    async def ban_member(self, user_id: int, **kwargs):
        from .methods import Methods
        return await Methods.get_current().ban_chat_member(self.id, user_id, **kwargs)

    async def export_invite_link(self, **kwargs):
        from .methods import Methods
        return await Methods.get_current().export_chat_invite_link(self.id, **kwargs)

    async def get_member(self, user_id: int, **kwargs):
        from .methods import Methods
        return await Methods.get_current().get_chat_member(self.id, user_id, **kwargs)

    async def get_members(self, **kwargs):
        from .methods import Methods
        return await Methods.get_current().get_chat_members(self.id, **kwargs)

    async def join(self, **kwargs):
        from .methods import Methods
        return await Methods.get_current().join_chat(self.id, **kwargs)

    async def leave(self, **kwargs):
        from .methods import Methods
        return await Methods.get_current().leave_chat(self.id, **kwargs)

    async def mark_unread(self, **kwargs):
        from .methods import Methods
        return await Methods.get_current().mark_chat_unread(self.id, **kwargs)

    async def promote_member(self, user_id: int, **kwargs):
        from .methods import Methods
        return await Methods.get_current().promote_chat_member(self.id, user_id, **kwargs)

    async def restrict_member(self, user_id: int, permissions: Dict[str, bool], **kwargs):
        from .methods import Methods
        return await Methods.get_current().restrict_chat_member(self.id, user_id, permissions, **kwargs)

    async def set_description(self, description: str, **kwargs):
        from .methods import Methods
        return await Methods.get_current().set_chat_description(self.id, description, **kwargs)

    async def set_photo(self, photo: Union[str, bytes], **kwargs):
        from .methods import Methods
        return await Methods.get_current().set_chat_photo(self.id, photo, **kwargs)

    async def set_protected_content(self, protected: bool, **kwargs):
        from .methods import Methods
        return await Methods.get_current().set_chat_protected_content(self.id, protected, **kwargs)

    async def set_title(self, title: str, **kwargs):
        from .methods import Methods
        return await Methods.get_current().set_chat_title(self.id, title, **kwargs)

    async def unarchive(self, **kwargs):
        from .methods import Methods
        return await Methods.get_current().unarchive_chat(self.id, **kwargs)

    async def unban_member(self, user_id: int, **kwargs):
        from .methods import Methods
        return await Methods.get_current().unban_chat_member(self.id, user_id, **kwargs)

    async def unpin_all_messages(self, **kwargs):
        from .methods import Methods
        return await Methods.get_current().unpin_all_chat_messages(self.id, **kwargs)

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
    photo: Optional[List[Dict[str, Any]]] = None
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
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})

    async def copy(self, chat_id: Union[int, str], **kwargs):
        from .methods import Methods
        return await Methods.get_current().copy_message(chat_id, self.chat.id, self.message_id, **kwargs)

    async def delete(self, **kwargs):
        from .methods import Methods
        return await Methods.get_current().delete_message(self.chat.id, self.message_id, **kwargs)

    async def download(self, file_name: str = None, **kwargs):
        if self.document:
            file_id = self.document['file_id']
        elif self.photo:
            file_id = self.photo[-1].file_id
        elif self.audio:
            file_id = self.audio['file_id']
        elif self.video:
            file_id = self.video['file_id']
        else:
            raise ValueError("No downloadable content in this message")

        from .methods import Methods
        file_info = await Methods.get_current().get_file(file_id)
        return await Methods.get_current().download_file(file_info['file_path'], file_name, **kwargs)

    async def edit(self, **kwargs):
        from .methods import Methods
        return await Methods.get_current().edit_message_text(chat_id=self.chat.id, message_id=self.message_id, **kwargs)

    async def edit_caption(self, caption: str, **kwargs):
        from .methods import Methods
        return await Methods.get_current().edit_message_caption(chat_id=self.chat.id, message_id=self.message_id, caption=caption, **kwargs)

    async def edit_media(self, media: Dict[str, Any], **kwargs):
        from .methods import Methods
        return await Methods.get_current().edit_message_media(chat_id=self.chat.id, message_id=self.message_id, media=media, **kwargs)

    async def edit_reply_markup(self, reply_markup: Dict[str, Any], **kwargs):
        from .methods import Methods
        return await Methods.get_current().edit_message_reply_markup(chat_id=self.chat.id, message_id=self.message_id, reply_markup=reply_markup, **kwargs)

    async def edit_text(self, text: str, **kwargs):
        from .methods import Methods
        return await Methods.get_current().edit_message_text(chat_id=self.chat.id, message_id=self.message_id, text=text, **kwargs)

    async def forward(self, chat_id: Union[int, str], **kwargs):
        from .methods import Methods
        return await Methods.get_current().forward_message(chat_id, self.chat.id, self.message_id, **kwargs)

    async def pin(self, **kwargs):
        from .methods import Methods
        return await Methods.get_current().pin_chat_message(self.chat.id, self.message_id, **kwargs)

    async def react(self, emoji: str, **kwargs):
        from .methods import Methods
        return await Methods.get_current().set_message_reaction(self.chat.id, self.message_id, [emoji], **kwargs)

    async def reply(self, text: str, **kwargs):
        from .methods import Methods
        return await Methods.get_current().send_message(self.chat.id, text, reply_to_message_id=self.message_id, **kwargs)

    async def reply_animation(self, animation: Union[str, bytes], **kwargs):
        from .methods import Methods
        return await Methods.get_current().send_animation(self.chat.id, animation, reply_to_message_id=self.message_id, **kwargs)

    async def reply_audio(self, audio: Union[str, bytes], **kwargs):
        from .methods import Methods
        return await Methods.get_current().send_audio(self.chat.id, audio, reply_to_message_id=self.message_id, **kwargs)

    async def reply_cached_media(self, file_id: str, **kwargs):
        from .methods import Methods
        return await Methods.get_current().send_cached_media(self.chat.id, file_id, reply_to_message_id=self.message_id, **kwargs)

    async def reply_chat_action(self, action: str, **kwargs):
        from .methods import Methods
        return await Methods.get_current().send_chat_action(self.chat.id, action, **kwargs)

    async def reply_contact(self, phone_number: str, first_name: str, **kwargs):
        from .methods import Methods
        return await Methods.get_current().send_contact(self.chat.id, phone_number, first_name, reply_to_message_id=self.message_id, **kwargs)

    async def reply_document(self, document: Union[str, bytes], **kwargs):
        from .methods import Methods
        return await Methods.get_current().send_document(self.chat.id, document, reply_to_message_id=self.message_id, **kwargs)

    async def reply_game(self, game_short_name: str, **kwargs):
        from .methods import Methods
        return await Methods.get_current().send_game(self.chat.id, game_short_name, reply_to_message_id=self.message_id, **kwargs)

    async def reply_inline_bot_result(self, inline_message_id: str, **kwargs):
        from .methods import Methods
        return await Methods.get_current().send_inline_bot_result(self.chat.id, inline_message_id, reply_to_message_id=self.message_id, **kwargs)

    async def reply_location(self, latitude: float, longitude: float, **kwargs):
        from .methods import Methods
        return await Methods.get_current().send_location(self.chat.id, latitude, longitude, reply_to_message_id=self.message_id, **kwargs)

    async def reply_media_group(self, media: List[Dict[str, Any]], **kwargs):
        from .methods import Methods
        return await Methods.get_current().send_media_group(self.chat.id, media, reply_to_message_id=self.message_id, **kwargs)

    async def reply_photo(self, photo: Union[str, bytes], **kwargs):
        from .methods import Methods
        return await Methods.get_current().send_photo(self.chat.id, photo, reply_to_message_id=self.message_id, **kwargs)

    async def reply_poll(self, question: str, options: List[str], **kwargs):
        from .methods import Methods
        return await Methods.get_current().send_poll(self.chat.id, question, options, reply_to_message_id=self.message_id, **kwargs)

    async def reply_sticker(self, sticker: Union[str, bytes], **kwargs):
        from .methods import Methods
        return await Methods.get_current().send_sticker(self.chat.id, sticker, reply_to_message_id=self.message_id, **kwargs)

    async def reply_text(self, text: str, **kwargs) -> 'Message':
        from .methods import Methods
        result = await Methods.get_current().send_message(self.chat.id, text, reply_to_message_id=self.message_id, **kwargs)
        return Message.from_dict(result)

    async def reply_venue(self, latitude: float, longitude: float, title: str, address: str, **kwargs):
        from .methods import Methods
        return await Methods.get_current().send_venue(self.chat.id, latitude, longitude, title, address, reply_to_message_id=self.message_id, **kwargs)

    async def reply_video(self, video: Union[str, bytes], **kwargs):
        from .methods import Methods
        return await Methods.get_current().send_video(self.chat.id, video, reply_to_message_id=self.message_id, **kwargs)

    async def reply_video_note(self, video_note: Union[str, bytes], **kwargs):
        from .methods import Methods
        return await Methods.get_current().send_video_note(self.chat.id, video_note, reply_to_message_id=self.message_id, **kwargs)

    async def reply_voice(self, voice: Union[str, bytes], **kwargs):
        from .methods import Methods
        return await Methods.get_current().send_voice(self.chat.id, voice, reply_to_message_id=self.message_id, **kwargs)

    async def unpin(self, **kwargs):
        from .methods import Methods
        return await Methods.get_current().unpin_chat_message(self.chat.id, self.message_id, **kwargs)

    async def vote(self, option: int, **kwargs):
        from .methods import Methods
        return await Methods.get_current().vote_poll(self.chat.id, self.message_id, option, **kwargs)

    def __getitem__(self, key):
        return getattr(self, key)

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=2)

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

    async def answer(self, text: Optional[str] = None, show_alert: bool = False, **kwargs):
        from .methods import Methods
        return await Methods.get_current().answer_callback_query(self.id, text=text, show_alert=show_alert, **kwargs)

    async def edit_message_caption(self, caption: str, **kwargs):
        from .methods import Methods
        return await Methods.get_current().edit_message_caption(chat_id=self.message.chat.id, message_id=self.message.message_id, caption=caption, **kwargs)

    async def edit_message_media(self, media: Dict[str, Any], **kwargs):
        from .methods import Methods
        return await Methods.get_current().edit_message_media(chat_id=self.message.chat.id, message_id=self.message.message_id, media=media, **kwargs)

    async def edit_message_reply_markup(self, reply_markup: Dict[str, Any], **kwargs):
        from .methods import Methods
        return await Methods.get_current().edit_message_reply_markup(chat_id=self.message.chat.id, message_id=self.message.message_id, reply_markup=reply_markup, **kwargs)

    async def edit_message_text(self, text: str, **kwargs):
        from .methods import Methods
        return await Methods.get_current().edit_message_text(chat_id=self.message.chat.id, message_id=self.message.message_id, text=text, **kwargs)

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

    async def answer(self, results: List[Dict[str, Any]], **kwargs):
        from .methods import Methods
        return await Methods.get_current().answer_inline_query(self.id, results, **kwargs)

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

    async def answer(self, ok: bool, shipping_options: Optional[List[Dict[str, Any]]] = None, error_message: Optional[str] = None):
        from .methods import Methods
        return await Methods.get_current().answer_shipping_query(self.id, ok, shipping_options, error_message)

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

    async def answer(self, ok: bool, error_message: Optional[str] = None):
        from .methods import Methods
        return await Methods.get_current().answer_pre_checkout_query(self.id, ok, error_message)

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

    async def approve(self, **kwargs):
        from .methods import Methods
        return await Methods.get_current().approve_chat_join_request(self.chat.id, self.from_user.id, **kwargs)

    async def decline(self, **kwargs):
        from .methods import Methods
        return await Methods.get_current().decline_chat_join_request(self.chat.id, self.from_user.id, **kwargs)

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

