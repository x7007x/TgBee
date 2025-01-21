import aiohttp
import aiofiles
import os
import logging
from typing import TYPE_CHECKING, List, Dict, Any, Optional, Union
from .types import Message, User, Chat, DotDict

# Set up logging
logger = logging.getLogger(__name__)

class DotDict(dict):
    def __getattr__(self, name):
        return self[name]

class Methods:
    def __init__(self):
        self.base_url = None
        self.token = None
        self.main_script_path = None

    def set_token(self, token: str):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}/"

    def set_main_script_path(self, path: str):
        self.main_script_path = path

    async def _make_request(self, method: str, data: Dict[str, Any] = None, files: Dict[str, Any] = None) -> Dict[str, Any]:
        if not self.base_url:
            raise ValueError("Bot token not set")
        
        url = self.base_url + method
        if not url.startswith("https://"):
            raise ValueError(f"Invalid base URL: {self.base_url}")

        logger.debug(f"Making request. Method: {method}, URL: {url}")
        
        async with aiohttp.ClientSession() as session:
            if files:
                form_data = aiohttp.FormData()
                for key, value in (data or {}).items():
                    form_data.add_field(key, str(value))
                for file_key, file_info in files.items():
                    if isinstance(file_info, str):
                        # It's a file path
                        async with aiofiles.open(file_info, 'rb') as f:
                            form_data.add_field(file_key, await f.read(), filename=os.path.basename(file_info))
                    elif isinstance(file_info, bytes):
                        # It's raw bytes
                        form_data.add_field(file_key, file_info, filename=f"{file_key}.dat")
                    else:
                        # It's a tuple (file_content, filename, content_type)
                        form_data.add_field(file_key, file_info[0], filename=file_info[1], content_type=file_info[2])
                async with session.post(self.base_url + method, data=form_data) as response:
                    result = await response.json()
            else:
                async with session.post(self.base_url + method, json=data) as response:
                    result = await response.json()
            
            if not result.get('ok'):
                raise Exception(f"Telegram API error: {result.get('description')}")
            return result.get('result')

    async def call(self, method: str, **kwargs):
        return await self._make_request(method, kwargs)

    # Getting updates
    async def get_updates(self, **kwargs) -> List[Dict[str, Any]]:
        try:
            result = await self.call("getUpdates", **kwargs)
            logger.debug(f"Raw getUpdates result: {result}")
            
            if isinstance(result, list):
                return [DotDict(update) for update in result]
            elif isinstance(result, dict):
                if 'result' in result and isinstance(result['result'], list):
                    return [DotDict(update) for update in result['result']]
                else:
                    logger.error(f"Unexpected result structure from getUpdates: {result}")
                    return []
            else:
                logger.error(f"Unexpected result type from getUpdates: {type(result)}")
                return []
        except Exception as e:
            logger.exception(f"Error in get_updates: {e}")
            return []

    async def set_webhook(self, url: str, **kwargs) -> bool:
        return await self.call("setWebhook", url=url, **kwargs)

    async def delete_webhook(self, **kwargs) -> bool:
        return await self.call("deleteWebhook", **kwargs)

    async def get_webhook_info(self) -> Dict[str, Any]:
        return await self.call("getWebhookInfo")

    # Available methods
    async def get_me(self) -> Dict[str, Any]:
        return await self.call("getMe")

    async def log_out(self) -> bool:
        return await self.call("logOut")

    async def close(self) -> bool:
        return await self.call("close")

    async def send_message(self, chat_id: Union[int, str], text: str, **kwargs) -> Dict[str, Any]:
        return await self.call("sendMessage", chat_id=chat_id, text=text, **kwargs)

    async def forward_message(self, chat_id: Union[int, str], from_chat_id: Union[int, str], message_id: int, **kwargs) -> Dict[str, Any]:
        return await self.call("forwardMessage", chat_id=chat_id, from_chat_id=from_chat_id, message_id=message_id, **kwargs)

    async def copy_message(self, chat_id: Union[int, str], from_chat_id: Union[int, str], message_id: int, **kwargs) -> Dict[str, Any]:
        return await self.call("copyMessage", chat_id=chat_id, from_chat_id=from_chat_id, message_id=message_id, **kwargs)

    async def send_photo(self, chat_id: Union[int, str], photo: Union[str, bytes], **kwargs) -> Dict[str, Any]:
        files = {'photo': photo} if isinstance(photo, (str, bytes)) else None
        return await self._make_request("sendPhoto", {'chat_id': chat_id, **kwargs}, files)

    async def send_audio(self, chat_id: Union[int, str], audio: Union[str, bytes], **kwargs) -> Dict[str, Any]:
        files = {'audio': audio} if isinstance(audio, (str, bytes)) else None
        return await self._make_request("sendAudio", {'chat_id': chat_id, **kwargs}, files)

    async def send_document(self, chat_id: Union[int, str], document: Union[str, bytes], **kwargs) -> Dict[str, Any]:
        files = {'document': document} if isinstance(document, (str, bytes)) else None
        return await self._make_request("sendDocument", {'chat_id': chat_id, **kwargs}, files)

    async def send_video(self, chat_id: Union[int, str], video: Union[str, bytes], **kwargs) -> Dict[str, Any]:
        files = {'video': video} if isinstance(video, (str, bytes)) else None
        return await self._make_request("sendVideo", {'chat_id': chat_id, **kwargs}, files)

    async def send_animation(self, chat_id: Union[int, str], animation: Union[str, bytes], **kwargs) -> Dict[str, Any]:
        files = {'animation': animation} if isinstance(animation, (str, bytes)) else None
        return await self._make_request("sendAnimation", {'chat_id': chat_id, **kwargs}, files)

    async def send_voice(self, chat_id: Union[int, str], voice: Union[str, bytes], **kwargs) -> Dict[str, Any]:
        files = {'voice': voice} if isinstance(voice, (str, bytes)) else None
        return await self._make_request("sendVoice", {'chat_id': chat_id, **kwargs}, files)

    async def send_video_note(self, chat_id: Union[int, str], video_note: Union[str, bytes], **kwargs) -> Dict[str, Any]:
        files = {'video_note': video_note} if isinstance(video_note, (str, bytes)) else None
        return await self._make_request("sendVideoNote", {'chat_id': chat_id, **kwargs}, files)

    async def send_media_group(self, chat_id: Union[int, str], media: List[Dict[str, Any]], **kwargs) -> List[Dict[str, Any]]:
        return await self.call("sendMediaGroup", chat_id=chat_id, media=media, **kwargs)

    async def send_location(self, chat_id: Union[int, str], latitude: float, longitude: float, **kwargs) -> Dict[str, Any]:
        return await self.call("sendLocation", chat_id=chat_id, latitude=latitude, longitude=longitude, **kwargs)

    async def edit_message_live_location(self, latitude: float, longitude: float, **kwargs) -> Union[Dict[str, Any], bool]:
        return await self.call("editMessageLiveLocation", latitude=latitude, longitude=longitude, **kwargs)

    async def stop_message_live_location(self, **kwargs) -> Union[Dict[str, Any], bool]:
        return await self.call("stopMessageLiveLocation", **kwargs)

    async def send_venue(self, chat_id: Union[int, str], latitude: float, longitude: float, title: str, address: str, **kwargs) -> Dict[str, Any]:
        return await self.call("sendVenue", chat_id=chat_id, latitude=latitude, longitude=longitude, title=title, address=address, **kwargs)

    async def send_contact(self, chat_id: Union[int, str], phone_number: str, first_name: str, **kwargs) -> Dict[str, Any]:
        return await self.call("sendContact", chat_id=chat_id, phone_number=phone_number, first_name=first_name, **kwargs)

    async def send_poll(self, chat_id: Union[int, str], question: str, options: List[str], **kwargs) -> Dict[str, Any]:
        return await self.call("sendPoll", chat_id=chat_id, question=question, options=options, **kwargs)

    async def send_dice(self, chat_id: Union[int, str], **kwargs) -> Dict[str, Any]:
        return await self.call("sendDice", chat_id=chat_id, **kwargs)

    async def send_chat_action(self, chat_id: Union[int, str], action: str) -> bool:
        return await self.call("sendChatAction", chat_id=chat_id, action=action)

    async def get_user_profile_photos(self, user_id: int, **kwargs) -> Dict[str, Any]:
        return await self.call("getUserProfilePhotos", user_id=user_id, **kwargs)

    async def get_file(self, file_id: str) -> Dict[str, Any]:
        return await self.call("getFile", file_id=file_id)

    async def kick_chat_member(self, chat_id: Union[int, str], user_id: int, **kwargs) -> bool:
        return await self.call("kickChatMember", chat_id=chat_id, user_id=user_id, **kwargs)

    async def unban_chat_member(self, chat_id: Union[int, str], user_id: int, **kwargs) -> bool:
        return await self.call("unbanChatMember", chat_id=chat_id, user_id=user_id, **kwargs)

    async def restrict_chat_member(self, chat_id: Union[int, str], user_id: int, permissions: Dict[str, bool], **kwargs) -> bool:
        return await self.call("restrictChatMember", chat_id=chat_id, user_id=user_id, permissions=permissions, **kwargs)

    async def promote_chat_member(self, chat_id: Union[int, str], user_id: int, **kwargs) -> bool:
        return await self.call("promoteChatMember", chat_id=chat_id, user_id=user_id, **kwargs)

    async def set_chat_administrator_custom_title(self, chat_id: Union[int, str], user_id: int, custom_title: str) -> bool:
        return await self.call("setChatAdministratorCustomTitle", chat_id=chat_id, user_id=user_id, custom_title=custom_title)

    async def ban_chat_sender_chat(self, chat_id: Union[int, str], sender_chat_id: int) -> bool:
        return await self.call("banChatSenderChat", chat_id=chat_id, sender_chat_id=sender_chat_id)

    async def unban_chat_sender_chat(self, chat_id: Union[int, str], sender_chat_id: int) -> bool:
        return await self.call("unbanChatSenderChat", chat_id=chat_id, sender_chat_id=sender_chat_id)

    async def set_chat_permissions(self, chat_id: Union[int, str], permissions: Dict[str, bool]) -> bool:
        return await self.call("setChatPermissions", chat_id=chat_id, permissions=permissions)

    async def export_chat_invite_link(self, chat_id: Union[int, str]) -> str:
        return await self.call("exportChatInviteLink", chat_id=chat_id)

    async def create_chat_invite_link(self, chat_id: Union[int, str], **kwargs) -> Dict[str, Any]:
        return await self.call("createChatInviteLink", chat_id=chat_id, **kwargs)

    async def edit_chat_invite_link(self, chat_id: Union[int, str], invite_link: str, **kwargs) -> Dict[str, Any]:
        return await self.call("editChatInviteLink", chat_id=chat_id, invite_link=invite_link, **kwargs)

    async def revoke_chat_invite_link(self, chat_id: Union[int, str], invite_link: str) -> Dict[str, Any]:
        return await self.call("revokeChatInviteLink", chat_id=chat_id, invite_link=invite_link)

    async def approve_chat_join_request(self, chat_id: Union[int, str], user_id: int) -> bool:
        return await self.call("approveChatJoinRequest", chat_id=chat_id, user_id=user_id)

    async def decline_chat_join_request(self, chat_id: Union[int, str], user_id: int) -> bool:
        return await self.call("declineChatJoinRequest", chat_id=chat_id, user_id=user_id)

    async def set_chat_photo(self, chat_id: Union[int, str], photo: Union[str, bytes]) -> bool:
        files = {'photo': photo} if isinstance(photo, (str, bytes)) else None
        return await self._make_request("setChatPhoto", {'chat_id': chat_id}, files)

    async def delete_chat_photo(self, chat_id: Union[int, str]) -> bool:
        return await self.call("deleteChatPhoto", chat_id=chat_id)

    async def set_chat_title(self, chat_id: Union[int, str], title: str) -> bool:
        return await self.call("setChatTitle", chat_id=chat_id, title=title)

    async def set_chat_description(self, chat_id: Union[int, str], description: str) -> bool:
        return await self.call("setChatDescription", chat_id=chat_id, description=description)

    async def pin_chat_message(self, chat_id: Union[int, str], message_id: int, **kwargs) -> bool:
        return await self.call("pinChatMessage", chat_id=chat_id, message_id=message_id, **kwargs)

    async def unpin_chat_message(self, chat_id: Union[int, str], message_id: int = None) -> bool:
        return await self.call("unpinChatMessage", chat_id=chat_id, message_id=message_id)

    async def unpin_all_chat_messages(self, chat_id: Union[int, str]) -> bool:
        return await self.call("unpinAllChatMessages", chat_id=chat_id)

    async def leave_chat(self, chat_id: Union[int, str]) -> bool:
        return await self.call("leaveChat", chat_id=chat_id)

    async def get_chat(self, chat_id: Union[int, str]) -> Dict[str, Any]:
        return await self.call("getChat", chat_id=chat_id)

    async def get_chat_administrators(self, chat_id: Union[int, str]) -> List[Dict[str, Any]]:
        return await self.call("getChatAdministrators", chat_id=chat_id)

    async def get_chat_member_count(self, chat_id: Union[int, str]) -> int:
        return await self.call("getChatMemberCount", chat_id=chat_id)

    async def get_chat_member(self, chat_id: Union[int, str], user_id: int) -> Dict[str, Any]:
        return await self.call("getChatMember", chat_id=chat_id, user_id=user_id)

    async def set_chat_sticker_set(self, chat_id: Union[int, str], sticker_set_name: str) -> bool:
        return await self.call("setChatStickerSet", chat_id=chat_id, sticker_set_name=sticker_set_name)

    async def delete_chat_sticker_set(self, chat_id: Union[int, str]) -> bool:
        return await self.call("deleteChatStickerSet", chat_id=chat_id)

    async def answer_callback_query(self, callback_query_id: str, **kwargs) -> bool:
        return await self.call("answerCallbackQuery", callback_query_id=callback_query_id, **kwargs)

    async def set_my_commands(self, commands: List[Dict[str, str]], **kwargs) -> bool:
        return await self.call("setMyCommands", commands=commands, **kwargs)

    async def delete_my_commands(self, **kwargs) -> bool:
        return await self.call("deleteMyCommands", **kwargs)

    async def get_my_commands(self, **kwargs) -> List[Dict[str, str]]:
        return await self.call("getMyCommands", **kwargs)

    async def set_chat_menu_button(self, **kwargs) -> bool:
        return await self.call("setChatMenuButton", **kwargs)

    async def get_chat_menu_button(self, **kwargs) -> Dict[str, Any]:
        return await self.call("getChatMenuButton", **kwargs)

    async def set_my_default_administrator_rights(self, **kwargs) -> bool:
        return await self.call("setMyDefaultAdministratorRights", **kwargs)

    async def get_my_default_administrator_rights(self, **kwargs) -> Dict[str, Any]:
        return await self.call("getMyDefaultAdministratorRights", **kwargs)

    # Updating messages
    async def edit_message_text(self, text: str, **kwargs) -> Union[Dict[str, Any], bool]:
        return await self.call("editMessageText", text=text, **kwargs)

    async def edit_message_caption(self, **kwargs) -> Union[Dict[str, Any], bool]:
        return await self.call("editMessageCaption", **kwargs)

    async def edit_message_media(self, media: Dict[str, Any], **kwargs) -> Union[Dict[str, Any], bool]:
        return await self.call("editMessageMedia", media=media, **kwargs)

    async def edit_message_reply_markup(self, **kwargs) -> Union[Dict[str, Any], bool]:
        return await self.call("editMessageReplyMarkup", **kwargs)

    async def stop_poll(self, chat_id: Union[int, str], message_id: int, **kwargs) -> Dict[str, Any]:
        return await self.call("stopPoll", chat_id=chat_id, message_id=message_id, **kwargs)

    async def delete_message(self, chat_id: Union[int, str], message_id: int) -> bool:
        return await self.call("deleteMessage", chat_id=chat_id, message_id=message_id)

    # Stickers
    async def send_sticker(self, chat_id: Union[int, str], sticker: Union[str, bytes], **kwargs) -> Dict[str, Any]:
        files = {'sticker': sticker} if isinstance(sticker, (str, bytes)) else None
        return await self._make_request("sendSticker", {'chat_id': chat_id, **kwargs}, files)

    async def get_sticker_set(self, name: str) -> Dict[str, Any]:
        return await self.call("getStickerSet", name=name)

    async def upload_sticker_file(self, user_id: int, png_sticker: Union[str, bytes]) -> Dict[str, Any]:
        files = {'png_sticker': png_sticker}
        return await self._make_request("uploadStickerFile", {'user_id': user_id}, files)

    async def create_new_sticker_set(self, user_id: int, name: str, title: str, emojis: str, **kwargs) -> bool:
        return await self.call("createNewStickerSet", user_id=user_id, name=name, title=title, emojis=emojis, **kwargs)

    async def add_sticker_to_set(self, user_id: int, name: str, emojis: str, **kwargs) -> bool:
        return await self.call("addStickerToSet", user_id=user_id, name=name, emojis=emojis, **kwargs)

    async def set_sticker_position_in_set(self, sticker: str, position: int) -> bool:
        return await self.call("setStickerPositionInSet", sticker=sticker, position=position)

    async def delete_sticker_from_set(self, sticker: str) -> bool:
        return await self.call("deleteStickerFromSet", sticker=sticker)

    async def set_sticker_set_thumb(self, name: str, user_id: int, thumb: Union[str, bytes] = None) -> bool:
        files = {'thumb': thumb} if thumb else None
        return await self._make_request("setStickerSetThumb", {'name': name, 'user_id': user_id}, files)

    # Inline mode
    async def answer_inline_query(self, inline_query_id: str, results: List[Dict[str, Any]], **kwargs) -> bool:
        return await self.call("answerInlineQuery", inline_query_id=inline_query_id, results=results, **kwargs)

    # Payments
    async def send_invoice(self, chat_id: Union[int, str], title: str, description: str, payload: str,
                           provider_token: str, currency: str, prices: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        return await self.call("sendInvoice", chat_id=chat_id, title=title, description=description,
                               payload=payload, provider_token=provider_token, currency=currency,
                               prices=prices, **kwargs)

    async def answer_shipping_query(self, shipping_query_id: str, ok: bool, **kwargs) -> bool:
        return await self.call("answerShippingQuery", shipping_query_id=shipping_query_id, ok=ok, **kwargs)

    async def answer_pre_checkout_query(self, pre_checkout_query_id: str, ok: bool, **kwargs) -> bool:
        return await self.call("answerPreCheckoutQuery", pre_checkout_query_id=pre_checkout_query_id, ok=ok, **kwargs)

    # Telegram Passport
    async def set_passport_data_errors(self, user_id: int, errors: List[Dict[str, Any]]) -> bool:
        return await self.call("setPassportDataErrors", user_id=user_id, errors=errors)

    # Games
    async def send_game(self, chat_id: Union[int, str], game_short_name: str, **kwargs) -> Dict[str, Any]:
        return await self.call("sendGame", chat_id=chat_id, game_short_name=game_short_name, **kwargs)

    async def set_game_score(self, user_id: int, score: int, **kwargs) -> Union[Dict[str, Any], bool]:
        return await self.call("setGameScore", user_id=user_id, score=score, **kwargs)

    async def get_game_high_scores(self, user_id: int, **kwargs) -> List[Dict[str, Any]]:
        return await self.call("getGameHighScores", user_id=user_id, **kwargs)

    # Helper methods
    async def download_file(self, file_path: str, custom_path: str = None) -> str:
        url = f"https://api.telegram.org/file/bot{self.token}/{file_path}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    content = await resp.read()
                    path = custom_path or file_path.split("/")[-1]
                    async with aiofiles.open(path, "wb") as f:
                        await f.write(content)
                    return path
                else:
                    raise Exception(f"Failed to download file: {resp.status}")

    async def upload_file(self, file_path: str, file_name: str = None) -> Dict[str, Any]:
        async with aiofiles.open(file_path, "rb") as f:
            content = await f.read()
        files = {"document": (file_name or os.path.basename(file_path), content)}
        return await self._make_request("sendDocument", files=files)

    def get_file_path(self, relative_path: str) -> str:
        if self.main_script_path:
            return os.path.abspath(os.path.join(self.main_script_path, relative_path))
        else:
            raise ValueError("Main script path not set. Call set_main_script_path() first.")

    @classmethod
    def get_current(cls):
        return methods

methods = Methods()

