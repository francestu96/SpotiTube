import urllib.request
import spotipy
import pytube
import string
import json
import re
from pathlib import Path
from spotipy.oauth2 import SpotifyClientCredentials

try:
  credentials = json.load(open('credentials.json'))
except Exception as e:
  print(e)

CLIENT_ID = credentials['client_id']
CLIENT_SECRET = credentials['client_secret']
YOUTUBE_QUERY_URL = "https://www.youtube.com/results?search_query="
YOUTUBE_WATCH_URL = "https://www.youtube.com/watch?v="
DESTINATION = "playlists/"

def get_tracks(playlist_id):
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

client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

playlist_link = input("Enter the playlist link: ")
playlist_id = playlist_link.split("/")[-1].split("?")[0]
playlist_name = sp.user_playlist(user=None, playlist_id=playlist_id, fields="name")["name"] + "/"

tracks = get_tracks(playlist_id)

for track in tracks:
    search_keyword = track[0] + "+" + " ".join(track[1])
    html = urllib.request.urlopen(urllib.parse.quote(YOUTUBE_QUERY_URL + search_keyword.replace(" ", "+"), safe=string.printable))
    video_id = re.findall(r"watch\?v=(\S{11})", html.read().decode())[0]
    filename = DESTINATION + playlist_name + track[0] + "(" + ";".join(track[1]) + ")" + ".mp3"
    Path(DESTINATION + playlist_name).mkdir(parents=True, exist_ok=True)
    pytube.YouTube(YOUTUBE_WATCH_URL + video_id).streams.filter(only_audio=True).first().download(filename=filename)