import json
import time
from pynput import mouse, keyboard

class Recorder:
    def __init__(self):
        self.recordings = []
        self.is_recording = False
        self.last_time = None

    def start_recording(self):
        self.is_recording = True
        self.recordings.append([])
        self.last_time = time.time()
        self.mouse_listener = mouse.Listener(on_move=self.on_move, on_click=self.on_click)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        self.mouse_listener.start()
        self.keyboard_listener.start()

    def stop_recording(self):
        self.is_recording = False
        self.mouse_listener.stop()
        self.keyboard_listener.stop()

    def on_move(self, x, y):
        if self.is_recording:
            self.record_event("move", x, y)

    def on_click(self, x, y, button, pressed):
        if self.is_recording and pressed:
            self.record_event("click", x, y, button=button)

    def on_key_press(self, key):
        if self.is_recording:
            try:
                self.record_event("key", key.char)
            except AttributeError:  # Special keys like Ctrl, Shift, etc.
                self.record_event("key", str(key))

    def record_event(self, event_type, *args, **kwargs):
        current_time = time.time()
        interval = current_time - self.last_time

        # Store button as string for JSON serialization:
        if "button" in kwargs:
            kwargs["button"] = str(kwargs["button"]).split('.')[1] 

        self.recordings[-1].append((interval, event_type, args, kwargs))
        self.last_time = current_time

    def save_recordings(self, file_path):
        with open(file_path, 'w') as file:
            json.dump(self.recordings, file)

    def load_recordings(self, file_path):
        with open(file_path, 'r') as file:
            self.recordings = json.load(file)

        # Convert button string back to pynput.mouse.Button object:
        for recording in self.recordings:
            for event in recording:
                if event[1] == "click":  # If it's a click event
                    button_str = event[3].get("button")
                    if button_str:
                        event[3]["button"] = getattr(mouse.Button, button_str)

class HotKeyManager:
    def __init__(self, recorder, playback_manager, update_record_ui_callback, update_playback_ui_callback, update_recording_list):
        self.recorder = recorder
        self.playback_manager = playback_manager
        self.record_listener = None
        self.playback_listener = None
        self.should_stop = False
        self.update_record_ui_callback = update_record_ui_callback
        self.update_playback_ui_callback = update_playback_ui_callback
        self.update_recording_list = update_recording_list

    def listen_hotkey(self):
        def on_press(key):
            if key == keyboard.Key.f8:
                if self.recorder.is_recording:
                    self.recorder.stop_recording()
                else:
                    self.recorder.start_recording()
                self.update_record_ui_callback()
                self.update_recording_list()
            elif key == keyboard.Key.f9:
                if self.playback_manager.is_playing:
                    self.playback_manager.stop_playback()
                else:
                    self.playback_manager.start_playback(self.recorder.recordings)
                self.update_playback_ui_callback()

        self.record_listener = keyboard.Listener(on_press=on_press)
        self.record_listener.start()
        while not self.should_stop:
            time.sleep(0.5)

    def stop_listening(self):
        self.should_stop = True
        self.record_listener.stop()
