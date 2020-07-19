#!/usr/bin/python3 -u
from __future__ import unicode_literals
import os
import shutil
from argparse import ArgumentParser
import subprocess

import youtube_dl

ap = ArgumentParser()
ap.add_argument("-v", "--videoid", required=True, type=str,
                        help="Youtube Video ID")
args = vars(ap.parse_args())

videoid = args['videoid']

# disable buffering
class Unbuffered(object):
   def __init__(self, stream):
       self.stream = stream
   def write(self, data):
       self.stream.write(data)
       self.stream.flush()
   def writelines(self, datas):
       self.stream.writelines(datas)
       self.stream.flush()
   def __getattr__(self, attr):
       return getattr(self.stream, attr)

import sys
sys.stdout = Unbuffered(sys.stdout)


DL_DIR = '/tmp'
MUSIC_DIR = '/media/datos/Syncthing/Phone-Music/yt-dl'

# change to downloads dir
os.chdir(DL_DIR)

# Array containing youtube-dl info
D = None

class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def my_hook(d):
    if d['status'] == 'downloading':
        if d['total_bytes']:
            perc = (d['downloaded_bytes'] * 100) // d['total_bytes']
        else:
            perc = -1
        print(f"Downloading... {perc}%")
    if d['status'] == 'finished':
        print("\n", d)
        print('\nDone downloading, now converting ...')
        global D
        D = d


ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
}
with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    ydl.download([f"https://www.youtube.com/watch?v={videoid}"])

if D['status'] == 'finished':
    # Replace webm extension for mp3
    FILENAME = D['filename'].replace('.webm', '.mp3')
    print(f"Done.")
else:
    print("File not downloaded")

if os.path.exists(os.path.join(MUSIC_DIR, FILENAME)):
    print("\nEsta cancion ya estaba descargada.")

print(f"Moviendo al directorio de musica: {MUSIC_DIR}");
# move the file either way
PFILENAME = os.path.join(DL_DIR, FILENAME)
MFILENAME = os.path.join(MUSIC_DIR, FILENAME)
shutil.copyfile(PFILENAME, MFILENAME)
os.remove(PFILENAME)

# fix permissions
subprocess.run(['chown', '-R', 'aorith:odroid', MUSIC_DIR])

print(f"\nGuardado como: {FILENAME}");

print(f"\nYA PUEDES CERRAR ESTA VENTANA.");

