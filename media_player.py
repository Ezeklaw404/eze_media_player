import os
import json
import subprocess
import threading
import time
from pathlib import Path
import customtkinter as ctk
from tkinter import filedialog, dialog
import requests
from requests.auth import HTTPBasicAuth

CONFIG_FILE = "config.json"

class FileObject:
    def __init__(self, name, path):
        self.name = name
        self.path = Path(path)
        self.watched = False
        self.isFolder = self.path.is_dir()


ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class MediaApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Eze Media Player")
        self.geometry("600x500")
        
        # --- Configurable Paths ---
        self.config_data = self.load_config()
        
        self.base_url = Path(self.config_data["base_folder_path"]) if self.config_data["base_folder_path"] else None
        
        config_path_str = self.config_data.get("vlc_path", "")
        self.vlc_path = Path(config_path_str) if config_path_str else None
        
        if not self.vlc_path or not self.vlc_path.is_file():
            chosen_vlc = filedialog.askopenfilename(
                title="Locate vlc.exe",
                filetypes=[("VLC Executable", "vlc.exe"), ("Executable Files", "*.exe")]
            )
            if chosen_vlc:
                self.vlc_path = Path(chosen_vlc)
                self.config_data["vlc_path"] = str(self.vlc_path)
                self.save_config()
            else:
                self.vlc_path = Path("")

        # Check for VLC HTTP Password
        if not self.config_data.get("vlc_password"):
            self.request_vlc_password()

        self.current_dir = self.base_url
        self.history = []                     
        self.media_items = []
        
        # --- Layout Components ---
        self.setup_ui()

        if self.base_url:
            self.load_media_items()
            
        # --- Start Background VLC Monitor ---
        self.monitor_thread = threading.Thread(target=self.monitor_vlc_status, daemon=True)
        self.monitor_thread.start()

    def load_config(self):
        """Loads app configurations and history tracking list from JSON."""
        default_structure = {
            "vlc_path": "",
            "vlc_password": "",
            "base_folder_path": "",
            "watched_paths": []
        }
        
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                    for key, val in default_structure.items():
                        if key not in data:
                            data[key] = val
                    return data
            except Exception:
                return default_structure
        return default_structure

    def save_config(self):
        save_data = {
            "vlc_path": str(self.vlc_path),
            "vlc_password": self.config_data.get("vlc_password", ""),
            "base_folder_path": str(self.base_url) if self.base_url else "",
            "watched_paths": self.config_data["watched_paths"]
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(save_data, f, indent=4)

    def request_vlc_password(self):
        """Simple popup dialog to get the VLC Lua HTTP password."""
        dialog = ctk.CTkInputDialog(text="Enter your VLC HTTP Lua Password:", title="VLC Connection")
        password = dialog.get_input()
        if password:
            self.config_data["vlc_password"] = password
            self.save_config()

    def is_path_watched(self, item_path):
        item_path_str = str(Path(item_path).resolve())
        for watched_str in self.config_data["watched_paths"]:
            w_path = str(Path(watched_str).resolve())
            if item_path_str == w_path or item_path_str.startswith(w_path + os.sep):
                return True
        return False
    
    def choose_folder(self):
        chosen_dir = filedialog.askdirectory(title="Select Media Target Folder")
        if chosen_dir:
            self.base_url = Path(chosen_dir)
            self.current_dir = self.base_url
            self.history.clear()
            self.save_config()
            self.update_ui_state()
            self.load_media_items()

    def load_media_items(self):
        self.media_items.clear()
        self.scroll_frame.pack_forget()
        
        for child in self.scroll_frame.winfo_children():
            child.destroy()
            
        if not self.base_url or not self.base_url.exists():
            self.scroll_frame.pack(pady=5, padx=20, fill="both", expand=True)
            return
            
        try:
            for item in self.current_dir.iterdir():
                if not item.name.startswith('.'):
                    watched_status = self.is_path_watched(item)
                    file_obj = FileObject(name=item.name, path=item)
                    file_obj.watched = watched_status
                    self.media_items.append(file_obj)
                    self.create_item_row(file_obj)
        except PermissionError:
            print(f"Permission denied accessing: {self.current_dir}")
            self.go_back()
        
        self.scroll_frame.pack(pady=5, padx=20, fill="both", expand=True)

    def setup_ui(self):
        top_bar = ctk.CTkFrame(self)
        top_bar.pack(fill="x", padx=20, pady=15)
        
        self.back_btn = ctk.CTkButton(top_bar, text="⬅", width=35, command=self.go_back, state="disabled")
        self.back_btn.pack(side="left", padx=5, pady=10)

        self.browse_btn = ctk.CTkButton(top_bar, text="📁", width=35, command=self.choose_folder)
        self.browse_btn.pack(side="left", padx=5, pady=10)

        folder_display_text = f"../{self.base_url.name}" if self.base_url else "No Folder Selected"
        self.path_label = ctk.CTkLabel(top_bar, text=folder_display_text, font=ctk.CTkFont(weight="bold"))
        self.path_label.pack(side="left", padx=10, pady=10)

        self.scroll_frame = ctk.CTkScrollableFrame(self, width=560, height=380)
        self.scroll_frame.pack(pady=5, padx=20, fill="both", expand=True)

    def update_ui_state(self):
        if self.current_dir and self.base_url:
            if self.current_dir == self.base_url:
                self.path_label.configure(text=f"../{self.base_url.name}")
            else:
                relative_path = self.current_dir.relative_to(self.base_url).as_posix()
                full_display_path = f"../{self.base_url.name}/{relative_path}"
                self.path_label.configure(text=full_display_path)
        
        if self.history:
            self.back_btn.configure(state="normal")
        else:
            self.back_btn.configure(state="disabled")
        self.browse_btn.configure(state="normal")

    def create_item_row(self, item):
        row_frame = ctk.CTkFrame(self.scroll_frame)
        row_frame.pack(fill="x", pady=5, padx=5)
        
        prefix = "📁 " if item.isFolder else "🎬 "
        display_name = f"{prefix} {item.name}"
        
        play_btn = ctk.CTkButton(row_frame, text="▷", width=15, command=lambda obj=item: self.launch_media(obj))
        play_btn.pack(side="left", padx=5, pady=0)

        name_label = ctk.CTkLabel(row_frame, text=display_name, anchor="w", wraplength=450)
        name_label.pack(side="left", padx=5, pady=0, fill="x", expand=True)
        
        if item.watched:
            name_label.configure(text_color="#808080")
            
        if item.isFolder:
            row_frame.bind("<Double-1>", lambda event, obj=item: self.navigate_into(obj))
            name_label.bind("<Double-1>", lambda event, obj=item: self.navigate_into(obj))
            
        row_frame.bind("<Button-3>", lambda event, lbl=name_label, obj=item: self.mark_as_watched(lbl, obj))
        name_label.bind("<Button-3>", lambda event, lbl=name_label, obj=item: self.mark_as_watched(lbl, obj))

        row_frame.configure(cursor="hand2")
        name_label.configure(cursor="hand2")

    def mark_as_watched(self, label, media_item):
        path_str = str(media_item.path.resolve())
        
        if path_str in self.config_data["watched_paths"]:
            self.config_data["watched_paths"].remove(path_str)
            media_item.watched = False
            if label: label.configure(text_color="#FFFFFF")
        else:
            self.config_data["watched_paths"].append(path_str)
            media_item.watched = True
            if label: label.configure(text_color="#808080")
            
        self.save_config()
            
        if media_item.isFolder:
            self.load_media_items()

    def show_loading(self, message):
        self.back_btn.configure(state="disabled")
        self.browse_btn.configure(state="disabled")
        self.path_label.configure(text=f"⏳ {message}...")
        self.update_idletasks()

    def navigate_into(self, folder_item):
        self.show_loading("Loading Directory")
        self.history.append(self.current_dir) 
        self.current_dir = folder_item.path    
        self.update_ui_state()
        self.load_media_items()

    def go_back(self):
        if self.history:
            self.show_loading("Loading Directory")
            self.current_dir = self.history.pop() 
            self.update_ui_state()
            self.load_media_items()

    def launch_media(self, media_item):
        if not self.vlc_path or not self.vlc_path.is_file():
            chosen_vlc = filedialog.askopenfilename(
                title="Locate vlc.exe",
                filetypes=[("VLC Executable", "vlc.exe"), ("Executable Files", "*.exe")]
            )
            if chosen_vlc:
                self.vlc_path = Path(chosen_vlc)
                self.config_data["vlc_path"] = str(self.vlc_path)
                self.save_config()
            else:
                return
            
        cmd = [str(self.vlc_path), "--playlist-autostart"]
        
        if media_item.isFolder:
            self.show_loading("Opening playlist")
            unwatched_files = []
            try:
                for file_path in media_item.path.rglob("*"):
                    if file_path.is_file() and not file_path.name.startswith('.'):
                        if not self.is_path_watched(file_path):
                            unwatched_files.append(str(file_path))
            except Exception:
                self.update_ui_state()
                return
                
            if not unwatched_files:
                self.update_ui_state()
                return
                
            cmd.extend(unwatched_files)
        else:
            self.show_loading("Opening video")
            cmd.append(str(media_item.path))
            
        subprocess.Popen(cmd)
        self.after(1500, self.update_ui_state)

    def monitor_vlc_status(self):
        """Runs on a background thread checking VLC's playback position."""
        vlc_url = "http://localhost:8080/requests/status.json"
        
        while True:
            password = self.config_data.get("vlc_password", "")
            if password:
                try:
                    response = requests.get(vlc_url, auth=HTTPBasicAuth('', password), timeout=1.5)
                    if response.status_code == 200:
                        data = response.json()
                        position = data.get("position", 0.0) # Scale of 0.0 to 1.0
                        meta = data.get("information", {}).get("category", {}).get("meta", {})
                        
                        # VLC returns filename, or occasionally absolute URI/filepath parameters
                        filename = meta.get("filename") or meta.get("filename_vlc")
                        
                        # If a video is playing and is over 90% complete
                        if filename and position > 0.9:
                            self.auto_mark_by_name(filename)
                except Exception:
                    pass # VLC status server is closed or not responding right now
            time.sleep(3)

    def auto_mark_by_name(self, filename):
        """Scans the active pool for a matching file name to safely auto-flag it."""
        for item in self.media_items:
            if not item.isFolder and item.path.name == filename:
                if not item.watched:
                    # Thread-safe color update handling back to the Tkinter UI execution loop
                    self.after(0, lambda obj=item: self.mark_as_watched(None, obj))
                    self.after(50, self.load_media_items)
                    break


if __name__ == "__main__":
    app = MediaApp()
    app.mainloop()



# -------------future notes-------------
# when marking a folder as watched, add each item individually, and not just the folder path