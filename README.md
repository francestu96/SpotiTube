# SpotiTube

Tired of downloading each song of your **Spotify** playlists by hand? **SpotiTube** comes to help you!\
Donwload your **Spotify** playlists automacally!\
\
The script look for your **Spotify** tracks and queries **YouTube** with their names and artists.\
The first result showing up, **will be downloaded**!

# Configuration

In order to make the script works, you need to have a **Spotify account** (Premium not required).\
Once Signed Up, follow the istructions at this [link](https://cran.r-project.org/web/packages/spotidy/vignettes/Connecting-with-the-Spotify-API.html) to get the **client_id** and the **client_secret**.\
Once you have both, create a new **credentials.json** file with this format:

```json
{
    "client_id": "<your_client_id>", 
    "client_secret": "<your_client_secret>"
}
```

# Run

To run the script, launch **py spotitube.py**. It will ask you for the playlist to download. Enter it and wait till the process ends its job!\
\
Enjoy your songs!