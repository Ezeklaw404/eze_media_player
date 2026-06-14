# Eze Media Player

A clean, dark-mode desktop media explorer built with Python and CustomTkinter. It allows you to navigate through your media library directories, track your watched history persistently, and launch unwatched content directly into VLC.

---

## Features

* **Double-Click Navigation:** Quick directory diving with an intuitive history back-stack.
* **Smart Right-Click Toggle:** Right-click any file or folder to toggle its \"watched\" state (turns font gray).
* **Persistent History:** Your targeted root directory, VLC path, and watch history save automatically to a local \`config.json\` file.
* **Smart Folder Queuing:** Clicking play (\`▷\`) on a folder scans deeply and automatically streams **only your unwatched files** straight into VLC.
* **Auto-Wrap Layout:** File and folder names intelligently fill up the application layout space without ugly truncation.
* **Automated Playback Tracking:** Connects directly to VLC's local host interface to automatically mark files as watched once playback crosses 85% completion.

---

## Setup & Requirements

1. **Install Python 3.x**
2. **Install dependencies:**
   \`\`\`bash
   pip install customtkinter
   \`\`\`

---

## Download Link - Executable

* [GitHub Releases](https://github.com/Ezeklaw404/eze_media_player/releases)

---

## Configuration & First-Time Setup

To ensure the application initializes immediately without warning screens or errors, the local \`config.json\` requires two paths and an interface password to be configured:

### 1. VLC HTTP Interface & Password (`vlc_password`)
To enable automatic "mark as watched" tracking, you must configure VLC's built-in web server so the application can communicate with it in the background:

1. Open **VLC Media Player** and navigate to **Tools** -> **Preferences** (or press `Ctrl + P`).
2. At the bottom-left corner under *Show settings*, select the **All** radio button to unlock advanced settings.
3. In the left-hand sidebar, scroll down to **Interface**, expand **Main interfaces**, and check the box next to **Web**.
4. Dive deeper into the left sidebar: expand **Main interfaces** completely, click on **Lua**, and look for the **Lua HTTP** section.
5. Enter a password of your choice (e.g., `1234`) into the **Password** field and click **Save**. It is Localhost so it doesn't need to be secure
6. Restart VLC completely to apply the changes.

The very first time your app runs after this setup, a pop-up window will request this exact password. Once entered, it saves securely inside your local `config.json` file for all future automated playback tracking.

### 2. VLC Executable Path (\`vlc_path\`)
On your very first launch, the app will immediately open a file explorer window asking you to locate \`vlc.exe\`. You **must** select a valid VLC executable here.

### 3. Media Target Folder (\`base_folder_path\`)
Once inside the app, click the folder icon (\`📁\`) at the top left to choose your media root directory.'''
