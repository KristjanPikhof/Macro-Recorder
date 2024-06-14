import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import webbrowser
import os
import sys
from ttkthemes import ThemedTk, ThemedStyle

from recorder import Recorder, HotKeyManager
from playback import PlaybackManager
from tooltip import ToolTip

def resource_path(relative_path):
    """Get the correct path to a resource file"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

icon_path = resource_path('media/esmaabi_icon.ico')

def status(text):
    return f"Status: {text}"

class App(ThemedTk):
    def __init__(self):
        super().__init__()
        self.title("Macro Mouse Recorder")
        self.configure(bg="#f5f6f8")
        self.geometry("420x490")

        self.iconbitmap(icon_path)

        self.style = ThemedStyle(self)
        # print(self.style.theme_names())  # Print available themes
        self.style.set_theme("yaru")
        self.style.configure('TLabel', background='#f5f6f8')
        self.style.configure('My.TLabel', background='#f5f6f8')  # Custom style to be used

        self.recorder = Recorder()
        self.playback_manager = PlaybackManager()

        self.init_ui()

        self.hotkey_manager = HotKeyManager(
            self.recorder, 
            self.playback_manager,
            self.update_record_button, 
            self.update_playback_button, 
            self.update_recording_list
        )
        
        self.hotkey_thread = threading.Thread(target=self.hotkey_manager.listen_hotkey)
        self.hotkey_thread.daemon = True
        self.hotkey_thread.start()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def init_ui(self):
        control_frame = ttk.Frame(self)
        control_frame.pack(pady=10)

        self.record_button = ttk.Button(control_frame, text="⏺ Start Recording", command=self.toggle_recording)
        self.record_button.grid(row=0, column=1, padx=5, pady=5)
        ToolTip(self.record_button, "Start recording your actions")

        self.play_button = ttk.Button(control_frame, text="▶️ Start Playback", command=self.toggle_playback)
        self.play_button.grid(row=0, column=2, padx=5, pady=5)
        ToolTip(self.play_button, "Play back the recorded actions")

        self.delete_button = ttk.Button(control_frame, text="❌ Delete Recording", command=self.delete_recording)
        self.delete_button.grid(row=0, column=3, padx=5, pady=5)
        ToolTip(self.delete_button, "Delete the selected recording")

        self.playback_speed_label = ttk.Label(control_frame, text="Playback Speed:", style='My.TLabel')
        self.playback_speed_label.grid(row=1, column=1, padx=5, pady=5, sticky="e")
        ToolTip(self.playback_speed_label, "Adjust the playback speed of recordings from 0.1x to 10x.")

        self.playback_speed_slider = ttk.Scale(control_frame, from_=0.1, to=10.0, orient='horizontal', value=1.0, command=self.update_speed)
        self.playback_speed_slider.grid(row=1, column=2, padx=5, pady=5, sticky="ew")

        # Use ttk.Label with custom style for background color
        self.speed_value_label = ttk.Label(control_frame, text="1.0x", style='My.TLabel')
        self.speed_value_label.grid(row=1, column=3, padx=5, pady=5)

        # Updated recording list UI
        list_frame = ttk.Frame(self)
        list_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_columnconfigure(1, weight=1)

        self.left_list = tk.Listbox(list_frame, bg="#1e1e1e", fg="#ffffff", selectbackground="#3c3f41", selectforeground="#ffffff", font=("Helvetica", 12)) 
        self.left_list.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.right_list = tk.Listbox(list_frame, bg="#1e1e1e", fg="#ffffff", selectbackground="#3c3f41", selectforeground="#ffffff", font=("Helvetica", 12)) 
        self.right_list.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        # Configuring status label to use the same background color
        self.status_label = tk.Label(self, text=status("Idle"), bg='#f5f6f8', font=("Helvetica", 12))
        self.status_label.pack(pady=10)

        # Menubar setup
        menubar = tk.Menu(self)
        
        # File menu
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Save Recordings", command=self.save_recordings)
        filemenu.add_command(label="Load Recordings", command=self.load_recordings)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.on_closing)
        menubar.add_cascade(label="File", menu=filemenu)

        # Help menu
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=self.show_about_window)
        menubar.add_cascade(label="Help", menu=helpmenu)
        
        self.config(menu=menubar)

    def show_about_window(self):
        about_window = tk.Toplevel(self)
        about_window.title("About")
        about_window.geometry("600x425")
        about_window.configure(bg="#f5f6f8")
        about_window.iconbitmap(icon_path)

        # Emphasizing the description
        description_title = ttk.Label(about_window, text="About this Application", font=("Helvetica", 16, "bold"), background="#f5f6f8")
        description_title.pack(pady=(20, 10), padx=20)

        description = """
        This application allows you to record and playback mouse and keyboard actions.
        Here are the key functionalities:

        ⏺ Start Recording (F8): Start recording your actions.
        ⏹ Stop Recording (F8): Stop recording.
        ▶️ Start Playback (F9): Play back the recorded actions.
        ⏹️ Stop Playback (F9): Stop the playback.
        ❌ Delete Recording: Delete the selected recording.
             - If you select a recording, only the selected one will be deleted.
             - Otherwise, all recordings will be deleted.
        🔁 Playback Speed: Use the slider to adjust the playback speed.
        📁 Save Recordings: Save your recordings to a file using the File menu.
        📂 Load Recordings: Load your recordings from a file using the File menu.
        🔄 Recordings will be played in random order.
        """

        # Create a frame for more control over placement
        content_frame = ttk.Frame(about_window, padding=(20, 10), style="Content.TFrame")
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Create a text area for the description
        description_label = tk.Label(content_frame, text=description.strip(), anchor="w", justify="left", background="#f5f6f8", font=("Helvetica", 11))
        description_label.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Adding the GitHub link
        github_label = tk.Label(content_frame, text="GitHub: github.com/KristjanPikhof", fg="#0078D7", cursor="hand2", bg="#f5f6f8", font=("Helvetica", 10, "bold"))
        github_label.pack(pady=(10, 20))
        github_label.bind("<Button-1>", lambda e: webbrowser.open_new("https://github.com/KristjanPikhof"))

    def toggle_recording(self):
        if self.recorder.is_recording:
            self.recorder.stop_recording()
            self.record_button.config(text="⏺ Start Recording")
            self.update_status("Recording stopped.")
        else:
            self.recorder.start_recording()
            self.record_button.config(text="⏹ Stop Recording")
            self.update_status("Recording started...")

        self.update_recording_list()

    def toggle_playback(self):
        speed = self.playback_speed_slider.get()
        if self.playback_manager.is_playing:
            self.playback_manager.stop_playback()
            self.play_button.config(text="▶️ Start Playback")
            self.update_status("Playback stopped.")
        else:
            self.playback_manager.start_playback(self.recorder.recordings, speed_factor=speed)
            self.play_button.config(text="⏹️ Stop Playback")
            self.update_status("Playback started...")

    def delete_recording(self):
        selected_idx = self.left_list.curselection() or self.right_list.curselection()
        if selected_idx:
            listbox = self.left_list if self.left_list.curselection() else self.right_list
            confirm = messagebox.askyesno(title="Confirm Delete", message="Are you sure you want to delete the selected recording?")
            if confirm:
                idx = selected_idx[0]
                if listbox == self.right_list:
                    idx += 10
                del self.recorder.recordings[idx]
                self.update_status(f"Recording {idx + 1} deleted.")
                self.update_recording_list()
        else:
            confirm = messagebox.askyesno(title="Confirm Delete All", message="Are you sure you want to delete all recordings?")
            if confirm:
                self.recorder.recordings.clear()
                self.update_status("All recordings deleted.")
                self.update_recording_list()

    # Update update_recording_list to clear selection
    def update_recording_list(self):
        self.left_list.delete(0, tk.END)
        self.right_list.delete(0, tk.END)
        
        for idx, recording in enumerate(self.recorder.recordings):
            listbox = self.left_list if idx < 10 else self.right_list
            listbox.insert(tk.END, f"Recording {idx + 1}: {len(recording)} points")

    def update_status(self, text):
        self.status_label.config(text=status(text))

    def save_recordings(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            try:
                self.recorder.save_recordings(file_path)
                self.update_status(f"✅ Recordings saved to {file_path}")
                self.update_recording_list()
            except Exception as e:
                messagebox.showerror(title="Error", message=f"🔴 Failed to save recordings: {e}")

    def load_recordings(self):
        file_path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            try:
                self.recorder.load_recordings(file_path)
                self.update_status(f"✅ Recordings loaded from {file_path}")
                self.update_recording_list()
            except Exception as e:
                messagebox.showerror(title="Error", message=f"🔴 Failed to load recordings: {e}")

    def update_speed(self, value):
        speed = float(value)
        if 0.1 <= speed <= 10.0:
            self.playback_manager.speed_factor = speed
            self.speed_value_label.config(text=f"{speed:.1f}x")
        else:
            self.playback_speed_slider.set(self.playback_manager.speed_factor)
            messagebox.showwarning("🔴 Invalid Speed", "Playback speed must be between 0.1 and 10.0.")

    def on_closing(self):
        self.hotkey_manager.stop_listening()
        self.hotkey_thread.join()
        self.destroy()

    def update_record_button(self):
        if self.recorder.is_recording:
            self.record_button.config(text="⏹️ Stop Recording")
            self.update_status("Recording started...")
        else:
            self.record_button.config(text="⏺ Start Recording")
            self.update_status("Recording stopped.")
            self.update_recording_list()

    def update_playback_button(self):
        if self.playback_manager.is_playing:
            self.play_button.config(text="⏹️ Stop Playback")
            self.update_status("Playback started...")
        else:
            self.play_button.config(text="▶️ Start Playback")
            self.update_status("Playback stopped.")

    def update_recording_list(self):
        self.left_list.delete(0, tk.END)
        self.right_list.delete(0, tk.END)
        
        for idx, recording in enumerate(self.recorder.recordings):
            listbox = self.left_list if idx < 15 else self.right_list
            listbox.insert(tk.END, f"Recording {idx + 1}: {len(recording)} points")

if __name__ == "__main__":
    app = App()
    app.mainloop()