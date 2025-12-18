<<<<<<< HEAD
# pip install spotdl spotipy
# spotdl requires FFmpeg
=======
# pip install yt-dlp tk
# pip install ttkbootstrap
>>>>>>> parent of d16cd1b (Update Youtube Playlist Downloader.py)

import os
import sys
import json
import time
import asyncio
import threading
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from concurrent.futures import ThreadPoolExecutor

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# ======================
# CONFIG
# ======================
SPOTIFY_API_DELAY = 30
MAX_DOWNLOAD_WORKERS = 3
BITRATE = "192k"
CACHE_DIR = "spotify_cache"

SpotClientID = "Client ID Here"
SpotClientSecret = "Client Secret Here"

# ======================
# GUI LOGGING
# ======================
def log_message(msg):
    console_text.insert(tk.END, msg + "\n")
    console_text.see(tk.END)

# ======================
# UTIL
# ======================
def safe_name(name):
    return "".join(c for c in name if c not in r'\/:*?"<>|').strip()

# ======================
# SPOTIFY RATE LIMITER
# ======================
class SpotifyRateLimiter:
    def __init__(self, delay):
        self.delay = delay
        self.last_call = 0
        self.lock = asyncio.Lock()

    async def call(self, fn, *args, **kwargs):
        async with self.lock:
            elapsed = time.time() - self.last_call
            if elapsed < self.delay:
                await asyncio.sleep(self.delay - elapsed)

            result = fn(*args, **kwargs)
            self.last_call = time.time()
            return result

# ======================
# CACHE
# ======================
def cache_path(playlist_id):
    os.makedirs(CACHE_DIR, exist_ok=True)
    return os.path.join(CACHE_DIR, f"{playlist_id}.json")

def load_cache(playlist_id):
    path = cache_path(playlist_id)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def save_cache(playlist_id, data):
    with open(cache_path(playlist_id), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# ======================
# SPOTIFY → QUEUE
# ======================
async def fetch_tracks(sp, limiter, playlist_id, queue):
    cached = load_cache(playlist_id)
    if cached:
        log_message("📦 Loaded playlist metadata from cache")
        for track in cached["tracks"]:
            await queue.put(track)
        return

    log_message("🌐 Fetching playlist metadata (rate-limited)")
    meta = await limiter.call(sp.playlist, playlist_id, fields=["name"])
    log_message(f"🎵 Playlist: {meta['name']}")

    results = await limiter.call(sp.playlist_items, playlist_id)
    tracks = []

    while True:
        for item in results["items"]:
            track = item.get("track")
            if not track:
                continue

            artist = track["artists"][0]["name"] if track["artists"] else "Unknown Artist"

            tracks.append({
                "url": track["external_urls"]["spotify"],
                "artist": artist,
                "title": track["name"]
            })

        if not results["next"]:
            break
        results = await limiter.call(sp.next, results)

    save_cache(playlist_id, {"tracks": tracks})
    log_message(f"💾 Cached {len(tracks)} tracks")

    for t in tracks:
        await queue.put(t)

# ======================
# SPOTDL EXECUTION
# ======================
def run_spotdl(track, base_folder, worker_id):
    artist = safe_name(track["artist"])
    out_dir = os.path.join(base_folder, artist)
    os.makedirs(out_dir, exist_ok=True)

    # Template without .mp3 (spotdl adds it automatically)
    output_template = os.path.join(out_dir, "{artist} - {title}")

    cmd = [
        sys.executable, "-m", "spotdl", "download",
        track["url"],
        "--format", "mp3",
        "--bitrate", BITRATE,
        "--output", output_template,
        "--overwrite", "skip"
    ]

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    for line in proc.stdout:
        log_message(f"[W{worker_id}] {line.rstrip()}")

    proc.wait()
    return proc.returncode

# ======================
# WORKER
# ======================
async def download_worker(worker_id, queue, folder, executor):
    loop = asyncio.get_running_loop()
    while True:
        track = await queue.get()
        log_message(f"[W{worker_id}] ⬇️ {track['artist']} – {track['title']}")
        code = await loop.run_in_executor(
            executor,
            run_spotdl,
            track,
            folder,
            worker_id
        )
        if code == 0:
            log_message(f"[W{worker_id}] ✅ Completed")
        else:
            log_message(f"[W{worker_id}] ❌ Failed")
        queue.task_done()

# ======================
# ASYNC CONTROLLER
# ======================
async def async_controller(playlist_id, sp, folder):
    limiter = SpotifyRateLimiter(SPOTIFY_API_DELAY)
    queue = asyncio.Queue()

    executor = ThreadPoolExecutor(max_workers=MAX_DOWNLOAD_WORKERS)
    workers = [
        asyncio.create_task(download_worker(i + 1, queue, folder, executor))
        for i in range(MAX_DOWNLOAD_WORKERS)
    ]

    await fetch_tracks(sp, limiter, playlist_id, queue)
    await queue.join()

    for w in workers:
        w.cancel()
    executor.shutdown(wait=False)

# ======================
# TK CALLBACK
# ======================
def download_playlist():
    playlist_url = url_entry.get().strip()
    folder = folder_path.get()

    if not playlist_url or not folder:
        messagebox.showerror("Error", "Missing playlist URL or folder")
        return

    playlist_id = playlist_url.rstrip("/").split("/")[-1].split("?")[0]

    def runner():
        try:
            auth = SpotifyClientCredentials(
                client_id=client_id_entry.get().strip(),
                client_secret=client_secret_entry.get().strip()
            )
            sp = spotipy.Spotify(auth_manager=auth)
            asyncio.run(async_controller(playlist_id, sp, folder))
            messagebox.showinfo("Done", "All downloads completed")
        except Exception as e:
            log_message(f"❌ {e}")
            messagebox.showerror("Error", str(e))

    threading.Thread(target=runner, daemon=True).start()

# ======================
# GUI
# ======================
root = tk.Tk()
root.title("Spotify Playlist Downloader")
root.geometry("780x650")

tk.Label(root, text="Client ID").pack()
client_id_entry = tk.Entry(root, width=75)
client_id_entry.insert(0, SpotClientID)
client_id_entry.pack()

tk.Label(root, text="Client Secret").pack()
client_secret_entry = tk.Entry(root, width=75)
client_secret_entry.insert(0, SpotClientSecret)
client_secret_entry.pack()

tk.Label(root, text="Spotify Playlist URL").pack()
url_entry = tk.Entry(root, width=85)
url_entry.pack()

folder_path = tk.StringVar()
tk.Label(root, text="Download Folder").pack()
tk.Entry(root, textvariable=folder_path, width=70, state="readonly").pack()
tk.Button(root, text="Choose Folder", command=lambda: folder_path.set(filedialog.askdirectory())).pack()

tk.Button(root, text="Download Playlist", bg="green", fg="white", command=download_playlist).pack(pady=10)

console_text = scrolledtext.ScrolledText(root, width=100, height=28)
console_text.pack()

root.mainloop()
