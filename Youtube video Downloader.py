from pytubefix import YouTube
from pathlib import Path

downloads_path = Path.home() / "Downloads"

print("Your Video will be saved in", downloads_path)

link = input("Enter YouTube video link: ")
yt = YouTube(link, use_oauth=False, allow_oauth_cache=False)
print("Video Title: ",yt.title)

stream = yt.streams.get_highest_resolution()
print(stream)

stream.download(output_path=str(downloads_path))
print("Download Complete")