import asyncio
import io

from googleapiclient.http import MediaIoBaseDownload

from main import Client

bot = Client()
drive = bot.services["drive"]
file_id = "1GFjUddhjLtKQ1tViMjU5764YLtihqXKc"
data = drive.files().get(fileId=file_id).execute()
print(data)
request = drive.files().get_media(fileId=file_id)
fh = io.BytesIO()
downloader = MediaIoBaseDownload(fh, request)
done = False
while done is False:
    status, done = downloader.next_chunk()
    print("Download %d%%." % int(status.progress() * 100))

with open(data["name"], "wb") as out:
    out.write(fh.getbuffer())
