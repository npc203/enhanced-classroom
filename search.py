import asyncio
import logging
import os
import re
from pathlib import Path
from typing import List

import bs4
from tika import parser
from tika.tika import parse
from tinydb import where
from whoosh import index
from whoosh.fields import ID, TEXT, Schema
from whoosh.qparser import QueryParser
from whoosh.writing import IndexWriter

from consts import DOWNLOAD_PATH

logger = logging.getLogger("clsroom.search")
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler("./logs/search.log")

logger.addHandler(c_handler)
logger.addHandler(f_handler)

schema = Schema(
    courseId=ID(stored=True),
    topicId=ID(stored=True),
    fileId=ID(stored=True),
    title=TEXT(stored=True),
    pageNo=ID(stored=True),
    blob=TEXT,
)

# Not using the dynamic const from path.
indexdir = DOWNLOAD_PATH + ".index"
if not os.path.exists(indexdir):
    os.mkdir(indexdir)
    index.create_in(indexdir, schema)


class Search:
    ix = index.open_dir(indexdir)
    ext_mapper = {
        ".pptx": "slide-master-content",
        ".ppt": "slide-master-content",
        ".pdf": "page",
    }

    def __pager(self, xml: str, extension=None):
        soup = bs4.BeautifulSoup(xml, features="lxml")
        if divClass := self.ext_mapper.get(extension, None):
            logger.info("Paginating")
            for page in soup.findAll("div", class_=divClass):
                yield page.text
        yield soup.text

    def __worker_blob(self, metadata: dict, filepath: Path, writer: IndexWriter):
        """Does the actual api call parts and indexing"""
        logging.info(f"Started to parse and index {metadata['title']}")
        parsed = parser.from_file(str(filepath), xmlContent=True)
        try:
            if parsed["status"] == 200:
                if parsed["content"]:
                    for pageNo, blob in enumerate(
                        self.__pager(parsed["content"], filepath.suffix), 1
                    ):
                        writer.add_document(
                            courseId=metadata["courseId"],
                            topicId=metadata["topicId"],
                            fileId=metadata["id"],
                            title=metadata["title"],
                            pageNo=str(pageNo),
                            blob=blob,
                        )
                    logging.info(f"Indexed {metadata['title']}")
            else:
                logging.warning(
                    f"Invalid response from tika server, code: {parsed['status']}"
                )
        except Exception:
            logging.warning(f"Failed to index {metadata['title']}", exc_info=True)

    def index_course(self, courseId: str):
        """Index files to the database"""
        if course := self.course_db.get(where("id") == courseId):
            # TODO hard code remove it
            folder_path = Path(DOWNLOAD_PATH) / (
                course["name"] + " - " + course.get("section", "None")
            )
            work_materials = self.mat_db.search(where("courseId") == courseId)
            with self.ix.writer() as writer:
                logger.info(f"Starting to index {course['name']}")
                for thing in work_materials:
                    if "materials" in thing:
                        for material in thing["materials"]:
                            if "driveFile" in material:
                                file = material["driveFile"]["driveFile"]

                                # NO videos
                                if any(
                                    file["title"].endswith(i)
                                    for i in self.video_extensions
                                ):
                                    continue

                                # Indexing the file
                                filepath = Path(folder_path) / file["title"]
                                if filepath.is_file():
                                    metadata = {
                                        "courseId": courseId,
                                        "topicId": thing.get("topicId", "None"),
                                        "id": file["id"],
                                        "title": file["title"],
                                    }
                                    self.__worker_blob(metadata, filepath, writer)
                                else:
                                    logger.warning(f"File Not found {filepath}")
        else:
            raise RuntimeError("Course not found")

    def remove_from_index(self, fileId: str):
        """Remove from index"""
        # TODO
        self.ix.delete_by_term("fileId", fileId)
        self.ix.commit()
        logging.info(f"Removed {fileId} from index")

    # Maybe not a generator
    def search(self, query: str):
        """Search engine implementation"""
        with self.ix.searcher() as searcher:
            # print(next(searcher.lexicon("blob")))
            prep = QueryParser("blob", self.ix.schema).parse(query)
            results = searcher.search(prep)
            for i in results:
                yield i
