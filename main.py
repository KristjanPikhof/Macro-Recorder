import json
import threading
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox
from recorder import Recorder, HotKeyManager
from playback import PlaybackManager

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Macro Mouse Recorder")
        self.configure(bg="#1e1e1e")
        self.geometry("600x600")

        self.recorder = Recorder()
        self.playback_manager = PlaybackManager()

        self.init_ui()

        self.hotkey_manager = HotKeyManager(self.recorder, self.playback_manager,
                                            self.update_record_button, self.update_playback_button, self.update_recording_list)
        self.hotkey_thread = threading.Thread(target=self.hotkey_manager.listen_hotkey)
        self.hotkey_thread.daemon = True
        self.hotkey_thread.start()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def init_ui(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TButton", font=("Helvetica", 12), padding=10, background="#3c3f41", foreground="white")
        style.configure("TLabel", font=("Helvetica", 12), background="#1e1e1e", foreground="white")
        style.map("TButton", background=[("active", "#3c3f41")])

        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Save Recordings", command=self.save_recordings)
        filemenu.add_command(label="Load Recordings", command=self.load_recordings)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.on_closing)
        menubar.add_cascade(label="File", menu=filemenu)
        self.config(menu=menubar)

        control_frame = tk.Frame(self, bg="#1e1e1e")
        control_frame.pack(pady=10)

        self.record_button = ttk.Button(control_frame, text="Start Recording", command=self.toggle_recording)
        self.record_button.grid(row=0, column=1, padx=5, pady=5)

        self.play_button = ttk.Button(control_frame, text="Start Playback", command=self.toggle_playback)
        self.play_button.grid(row=0, column=2, padx=5, pady=5)

        self.delete_button = ttk.Button(control_frame, text="Delete Recording", command=self.delete_recording)
        self.delete_button.grid(row=0, column=3, padx=5, pady=5)

        self.playback_speed_label = ttk.Label(control_frame, text="Playback Speed:")
        self.playback_speed_label.grid(row=1, column=1, padx=5, pady=5, sticky="e")

        self.playback_speed_slider = ttk.Scale(control_frame, from_=0.1, to=10.0, orient='horizontal', value=1.0, command=self.update_speed)
        self.playback_speed_slider.grid(row=1, column=2, padx=5, pady=5, sticky="ew")

        # Add a label to display the slider value
        self.speed_value_label = ttk.Label(control_frame, text="1.0x")
        self.speed_value_label.grid(row=1, column=3, padx=5, pady=5)

        self.recording_list = tk.Listbox(self, bg="#333", fg="white", selectbackground="#555555", selectforeground="white")
        self.recording_list.pack(pady=10, fill=tk.BOTH, expand=True)

        self.status_label = ttk.Label(self, text="Status: Idle")
        self.status_label.pack(pady=10)

    def toggle_recording(self):
        if self.recorder.is_recording:
            self.recorder.stop_recording()
            self.record_button.config(text="Start Recording")
            self.update_status("Recording stopped.")
        else:
            self.recorder.start_recording()
            self.record_button.config(text="Stop Recording")
            self.update_status("Recording started...")

        self.update_recording_list()

    def toggle_playback(self):
        speed = self.playback_speed_slider.get()
        if self.playback_manager.is_playing:
            self.playback_manager.stop_playback()
            self.play_button.config(text="Start Playback")
            self.update_status("Playback stopped.")
        else:
            self.playback_manager.start_playback(self.recorder.recordings, speed_factor=speed)
            self.play_button.config(text="Stop Playback")
            self.update_status("Playback started...")

    def delete_recording(self):
        selected_idx = self.recording_list.curselection()
        if selected_idx:
            confirm = messagebox.askyesno(title="Confirm Delete", message="Are you sure you want to delete the selected recording?")
            if confirm:
                idx = selected_idx[0]
                del self.recorder.recordings[idx]
                self.update_status(f"Recording {idx + 1} deleted.")
                self.update_recording_list()
        else:
            confirm = messagebox.askyesno(title="Confirm Delete All", message="Are you sure you want to delete all recordings?")
            if confirm:
                self.recorder.recordings.clear()
                self.update_status("All recordings deleted.")
                self.update_recording_list()

    def update_status(self, message):
        self.status_label.config(text=f"Status: {message}")

    def save_recordings(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            try:
                self.recorder.save_recordings(file_path)
                self.update_status(f"Recordings saved to {file_path}")
                self.update_recording_list()
            except Exception as e:
                messagebox.showerror(title="Error", message=f"Failed to save recordings: {e}")

    def load_recordings(self):
        file_path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            try:
                self.recorder.load_recordings(file_path)
                self.update_status(f"Recordings loaded from {file_path}")
                self.update_recording_list()
            except Exception as e:
                messagebox.showerror(title="Error", message=f"Failed to load recordings: {e}")

    def update_speed(self, value):
        speed = float(value)
        if 0.1 <= speed <= 10.0:
            self.playback_manager.speed_factor = speed  # Update speed factor immediately
            self.speed_value_label.config(text=f"{speed:.1f}x") # Update the label
        else:
            self.playback_speed_slider.set(self.playback_manager.speed_factor)
            messagebox.showwarning("Invalid Speed", "Playback speed must be between 0.1 and 10.0.")

    def on_closing(self):
        self.hotkey_manager.stop_listening()
        self.hotkey_thread.join()
        self.destroy()

    def update_record_button(self):
        if self.recorder.is_recording:
            self.record_button.config(text="Stop Recording")
            self.update_status("Recording started...")
        else:
            self.record_button.config(text="Start Recording")
            self.update_status("Recording stopped.")
            self.update_recording_list()
    
    def update_playback_button(self):
        if self.playback_manager.is_playing:
            self.play_button.config(text="Stop Playback")
            self.update_status("Playback started...")
        else:
            self.play_button.config(text="Start Playback")
            self.update_status("Playback stopped.")

    def update_recording_list(self):
        self.recording_list.delete(0, tk.END)
        for idx, recording in enumerate(self.recorder.recordings):
            self.recording_list.insert(tk.END, f"Recording {idx + 1}: {len(recording)} points")

if __name__ == "__main__":
    app = App()
    app.mainloop()