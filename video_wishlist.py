import os
import subprocess
from pathlib import Path
import customtkinter as ctk
from tkinter import filedialog


# vlc = r"C:/Program Files (x86)/VideoLAN/VLC/vlc.exe"
# desktop
vlc = r"C:\Program Files\VideoLAN\VLC\vlc.exe"

CONFIG_FILE = "config.txt"



# ui for seeing folders files, selectable, next btn. drag and drop to reorder

# mark as watched to unselect. local stora

class FileObject:
    def __init__(self, name, path):
        self.name = name
        self.path = Path(path)
        self.watched = False
        self.isFolder = self.path.is_dir()



# Set up clean dark mode styling
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")



class MediaApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Media Queue Launcher")
        self.geometry("600x500")
        
        # --- Configurable Paths ---
        self.vlc_path = Path(vlc) # Adjust if 64-bit
        self.base_url = self.load_saved_path()
        
        # --- Data State ---
        self.media_items = []
        
        # --- Layout Components ---
        self.setup_ui()


        if self.base_url:
            self.load_media_items()
        
        

    def load_saved_path(self):
        """Reads the saved path string from config.txt if it exists."""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved_path = f.read().strip()
                if saved_path and os.path.exists(saved_path):
                    return Path(saved_path)
        return None

    def save_path_to_txt(self, path_str):
        """Overwrites config.txt with the newly chosen file location."""
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            f.write(path_str)

    def choose_folder(self):
        """Opens a native Windows browser window to pick a media directory."""
        chosen_dir = filedialog.askdirectory(title="Select Media Target Folder")
        if chosen_dir:
            self.base_url = Path(chosen_dir)
            self.save_path_to_txt(chosen_dir)
            
            # Update path label in UI and refresh contents
            self.path_label.configure(text=f"Folder: {self.base_url.name}")
            self.load_media_items()


    def load_media_items(self):
        """Scans the designated directory and renders items inside the GUI."""
        # Clear out any old list items and visual rows first
        self.media_items.clear()
        for child in self.scroll_frame.winfo_children():
            child.destroy()
            
        if not self.base_url or not self.base_url.exists():
            return
            
        for item in self.base_url.iterdir():
            if not item.name.startswith('.'):
                file_obj = FileObject(name=item.name, path=item)
                self.media_items.append(file_obj)
                self.create_item_row(file_obj)

    def setup_ui(self):
        # 1. Top Settings Bar (Picker & Feedback)
        top_bar = ctk.CTkFrame(self)
        top_bar.pack(fill="x", padx=20, pady=15)
        
        folder_display_text = f"Folder: {self.base_url.name}" if self.base_url else "No Folder Selected"
        self.path_label = ctk.CTkLabel(top_bar, text=folder_display_text, font=ctk.CTkFont(weight="bold"))
        self.path_label.pack(side="left", padx=15, pady=10)
        
        browse_btn = ctk.CTkButton(top_bar, text="Change Folder", width=110, command=self.choose_folder)
        browse_btn.pack(side="right", padx=15, pady=10)

        # 2. Scrollable Frame for Media Items
        self.scroll_frame = ctk.CTkScrollableFrame(self, width=560, height=380)
        self.scroll_frame.pack(pady=5, padx=20, fill="both", expand=True)

    def create_item_row(self, item):
        row_frame = ctk.CTkFrame(self.scroll_frame)
        row_frame.pack(fill="x", pady=5, padx=5)
        
        prefix = "📁 " if item.isFolder else "🎬 "
        display_name = item.name if len(item.name) < 55 else f"{item.name[:52]}..."
        
        name_label = ctk.CTkLabel(row_frame, text=f"{prefix} {display_name}", anchor="w")
        name_label.pack(side="left", padx=15, pady=10)
        

        play_btn = ctk.CTkButton(row_frame, text="▷", width=15, command=lambda obj=item: self.launch_media(obj))
        play_btn.pack(side="right", padx=15, pady=10)

    def launch_media(self, media_item):
        """Triggers VLC to open the selected specific file or folder path."""
        if not self.vlc_path.exists():
            print("VLC installation not found!")
            return
            
        print(f"Opening: {media_item.name}")
        subprocess.Popen([str(self.vlc_path), "--playlist-autostart", str(media_item.path)])

if __name__ == "__main__":
    app = MediaApp()
    app.mainloop()