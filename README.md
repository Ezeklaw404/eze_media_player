# Eze Media Player (Media Queue Launcher)

A clean, dark-mode desktop media explorer built with Python and CustomTkinter. It allows you to navigate through your media library directories, track your watched history persistently, and launch unwatched content directly into VLC.

---

## Features

* **Double-Click Navigation:** Quick directory diving with an intuitive history back-stack.
* **Smart Right-Click Toggle:** Right-click any file or folder to toggle its "watched" state (turns font gray).
* **Persistent History:** Your targeted root directory, VLC path, and watch history save automatically to a local `config.json` file.
* **Smart Folder Queuing:** Clicking play (`▷`) on a folder scans deeply and automatically streams **only your unwatched files** straight into VLC.
* **Auto-Wrap Layout:** File and folder names intelligently fill up the application layout space without ugly truncation.

---

## Setup & Requirements

1. **Install Python 3.x**
2. **Install dependencies:**
```bash
   pip install customtkinter


Configuration & First-Time Setup
To ensure the application initializes immediately without warning screens or errors, the local config.json requires two paths to be configured:

1. VLC Executable Path (vlc_path)
On your very first launch, the app will immediately open a file explorer window asking you to locate vlc.exe. You must select a valid VLC executable here.

2. Media Target Folder (base_folder_path)
Once inside the app, click the folder icon (📁) at the top left to choose your media root directory.