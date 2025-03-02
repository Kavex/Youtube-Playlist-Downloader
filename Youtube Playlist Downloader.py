# pip install yt-dlp tk

import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import yt_dlp

# Common YouTube resolutions
RESOLUTIONS = {
    "2160p (4K)": "bestvideo[height<=2160]+bestaudio/best",
    "1440p": "bestvideo[height<=1440]+bestaudio/best",
    "1080p (Full HD)": "bestvideo[height<=1080]+bestaudio/best",
    "720p (HD)": "bestvideo[height<=720]+bestaudio/best",
    "480p": "bestvideo[height<=480]+bestaudio/best",
    "360p": "bestvideo[height<=360]+bestaudio/best",
    "240p": "bestvideo[height<=240]+bestaudio/best"
}

def log_message(message):
    """Function to log messages to the console window"""
    console_text.insert(tk.END, message + "\n")
    console_text.see(tk.END)

def download_playlist():
    url = url_entry.get().strip()
    if not url:
        messagebox.showerror("Error", "Please enter a YouTube playlist URL")
        return

    folder = folder_path.get()
    if not folder:
        messagebox.showerror("Error", "Please select a download folder")
        return

    resolution = resolution_var.get()
    format_code = RESOLUTIONS.get(resolution, "best")

    log_message(f"📂 Downloading playlist to: {folder}")
    log_message(f"🎥 Selected resolution: {resolution}")

    def run_download():
        ydl_opts = {
            'outtmpl': os.path.join(folder, '%(title)s.%(ext)s'),
            'format': format_code,
            'merge_output_format': 'mp4',
            'progress_hooks': [progress_hook],
            'noplaylist': False
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([url])
                log_message("✅ Download complete!")
                messagebox.showinfo("Success", "Playlist download complete!")
            except Exception as e:
                log_message(f"❌ Error: {e}")
                messagebox.showerror("Download Failed", str(e))

    threading.Thread(target=run_download, daemon=True).start()

def progress_hook(d):
    """Handles download progress updates"""
    if d['status'] == 'downloading':
        log_message(f"⬇️ Downloading: {d['filename']} - {d['_percent_str']}")

def choose_folder():
    """Opens folder selection dialog"""
    folder_selected = filedialog.askdirectory()
    folder_path.set(folder_selected)

# GUI Setup
root = tk.Tk()
root.title("YouTube Playlist Downloader (yt-dlp)")
root.geometry("600x450")

# URL Input
tk.Label(root, text="YouTube Playlist URL:").pack(pady=5)
url_entry = tk.Entry(root, width=60)
url_entry.pack(pady=5)

# Folder Selection
tk.Label(root, text="Download Folder:").pack(pady=5)
folder_path = tk.StringVar()
folder_entry = tk.Entry(root, textvariable=folder_path, width=45, state="readonly")
folder_entry.pack(pady=5)
tk.Button(root, text="Choose Folder", command=choose_folder).pack(pady=5)

# Resolution Selection (Dropdown)
tk.Label(root, text="Select Video Resolution:").pack(pady=5)
resolution_var = tk.StringVar(value="1080p (Full HD)")
resolution_dropdown = ttk.Combobox(root, textvariable=resolution_var, values=list(RESOLUTIONS.keys()), state="readonly")
resolution_dropdown.pack(pady=5)

# Download Button
download_button = tk.Button(root, text="Download Playlist", command=download_playlist, bg="red", fg="white")
download_button.pack(pady=10)

# Console Output
tk.Label(root, text="Download Console:").pack(pady=5)
console_text = scrolledtext.ScrolledText(root, width=70, height=10, state="normal")
console_text.pack(pady=5)

# Status Label
status_label = tk.Label(root, text="", fg="black")
status_label.pack(pady=5)

# Run the GUI
root.mainloop()
