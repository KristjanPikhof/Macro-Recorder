# Macro Mouse Recorder

Macro Mouse Recorder allows you to record and playback mouse actions.

**Please use this tool ethically and responsibly.**

## Key Features

- ⏺ **Start Recording (F8)**: Start recording your actions.
- ⏹ **Stop Recording (F8)**: Stop recording.
- ▶️ **Start Playback (F9)**: Play back the recorded actions.
- ⏹️ **Stop Playback (F9)**: Stop the playback.
- ❌ **Delete Recording**: Delete the selected recording.
  - If you select a recording, only the selected one will be deleted.
  - Otherwise, all recordings will be deleted.
- 🔁 **Playback Speed**: Use the slider to adjust the playback speed.
- 📁 **Save Recordings**: Save your recordings to a file using the File menu.
- 📂 **Load Recordings**: Load your recordings from a file using the File menu.
- 🔄 **Random Playback**: Recordings will be played in random order.

## Requirements

The following Python packages are required to run the application:
- `pyautogui`
- `pynput`
- `ttkthemes`

You can install the required packages using:
```s
pip install -r requirements.txt
```

Launch the bot through the command line:

```sh
python main.py
```

## 🤖 How It Works
This application builds upon advanced frameworks to deliver a superior user experience with a wealth of options:

**Recording**: When you press F8 to start recording, the application listens to mouse and keyboard actions and logs the events with timestamps. These interactions are stored in a structured list for playback.

**Playback**: Pressing F9 starts the playback loop. The application reads the recorded events, calculates the intervals between actions, and simulates the recorded mouse movements and keyboard presses accordingly.

**Managing Recordings**:

- **Start/Stop recording by pressing F8**: Actions during recording are logged.
- **Start/Stop playback by pressing F9**: The recorded actions are replayed in random order.
- **Delete Recording**: Select a recording and delete it, or delete all recordings at once.
- **Save/Load Recordings**: Use the File menu to save recordings to a file or load them from a file.
- **Playback Speed**: Adjust the playback speed using the slider provided in the interface.

## Support
If you encounter any issues, please leave a message in the issues section of the GitHub repository.

## Screenshot
![image](https://github.com/KristjanPikhof/Macro-Recorder/assets/60576985/1a81c0bd-e382-447f-8764-642026e8fbf7)
