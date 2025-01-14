import aiohttp
from typing import List, Dict, Any, Optional, Union

class Methods:
    def __init__(self):
        self.base_url = None

    async def _make_request(self, method: str, data: Dict[str, Any] = None, files: Dict[str, Any] = None) -> Dict[str, Any]:
        if not self.base_url:
            raise ValueError("Bot token not set. Call set_token() first.")
        
        async with aiohttp.ClientSession() as session:
            if files:
                form_data = aiohttp.FormData()
                for key, value in (data or {}).items():
                    form_data.add_field(key, str(value))
                for file_key, file_info in files.items():
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
        return await self.call("getUpdates", **kwargs)

    async def set_webhook(self, **kwargs) -> bool:
        return await self.call("setWebhook", **kwargs)

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

    async def send_message(self, **kwargs) -> Dict[str, Any]:
        return await self.call("sendMessage", **kwargs)

    async def forward_message(self, **kwargs) -> Dict[str, Any]:
        return await self.call("forwardMessage", **kwargs)

    async def copy_message(self, **kwargs) -> Dict[str, Any]:
        return await self.call("copyMessage", **kwargs)

    async def send_photo(self, **kwargs) -> Dict[str, Any]:
        return await self.call("sendPhoto", **kwargs)

    async def send_audio(self, **kwargs) -> Dict[str, Any]:
        return await self.call("sendAudio", **kwargs)

    async def send_document(self, **kwargs) -> Dict[str, Any]:
        return await self.call("sendDocument", **kwargs)

    async def send_video(self, **kwargs) -> Dict[str, Any]:
        return await self.call("sendVideo", **kwargs)

    async def send_animation(self, **kwargs) -> Dict[str, Any]:
        return await self.call("sendAnimation", **kwargs)

    async def send_voice(self, **kwargs) -> Dict[str, Any]:
        return await self.call("sendVoice", **kwargs)

    async def send_video_note(self, **kwargs) -> Dict[str, Any]:
        return await self.call("sendVideoNote", **kwargs)

    async def send_media_group(self, **kwargs) -> List[Dict[str, Any]]:
        return await self.call("sendMediaGroup", **kwargs)

    async def send_location(self, **kwargs) -> Dict[str, Any]:
        return await self.call("sendLocation", **kwargs)

    async def edit_message_live_location(self, **kwargs) -> Dict[str, Any]:
        return await self.call("editMessageLiveLocation", **kwargs)

    async def stop_message_live_location(self, **kwargs) -> Dict[str, Any]:
        return await self.call("stopMessageLiveLocation", **kwargs)

    async def send_venue(self, **kwargs) -> Dict[str, Any]:
        return await self.call("sendVenue", **kwargs)

    async def send_contact(self, **kwargs) -> Dict[str, Any]:
        return await self.call("sendContact", **kwargs)

    async def send_poll(self, **kwargs) -> Dict[str, Any]:
        return await self.call("sendPoll", **kwargs)

    async def send_dice(self, **kwargs) -> Dict[str, Any]:
        return await self.call("sendDice", **kwargs)

    async def send_chat_action(self, **kwargs) -> bool:
        return await self.call("sendChatAction", **kwargs)

    async def get_user_profile_photos(self, **kwargs) -> Dict[str, Any]:
        return await self.call("getUserProfilePhotos", **kwargs)

    async def get_file(self, **kwargs) -> Dict[str, Any]:
        return await self.call("getFile", **kwargs)

    async def ban_chat_member(self, **kwargs) -> bool:
        return await self.call("banChatMember", **kwargs)

    async def unban_chat_member(self, **kwargs) -> bool:
        return await self.call("unbanChatMember", **kwargs)

    async def restrict_chat_member(self, **kwargs) -> bool:
        return await self.call("restrictChatMember", **kwargs)

    async def promote_chat_member(self, **kwargs) -> bool:
        return await self.call("promoteChatMember", **kwargs)

    async def set_chat_administrator_custom_title(self, **kwargs) -> bool:
        return await self.call("setChatAdministratorCustomTitle", **kwargs)

    async def ban_chat_sender_chat(self, **kwargs) -> bool:
        return await self.call("banChatSenderChat", **kwargs)

    async def unban_chat_sender_chat(self, **kwargs) -> bool:
        return await self.call("unbanChatSenderChat", **kwargs)

    async def set_chat_permissions(self, **kwargs) -> bool:
        return await self.call("setChatPermissions", **kwargs)

    async def export_chat_invite_link(self, **kwargs) -> str:
        return await self.call("exportChatInviteLink", **kwargs)

    async def create_chat_invite_link(self, **kwargs) -> Dict[str, Any]:
        return await self.call("createChatInviteLink", **kwargs)

    async def edit_chat_invite_link(self, **kwargs) -> Dict[str, Any]:
        return await self.call("editChatInviteLink", **kwargs)

    async def revoke_chat_invite_link(self, **kwargs) -> Dict[str, Any]:
        return await self.call("revokeChatInviteLink", **kwargs)

    async def approve_chat_join_request(self, **kwargs) -> bool:
        return await self.call("approveChatJoinRequest", **kwargs)

    async def decline_chat_join_request(self, **kwargs) -> bool:
        return await self.call("declineChatJoinRequest", **kwargs)

    async def set_chat_photo(self, **kwargs) -> bool:
        return await self.call("setChatPhoto", **kwargs)

    async def delete_chat_photo(self, **kwargs) -> bool:
        return await self.call("deleteChatPhoto", **kwargs)

    async def set_chat_title(self, **kwargs) -> bool:
        return await self.call("setChatTitle", **kwargs)

    async def set_chat_description(self, **kwargs) -> bool:
        return await self.call("setChatDescription", **kwargs)

    async def pin_chat_message(self, **kwargs) -> bool:
        return await self.call("pinChatMessage", **kwargs)

    async def unpin_chat_message(self, **kwargs) -> bool:
        return await self.call("unpinChatMessage", **kwargs)

    async def unpin_all_chat_messages(self, **kwargs) -> bool:
        return await self.call("unpinAllChatMessages", **kwargs)

    async def leave_chat(self, **kwargs) -> bool:
        return await self.call("leaveChat", **kwargs)

    async def get_chat(self, **kwargs) -> Dict[str, Any]:
        return await self.call("getChat", **kwargs)

    async def get_chat_administrators(self, **kwargs) -> List[Dict[str, Any]]:
        return await self.call("getChatAdministrators", **kwargs)

    async def get_chat_member_count(self, **kwargs) -> int:
        return await self.call("getChatMemberCount", **kwargs)

    async def get_chat_member(self, **kwargs) -> Dict[str, Any]:
        return await self.call("getChatMember", **kwargs)

    async def set_chat_sticker_set(self, **kwargs) -> bool:
        return await self.call("setChatStickerSet", **kwargs)

    async def delete_chat_sticker_set(self, **kwargs) -> bool:
        return await self.call("deleteChatStickerSet", **kwargs)

    async def answer_callback_query(self, **kwargs) -> bool:
        return await self.call("answerCallbackQuery", **kwargs)

    async def set_my_commands(self, **kwargs) -> bool:
        return await self.call("setMyCommands", **kwargs)

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

    async def edit_message_text(self, **kwargs) -> Union[bool, Dict[str, Any]]:
        return await self.call("editMessageText", **kwargs)

    async def edit_message_caption(self, **kwargs) -> Union[bool, Dict[str, Any]]:
        return await self.call("editMessageCaption", **kwargs)

    async def edit_message_media(self, **kwargs) -> Union[bool, Dict[str, Any]]:
        return await self.call("editMessageMedia", **kwargs)

    async def edit_message_reply_markup(self, **kwargs) -> Union[bool, Dict[str, Any]]:
        return await self.call("editMessageReplyMarkup", **kwargs)

    async def stop_poll(self, **kwargs) -> Dict[str, Any]:
        return await self.call("stopPoll", **kwargs)

    async def delete_message(self, **kwargs) -> bool:
        return await self.call("deleteMessage", **kwargs)

    def set_token(self, token: str):
        self.base_url = f"https://api.telegram.org/bot{token}/"

