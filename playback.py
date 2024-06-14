import random
import time
import threading
import pyautogui

# Disable pyautogui's global pause
pyautogui.PAUSE = 0 

class PlaybackManager:
    def __init__(self):
        self.is_playing = False
        self.speed_factor = 1.0  # Default playback speed

    def start_playback(self, recordings, speed_factor=None):  # Remove default value here
        if not recordings:
            return
        self.is_playing = True
        self.records = recordings
        # Only update speed_factor if provided
        if speed_factor is not None: 
            self.speed_factor = speed_factor
        playback_thread = threading.Thread(target=self._loop_playback)
        playback_thread.daemon = True
        playback_thread.start()

    def _loop_playback(self):
        while self.is_playing and self.records:
            task = random.choice(self.records)
            start_time = time.time()
            elapsed_time = 0

            for interval, event_type, args, kwargs in task:
                if not self.is_playing:
                    break

                elapsed_time += interval / self.speed_factor  # Apply speed factor here
                target_time = start_time + elapsed_time

                # Wait until the target time, or proceed if already passed
                time.sleep(max(0, target_time - time.time()))

                if self.is_playing:
                    if event_type == "move":
                        pyautogui.moveTo(*args)
                    elif event_type == "click":
                        button = kwargs.get('button')
                        if button:
                            # Fix: Get the button string directly
                            button = str(button).replace('Button.', '') # Correct way
                        pyautogui.click(*args, button=button)
                    elif event_type == "key":
                        pyautogui.press(args[0])

    

    def stop_playback(self):
        self.is_playing = False
