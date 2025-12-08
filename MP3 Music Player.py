import vlc
import time
import os

folder = "music"
songs = [f for f in os.listdir(folder) if f.lower().endswith(".mp3")]

if not songs:
    print("No songs found!")
    exit()

print("=== MP3 Player with Seeking ===\n")
for i, s in enumerate(songs, 1):
    print(f"{i}. {s}")

choice = int(input("\nEnter song number: ")) - 1
if choice < 0 or choice >= len(songs):
    print("Invalid choice!")
    exit()

song_path = os.path.join(folder, songs[choice])
player = vlc.MediaPlayer(song_path)

player.play()
time.sleep(1)

print("\nControls:")
print("space = pause/resume")
print("f = forward 10s")
print("b = rewind 10s")
print("q = quit")

paused = False

while True:
    key = input("")

    if key == " ":
        if paused:
            player.play()
            paused = False
            print("Resumed")
        else:
            player.pause()
            paused = True
            print("Paused")

    elif key.lower() == "f":
        current = player.get_time()
        player.set_time(current + 10000)
        print("Forward 10 sec")

    elif key.lower() == "b":
        current = player.get_time()
        player.set_time(max(0, current - 10000))
        print("Backward 10 sec")

    elif key.lower() == "q":
        player.stop()
        break

    length = player.get_length()
    pos = player.get_time()
    print(f"Position: {pos/1000:.1f}s / {length/1000:.1f}s")
