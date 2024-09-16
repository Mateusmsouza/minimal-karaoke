import os
import subprocess
import tkinter as tk
from tkinter import Listbox, Scrollbar, Button, Label, END, Scale, HORIZONTAL
from ffpyplayer.player import MediaPlayer
from PIL import Image, ImageTk
from ffpyplayer.pic import Image as FFImage


CONFIG_FILE = 'config.txt'

class KaraokePlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Karaoke Player")
        
        self.current_dir = self.load_initial_directory()
        self.initial_dir = self.current_dir
        if not self.current_dir:
            self.current_dir = os.path.expanduser("~")  # Use home directory as default

        # Frame for directory path display
        path_frame = tk.Frame(root)
        path_frame.pack(pady=10)

        self.path_label = tk.Label(path_frame, text=self.current_dir)
        self.path_label.pack()

        # Frame for video and folder list
        list_frame = tk.Frame(root)
        list_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        scrollbar = Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.item_listbox = Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.item_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.item_listbox.bind("<Double-1>", self.on_item_selected)  # Bind double click

        scrollbar.config(command=self.item_listbox.yview)

        # Navigation buttons
        nav_frame = tk.Frame(root)
        nav_frame.pack(pady=10)

        self.back_button = Button(nav_frame, text="Voltar", command=self.go_back)
        self.back_button.pack(side=tk.LEFT, padx=10)
        
        self.play_button = Button(nav_frame, text="Play", command=self.play_video)
        self.play_button.pack(side=tk.LEFT, padx=10)

        # Volume control
        self.volume_slider = Scale(nav_frame, from_=0, to=100, orient=HORIZONTAL, label="Volume", command=self.set_volume)
        self.volume_slider.set(50)  # Set default volume to 50%
        self.volume_slider.pack(side=tk.LEFT, padx=10)

        # Video display
        self.video_label = Label(root)
        self.video_label.pack(pady=10)

        self.player = None
        self.fullscreen = True
        self.load_directory(self.current_dir)

    def load_initial_directory(self):
        config_file = 'config.txt'
        if os.path.exists(config_file):
            with open(config_file, 'r') as file:
                directory = file.readline().strip()
                if os.path.isdir(directory):
                    return directory
        return None

    def load_directory(self, directory):
        self.current_dir = directory
        self.path_label.config(text=self.current_dir)
        self.item_listbox.delete(0, END)

        # List directories first
        for item in sorted(os.listdir(directory)):
            item_path = os.path.join(directory, item)
            if os.path.isdir(item_path):
                self.item_listbox.insert(END, "[DIR] " + item)

        # List videos second
        for item in sorted(os.listdir(directory)):
            item_path = os.path.join(directory, item)
            if os.path.isfile(item_path) and item.endswith(('.mp4', '.mkv', '.avi')):
                self.item_listbox.insert(END, item)

    def on_item_selected(self, event):
        selected_item = self.item_listbox.get(tk.ACTIVE)
        item_name = selected_item.replace("[DIR] ", "")
        selected_path = os.path.join(self.current_dir, item_name)

        if os.path.isdir(selected_path):
            self.load_directory(selected_path)
        else:
            self.play_video()

    def go_back(self):
        if self.player:
            self.stop_video()  # Stop the video when going back

        parent_dir = os.path.dirname(self.current_dir)
        if self.initial_dir in parent_dir:
            self.load_directory(parent_dir)
        #if parent_dir != self.current_dir:  # Prevent going beyond root
        #    self.load_directory(parent_dir)

    def play_video(self):
        selected_item = self.item_listbox.get(tk.ACTIVE)
        item_name = selected_item.replace("[DIR] ", "")
        video_path = os.path.join(self.current_dir, item_name)
        if os.path.isfile(video_path):
            self.start_video(video_path)

    def start_video(self, path):
        if self.player:
            self.player.close_player()

        self.player = MediaPlayer(path, callback=self.video_callback)
        self.player.set_size(width=1280, height=720)
        self.set_volume(self.volume_slider.get())  # Set initial volume
        self.update_frame()

    def stop_video(self):
        if self.player:
            self.player.close_player()
            self.player = None
            self.video_label.imgtk = None
            self.video_label.config(image=None)

    def set_volume(self, volume):
        if self.player:
            volume = int(volume) / 100
            self.player.set_volume(volume)

    def video_callback(self, frame):
        # Optional: Handle callback events from the player, if needed
        pass

    def update_frame(self):
        if self.player:
            frame, val = self.player.get_frame()
            if frame is not None:
                img, t = frame

                if isinstance(img, FFImage):
                    img_bytes = img.to_bytearray()[0]
                    img = Image.frombytes('RGB', img.get_size(), img_bytes, 'raw', 'RGB', 0, 1)
                
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_label.imgtk = imgtk
                self.video_label.config(image=imgtk)
            
            if val != 'eof':
                self.root.after(10, self.update_frame)
            else:
                self.stop_video()  # Stop the video when it ends
