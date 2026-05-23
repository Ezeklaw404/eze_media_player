import os
import subprocess
# import vlc

vlc = r"C:/Program Files (x86)/VideoLAN/VLC/vlc.exe"
hunter_url = "C:/stuf/amine/[Judas] Hunter x Hunter (2011) (Complete Series + Movies) [BD 1080p][HEVC x265 10bit][Dual-Audio][Eng-Subs]/[Judas] Hunter x Hunter (2011) - Episodes 001-148"
file_name = "[Judas] Hunter x Hunter (2011) - S01E020.mkv"
path = folder_to_play = os.path.normpath(hunter_url)


# os.startfile(hunter_url)
# os.system(vlc + hunter_url)
subprocess.Popen([vlc, path])

# player = vlc.MediaPlayer(f"{hunter_url}/{file_name}")
