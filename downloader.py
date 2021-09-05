import asyncio
import io
import logging
import os
from pathlib import Path

from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError
from tinydb import TinyDB
from tinydb_smartcache import SmartCacheTable

from consts import DOWNLOAD_PATH
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
    # Initialize downloader
    data_path = Path(os.path.abspath(__file__)).parent / DOWNLOAD_PATH
    dl_thread = asyncio.get_event_loop()

    # Initialize tinydb
    db = TinyDB(data_path / "db.json")
    db.table_class = SmartCacheTable
    course_db = db.table("courses")
    topic_db = db.table("topics")
    mat_db = db.table("materials")

    def download_batch(self, id_path: dict):
        """Download from file_id and store in the given path"""
        tasks = []

        # Spliting into 10 file parallel downloads
        # for chunk in chunks(, 10):
        for file_id, path in list(id_path.items()):
            tasks.append(self.__worker_downloader(file_id, path))
        self.dl_thread.run_until_complete(asyncio.gather(*tasks))

    async def __worker_downloader(self, file_id, path):
        """Download from file_id and store in the given path"""
        try:
            request = self.services["drive"].files().get_media(fileId=file_id)
        except HttpError:
            # Export as pdf if it's in drive
            request = (
                self.services["drive"]
                .files()
                .export_media(fileId=file_id, mimeType="application/pdf")
            )
            logger.warning(f"File {file_id} : {path} is not in drive, exporting as pdf")

        # Make path if it didn't exist
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        try:
            fh = io.FileIO(path, "wb")
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                logger.info(f"Downloaded {path} : {status.progress() * 100:.2f}")
            logger.info("Completed {}".format(path))
        except Exception as e:
            logger.error(f"Error downloading {path} : {e}")

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
