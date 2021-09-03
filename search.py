import os
from typing import List

from whoosh import index
from whoosh.fields import *

if not os.path.exists("data/.indexed"):
    os.mkdir("data/.indexed")


class Search:
    # from the path you can get the name OwO
    schema = Schema(
        courseId=ID(stored=True), topicId=ID(stored=True), path=ID(stored=True), blob=TEXT
    )
    # ix = index.create_in(".indexed", schema)

    def convert(self, file_paths: List):
        """Convert's files into blobs of texts and stores in .index for txt parsing"""

    def index(self, file_paths: List):
        """Index files to the database"""

    def search(self, query: str):
        """Search engine implementation"""
