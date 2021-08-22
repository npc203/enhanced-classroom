from utils import Singleton
import logging
import aiofiles
import aiohttp

logger = logging.getLogger(__name__)
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler("./logs/downloader.log")

logger.addHandler(c_handler)
logger.addHandler(f_handler)


class Downloader(metaclass=Singleton):
    def __init__(self):
        self.download_queue = []
        self.session = aiohttp.ClientSession()

    # async def download(self, urls):
    #     for url in image_urls:
    #         self.download_queue.append(self.fetch(url))
    #     await asyncio.gather(*tasks)

    @staticmethod
    async def fetch(session: aiohttp.ClientSession, url: str, path: str):
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    async with aiofiles.open(path, mode="wb") as f:
                        await f.write(await resp.read())
                        await f.close()
                else:
                    logger.warning(f"Broken url:{resp.status} - {url}")
            logger.info(f"Done: {url}")
        except Exception as e:
            logger.error(f"Error while downloading from: {url}", exc_info=True)
