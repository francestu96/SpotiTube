import urllib.request
import threading
import logging
import spotipy
import pytube
import string
import mutagen
import shutil
import math
import json
import re
from pathlib import Path
from moviepy.editor import *
from spotipy.oauth2 import SpotifyClientCredentials

THREAD_NO = 10
LOGFILE = "errors.log"
DESTINATION = "../"
YOUTUBE_QUERY_URL = "https://www.youtube.com/results?search_query="
YOUTUBE_WATCH_URL = "https://www.youtube.com/watch?v="

def get_tracks(sp, playlist_id):
    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])

    result = []
    for track in tracks:
        track_name = track["track"]["name"]
        track_artists = [x["name"] for x in track["track"]["artists"]]
        result.append((track_name, track_artists))
    
    return result

def save_tracks(tracks, retry=True):
    error_tracks = []
    for track in tracks:
        try:
            search_keyword = track[0] + "+" + " ".join(track[1])
            html = urllib.request.urlopen(urllib.parse.quote(YOUTUBE_QUERY_URL + search_keyword.replace(" ", "+"), safe=string.printable))
            video_id = re.findall(r"watch\?v=(\S{11})", html.read().decode())[0]
            video_file = DESTINATION + playlist_name + "tmp/" + track[0] + ".mp4"
            audio_file = DESTINATION + playlist_name + track[0] + ".mp3"
            Path(DESTINATION + playlist_name + "tmp").mkdir(parents=True, exist_ok=True)
            pytube.YouTube(YOUTUBE_WATCH_URL + video_id).streams.filter(abr = "160kbps").first().download(filename=video_file)
            
            audio = AudioFileClip(video_file)
            audio.write_audiofile(audio_file)
            audio.close()

            metadata = mutagen.File(audio_file, easy=True)
            metadata['title'] = track[0]
            metadata['artist'] = ";".join(track[1])

            metadata.save()
        except Exception as e:
            if(retry):
                logging.error("%s\n Video query: %s", e, search_keyword)
                error_tracks.append(track)
            else:
                logging.error("%s\n File download failed again: %s", e, search_keyword)

    if(len(error_tracks)):
        save_tracks(error_tracks, False)

if __name__ == "__main__":
    try:
        credentials = json.load(open('credentials.json'))
    except Exception as e:
        print(e)
    client_id = credentials['client_id']
    client_secret = credentials['client_secret']

    logging.basicConfig(filename=LOGFILE, filemode='a', format="%(asctime)s: %(message)s", level=logging.ERROR, datefmt="%H:%M:%S")

    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    playlist_link = input("Enter the playlist link: ")
    playlist_id = playlist_link.split("/")[-1].split("?")[0]
    playlist_name = sp.user_playlist(user=None, playlist_id=playlist_id, fields="name")["name"] + "/"

    tracks = get_tracks(sp, playlist_id)

    threads = []
    for x in range(THREAD_NO):
        start = x * math.ceil(len(tracks) / THREAD_NO)
        end = start + math.ceil(len(tracks) / THREAD_NO)
        threads.append(threading.Thread(target=save_tracks, args=(tracks[start:end],)))
        threads[-1].start()

    for x in threads:
        x.join()

    shutil.rmtree(DESTINATION + playlist_name + "tmp")