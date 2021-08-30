import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import Resource, build
from tinydb import Query, TinyDB
from tinydb_smartcache import SmartCacheTable

from auth import Auth
from consts import DOWNLOAD_PATH
from downloader import Downloader
from utils import Singleton


class Client(Auth, Downloader, metaclass=Singleton):
    def __init__(self, services: Dict[str, Resource] = {}):
        self.services = services

        # Initialize auth
        super().__init__()

        # Initialize downloader
        self.data_path = Path(os.path.abspath(__file__)).parent / DOWNLOAD_PATH
        self.dl_thread = asyncio.new_event_loop()

        # Initialize tinydb
        self.db = TinyDB(self.data_path / "db.json")
        self.db.table_class = SmartCacheTable
        self.course_db = self.db.table("courses")

        # Metadata Vars

    def load_courses(self, limit=None) -> List:
        """Load courses,If limit None, then gets every course"""
        crawler = self.services["classroom"].courses()
        query = Query()
        for resp in self.crawl_full(crawler, limit=limit):
            for course in resp["courses"]:
                self.course_db.upsert(course, query.id == course["id"])
        # return self.course_db.all()

    def build(self, service: str, version: str, creds: Credentials) -> Resource:
        built = build(service, version, credentials=creds)
        self.services[service] = built
        return built

    # Maybe not make this a generator
    @staticmethod
    def crawl_full(crawler: Any, limit=None, pageSize=100, **kwargs) -> List[Dict[str, Any]]:
        print("mooo")
        page_token = None
        if limit:
            times = limit // 100
            last_remainder = limit % 100
            for _ in range(times):
                response = crawler.list(
                    pageToken=page_token, pageSize=pageSize, **kwargs
                ).execute()
                page_token = response.get("nextPageToken", None)
                yield response
                if not page_token:
                    break

            # Last page
            yield crawler.list(pageToken=page_token, pageSize=last_remainder, **kwargs).execute()
        else:
            print("mooo1")
            while True:
                print("mooo2")
                response = crawler.list(
                    pageToken=page_token, pageSize=pageSize, **kwargs
                ).execute()
                page_token = response.get("nextPageToken", None)
                yield response
                if not page_token:
                    break

    def crawl(
        self, to_crawl: str, resp_obj: str, courseId: int, limit: int = None, **kwargs
    ) -> List[Dict]:
        """
        Crawls the given resource from classroom and returns a list of the response objects

        :param to_crawl: The resource to crawl         - courseWorkMaterials,topics,courseWork
        :param resp_obj: The response object to return - courseWorkMaterial,topic,courseWork
        :param courseId: The courseId to crawl
        :param limit: The limit of items to crawl
        :return: A list of response objects
        """
        things = []
        if crawler := getattr(self.services["classroom"].courses(), to_crawl, None):
            for value in self.crawl_full(crawler(), limit, courseId=courseId, **kwargs):
                things.extend(value[resp_obj])
            return things
        else:
            raise AttributeError(f"{to_crawl} is not a valid item to crawl")


if __name__ == "__main__":
    client = Client()
    # courses = client.load_courses()
    # print(client.load_courses())
    # print(len(client.course_db))
    # print(client.crawl("topics", "topic", 328146111353))
    # client.download("AAA", "AAA")
