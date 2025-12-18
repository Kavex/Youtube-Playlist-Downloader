# Youtube-Playlist-Downloader

<img width="705" height="613" alt="image" src="https://github.com/user-attachments/assets/98f4d3d4-7059-4e73-9fbb-89c74d448f25" />

A Python GUI application to download Spotify playlists with async queue-based downloading, organizing all songs by artist, and caching playlist metadata to speed up repeated downloads.

## Features

Download Spotify playlists to your local drive.

Organizes songs by artist: DownloadFolder/Artist Name/Artist Name - Song Title.mp3

* Flat structure — no per-song or per-album subfolders.
* Async queue-based downloading with multiple worker threads for faster downloads.
* Spotify API rate limiting — avoids hitting API limits (1 request every 30 seconds).
* Playlist metadata caching — saves playlist info to disk to reduce repeated API calls.
* Console logging — shows download progress per track in the GUI.
* Skips duplicates if the file already exists.
* Works cross-platform (Windows, macOS, Linux).

## Requirements

- Python 3.10+
- FFmpeg
- spotdl
- spotipy
- Tkinter (usually included with Python)
  
Install the required Python packages using pip:

```bash
  pip install spotdl spotipy
```

Upgrade:

```bash
  pip install --upgrade spotdl spotipy
```
