import aiohttp
import aiofiles
import os
from typing import Union

class FileHandler:
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.base_url = f"https://api.telegram.org/file/bot{bot_token}/"

    async def download_file(self, file_path: str, destination: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.base_url + file_path) as response:
                if response.status == 200:
                    async with aiofiles.open(destination, 'wb') as f:
                        await f.write(await response.read())
                else:
                    raise Exception(f"Failed to download file: {response.status}")

    async def upload_file(self, file_path: Union[str, bytes], file_name: str = None):
        if isinstance(file_path, str):
            async with aiofiles.open(file_path, 'rb') as f:
                file_content = await f.read()
            file_name = file_name or os.path.basename(file_path)
        else:
            file_content = file_path
            file_name = file_name or "file"

        return file_content, file_name

    async def get_file_info(self, file_id: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.telegram.org/bot{self.bot_token}/getFile", params={"file_id": file_id}) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["result"]
                else:
                    raise Exception(f"Failed to get file info: {response.status}")

