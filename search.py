from tika.tika import parse
from consts import DOWNLOAD_PATH, INDEX_PATH
import logging
import os
from typing import List
from tinydb import where

from whoosh import index
from whoosh.qparser import QueryParser
from whoosh.fields import TEXT, ID, Schema
from tika import parser
from pathlib import Path
import asyncio
import re

logger = logging.getLogger("clsroom.search")
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler("./logs/search.log")

schema = Schema(
    courseId=ID(stored=True),
    topicId=ID(stored=True),
    fileId=ID(stored=True),
    title=TEXT(stored=True),
    blob=TEXT,
)

# Not using the dynamic const from path.
indexdir = INDEX_PATH + ".index"
if not os.path.exists(indexdir):
    os.mkdir(indexdir)
    index.create_in(indexdir, schema)


class Search:
    ix = index.open_dir(indexdir)

    async def __worker_blob(self, filepath: Path):
        """Does the actual api call parts"""
        parsed = parser.from_file(str(filepath))
        if parsed["status"] == 200:
            dest = INDEX_PATH / Path(filepath.parent.name) / (filepath.stem + ".txt")
            if parsed["content"]:
                with open(dest, "w", encoding="utf-8") as f:
                    f.write(parsed["content"])
                logging.info(f"Sucessfully converted and stored in {dest}")
        else:
            logging.warning(f"Invalid response from tika server, code: {parsed['status']}")

    def __convert_to_blobs(self, folderpath: Path):
        """Convert's files into blobs of texts and stores in .indexed for txt parsing"""
        tasks = []
        # Make path if it didn't exist
        Path(INDEX_PATH / Path(folderpath.name)).mkdir(parents=True, exist_ok=True)
        for file in folderpath.iterdir():
            if file.is_file():
                logging.info(f"Converting {file} to blob")
                tasks.append(self.__worker_blob(file))
        self.dl_thread.run_until_complete(asyncio.gather(*tasks))

    def convert(self, folderpath: str):
        """Convert's files into blobs of texts and stores in .indexed for txt parsing"""
        self.__convert_to_blobs(Path(folderpath))

    def index_course(self, courseId: str):
        """Index files to the database"""
        writer = self.ix.writer()
        if course := self.course_db.get(where("id") == courseId):
            # TODO hard code remove it
            folder_name = course["name"] + " - " + course.get("section", "None")
            indexed_folder_path = Path(INDEX_PATH) / folder_name
            work_materials = self.mat_db.search(where("courseId") == courseId)
            for thing in work_materials:
                if "materials" in thing:
                    for material in thing["materials"]:
                        if "driveFile" in material:
                            file = material["driveFile"]["driveFile"]
                            # NO videos
                            if any(file["title"].endswith(i) for i in self.video_extensions):
                                continue
                            # print(thing)
                            try:
                                # Indexing the file
                                with open(
                                    indexed_folder_path
                                    / (file["title"].rsplit(".", 1)[0] + ".txt"),
                                    "r",
                                    encoding="utf-8",
                                ) as f:
                                    content = f.read()
                                    # Minor compressings (maybe remove it)
                                    content = re.sub(r"\n+", "\n", content).strip()

                                writer.add_document(
                                    courseId=courseId,
                                    topicId=thing["topicId"],
                                    fileId=file["id"],
                                    title=file["title"],
                                    blob=content,
                                )
                            except Exception as e:
                                logging.warning(f"Failed to index {file['title']}")
                                logging.error(e)
                                # raise e
                            logging.info(f"Indexed {file['title']}")
            writer.commit()
        else:
            raise RuntimeError("Course not found")

    def remove_from_index(self, fileId: str):
        """Remove from index"""
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
