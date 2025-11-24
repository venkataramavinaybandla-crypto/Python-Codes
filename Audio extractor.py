from moviepy import VideoFileClip
from pathlib import Path

video_path = input("Enter path of the video file: ").strip().replace('"', '')

print("Loading video...")
video = VideoFileClip(video_path)
audio = video.audio

output_name = input("Enter file name: ").strip()
output_file = output_name + ".mp3"

downloads_path = Path.home() / "Downloads"

print("Extracting audio... please wait")
audio.write_audiofile(str(downloads_path / output_file))

video.close()
print("Audio extraction complete!")
