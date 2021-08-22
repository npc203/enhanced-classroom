from downloader import Downloader
from auth import Auth
from typing import Dict, Any, List
from utils import Singleton
from googleapiclient.discovery import Resource, build
from google.oauth2.credentials import Credentials
import logging


class Client(Auth, Downloader, metaclass=Singleton):
    def __init__(self, services: Dict[str, Resource] = {}):
        self.services = services
        super().__init__()
        # Initialize auth
        self.auth()

        # build the services
        if self.creds:
            self.build("classroom", "v1", self.creds)
            self.build("drive", "v3", self.creds)
        else:
            raise RuntimeError("Can't build services")

    def build(self, service: str, version: str, creds: Credentials) -> Resource:
        built = build(service, version, credentials=creds)
        self.services[service] = built
        return built

    # Maybe not make this a generator
    @staticmethod
    def crawl_full(crawler: Any, limit=None, **kwargs) -> List[Dict[str, Any]]:
        page_token = None
        if limit:
            times = limit // 100
            last_remainder = limit % 100
            for _ in range(times):
                response = crawler.list(pageToken=page_token, pageSize=100, **kwargs).execute()
                page_token = response.get("nextPageToken", None)
                if not page_token:
                    break
                yield response
            # Last page
            yield crawler.list(pageToken=page_token, pageSize=last_remainder, **kwargs).execute()
        else:
            while True:
                response = crawler.list(pageToken=page_token, pageSize=100, **kwargs).execute()
                page_token = response.get("nextPageToken", None)
                if not page_token:
                    break
                yield response

    def crawl(
        self, to_crawl: str, resp_obj: str, courseId: str, limit: int = None, **kwargs
    ) -> List[Dict]:
        """
        Crawls the given resource from classroom and returns a list of the response objects

        :param to_crawl: The resource to crawl
        :param resp_obj: The response object to return
        :param courseId: The courseId to crawl
        :param limit: The limit of items to crawl
        :return: A list of response objects
        """
        things = []
        if crawler := getattr(self.services["classroom"].courses(), to_crawl, None):
            for value in self.crawl_full(crawler(), limit, courseId=courseId, kwargs=kwargs):
                things.extend(value[resp_obj])
            return things
        else:
            raise AttributeError(f"{to_crawl} is not a valid item to crawl")


if __name__ == "__main__":
    client = Client()
