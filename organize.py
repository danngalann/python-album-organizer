import os, eyed3
import eyed3.mimetype # Solves some issue with circular imports
from threading import Thread
from queue import Queue

dirs = list(filter(lambda x: os.path.isdir(x), os.listdir())) # Filter out files at root level (like this script)
nthreads = 8
q = Queue()

# Prepends the album to the song name (not necessary atm)
# EG rock_songname
def renameSong(fileName, dir):
  newFileName = fileName[:-3] + ".mp3"
  os.rename(fileName, newFileName)
  return newFileName

def processSong():
  global q
  while True:
    filePath = q.get()
    song = eyed3.load(filePath)
    [dir, fileName] = os.path.split(filePath)

    if song == None:
      print(f"{fileName} could not be processed (NoneType)")
      q.task_done()
      return

    # Remove title
    if song.tag.title:
      song.tag.title = ""
      song.tag.save()

    # Add album
    if song.tag.album != dir:
      song.tag.album = dir # Add the directory name as the song's album
      song.tag.save()
      print("{:<8} {:<15}".format(f"Added to {dir}:", fileName[:-4]))

    q.task_done()


# For each song in each directory
for dir in dirs:
  if dir[0] != '_':
    for fileName in os.listdir(dir):
      q.put(os.path.join(dir, fileName))

# Create and start threads
for t in range(nthreads):
    worker = Thread(target=processSong)
    worker.daemon = True # Destroy child thread when main is closed
    worker.start()

q.join() # Hang main thread until queue is empty