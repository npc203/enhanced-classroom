import asyncio
import io
import logging

import aiofiles
import aiohttp
from googleapiclient.http import MediaIoBaseDownload

from utils import Singleton

logger = logging.getLogger("clsroom.downloader")
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler("./logs/downloader.log")

logger.addHandler(c_handler)
logger.addHandler(f_handler)


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


class Downloader(metaclass=Singleton):
    def download_batch(self, id_path: dict):
        """Download from file_id and store in the given path"""
        tasks = []

        # Spliting into chunks
        for chunk in chunks(id_path.items(), 100):
            for file_id, path in chunk:
                tasks.append(self._worker(file_id, path))
            self.dl_thread.run_until_complete(asyncio.gather(*tasks))

    async def _worker(self, file_id, path):
        """Download from file_id and store in the given path"""
        request = self.services["drive"].files().get_media(fileId=file_id)

        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            logger.info("Download %d%%." % int(status.progress() * 100))

        # Is this even worth it?
        async with aiofiles.open(path, mode="wb") as f:
            await f.write(fh.getbuffer())

        logger.info("Downloaded {}".format(path))

    # @staticmethod
    # async def fetch(session: aiohttp.ClientSession, url: str, path: str):
    #     try:
    #         async with session.get(url) as resp:
    #             if resp.status == 200:
    #                 async with aiofiles.open(path, mode="wb") as f:
    #                     await f.write(await resp.read())
    #                     await f.close()
    #             else:
    #                 logger.warning(f"Broken url:{resp.status} - {url}")
    #         logger.info(f"Done: {url}")
    #     except Exception as e:
    #         logger.error(f"Error while downloading from: {url}", exc_info=True)

    # async def download(self, urls):
    #     for url in image_urls:
    #         self.download_queue.append(self.fetch(url))
    #     await asyncio.gather(*tasks)
