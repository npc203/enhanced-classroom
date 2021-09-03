import asyncio
from inspect import CO_NESTED
import json
import logging
from search import Search
from typing import Any, Dict, List

from auth import Auth
from downloader import Downloader
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import Resource, build
from utils import Singleton
from tinydb import Query, where
import os

logging.basicConfig(level=logging.INFO)


class Client(Auth, Downloader, Search, metaclass=Singleton):
    def __init__(self, services: Dict[str, Resource] = {}):
        self.services = services

        # Initialize auth
        super().__init__()

        # Metadata Vars
        self.video_extensions = [".mp4", ".webm", ".ogv", ".ogg", ".mkv", ".flv", ".m4v"]

    def load_courses(self, limit=None) -> List:
        """Load courses,If limit None, then gets every course"""
        crawler = self.services["classroom"].courses()
        query = Query()
        for resp in self.crawl_full(crawler, limit=limit):
            for course in resp["courses"]:
                course["hidden"] = False
                course["last_scrape"] = None
                self.course_db.upsert(course, query.id == course["id"])
        return self.course_db.all()

    def build(self, service: str, version: str, creds: Credentials) -> Resource:
        built = build(service, version, credentials=creds)
        self.services[service] = built
        return built

    # Maybe not make this a generator
    @staticmethod
    def crawl_full(
        crawler: Any,
        limit=None,
        page_token=None,
        pageSize=100,
        **kwargs,
    ) -> List[Dict[str, Any]]:

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
            while True:
                logging.info(f"Crawling unlimitedly with pageSize {pageSize}")
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

    def download_course(self, course_id: int):
        """Downloads all materials in a course, Make sure the ID is valid else it will crash"""

        cache_course = self.course_db.get(Query().id == str(course_id))
        if cache_course:
            course_name = (
                cache_course.get("name", "None") + " - " + cache_course.get("section", "None")
            )
        else:
            course = self.services["classroom"].courses().get(id=course_id).execute()
            course["hidden"] = False
            course["last_scrape"] = None
            self.course_db.insert(course)
            course_name = course.get("name", "None") + " - " + course.get("section", "None")

        # we already downloaded this course so just update the newer materials if not present
        if c_work_materials := self.mat_db.search(Query().courseId == str(course_id)):
            stop = False
            logging.info("Working with cache")
            crawler = getattr(self.services["classroom"].courses(), "courseWorkMaterials")
            query = Query()
            for batch_work_materials in self.crawl_full(
                crawler(),
                courseId=course_id,
                pageSize=10,
            ):
                batch_work_materials = batch_work_materials["courseWorkMaterial"]
                for work_material in batch_work_materials:
                    logging.info("Cache miss")
                    for cache_material in c_work_materials:
                        if cache_material["id"] == work_material["id"]:
                            stop = True
                            break
                    # Insert elements if we didn't find the last cached doc in the
                    self.mat_db.upsert(work_material, query.id == work_material["id"])
                    if stop:
                        break
                if stop:
                    break
            work_materials = self.mat_db.search(Query().courseId == course_id)
        else:
            logging.info("Fetching all materials")
            work_materials = self.crawl("courseWorkMaterials", "courseWorkMaterial", course_id)
            self.mat_db.insert_multiple(work_materials)

        logging.info(f"Number of materials to download: {len(work_materials)}")
        id_path = {}

        for thing in work_materials:
            if "materials" in thing:
                for material in thing["materials"]:
                    if "driveFile" in material:
                        file = material["driveFile"]["driveFile"]
                        # We don't need videos >_>
                        if not any(file["title"].endswith(i) for i in self.video_extensions):
                            file_path = f"data/{course_name}/{file['title']}"
                            # Make sure to NOT redownload the same thing
                            if not os.path.exists(file_path):
                                id_path[file["id"]] = file_path

        logging.info("Started downloading batch")
        # print(json.dumps(id_path, indent=2))
        self.download_batch(id_path)


if __name__ == "__main__":
    client = Client()
    client.auth()
    # print(client.services["classroom"].courses().get(id=123).execute())
    courses = client.course_db.all()
    # a = client.crawl(
    #     "courseWorkMaterials", "courseWorkMaterial", 328146111353, pageSize=10, limit=10
    # )
    # print(a)
    for i in courses:
        if "III" in i["name"] + " | " + i.get("section", "None"):
            client.download_course(i["id"])
    # a = {"", "data/test/owo.pdf"}
    # print(client.course_db.search(where("id") == "328146111353"))

    # for i in client.mat_db.all():
    #     print(i)
    #     break

    # client.download_batch(a)
    # a = {
    #     "1zOi2Pqw1xinhlc3oTajZDw14vKgwy5YY": "data/thinkCSpy.pdf",
    #     "1tDsb7pYy9imsCI5l-loBsx2ZEM8jfniP": "data/PrologBook.pdf",
    #     "1lb0xiCy6Us3l9AUzfsnarwF4fiD8_2Sv": "data/18CS502.pdf",
    # }
    # for i in client.course_db:
    #     if i["id"] != 328146111353:
    #         topics = client.crawl("topics", "topic", i["id"])
    #         client.topic_db.insert_multiple(topics)
    #         print(i["id"], len(topics))
    # client.download("AAA", "AAA")
