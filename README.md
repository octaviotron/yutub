# Yutub

**Yutub** is a modern, lightweight YouTube downloader GUI built with Python and Tkinter. It acts as a friendly wrapper for `yt-dlp`, allowing you to easily explore available video/audio formats and download them with a single click.

## Features
- **Modern UI**: Dark-themed, responsive interface using Slate/Violet aesthetics.
- **Smart Exploration**: Fetch all available formats for any YouTube URL.
- **Video Downloads**: Support for MP4 and WebM formats with resolution selection.
- **Audio Extraction**: Download audio only with custom conversion options (Original, MP3, or WAV).
- **Cookie Integration**: Automatic Firefox cookie extraction to bypass bot detection.
- **Real-time Progress**: Background downloading with live percentage updates.

## Installation

### Prerequisites
1.  **Python 3.11+**: Ensure Python is installed on your system.
2.  **Web Browser**: Chrome, Firefox, Brave, Opera, Edge, or Safari. The app automatically detects your system's default browser to extract cookies and bypass bot detection. **Ensure you are logged into YouTube in one of these browsers.**

### Setup
1.  Clone the repository:
    ```bash
    git clone https://github.com/octaviotron/yutub.git
    cd yutub
    ```
2.  (Optional) If you are on Linux and encounter issues, you may need to install `ffmpeg` for audio conversion:
    ```bash
    sudo apt install ffmpeg
    ```

**Note:** The application will automatically:
- Download the latest `yt-dlp` executable if it's missing.
- Use bundled dependencies (in the `lib/` folder) to handle secure authentication without polluting your system Python.

## Usage
Run the application using Python:
```bash
python3 yutub.py
```

1.  Paste a YouTube URL and click **Explore**.
2.  Select a format from either the Video or Audio list.
3.  (Optional) Choose a conversion format for audio.
4.  Click **Get Video** or **Get Audio Only**.
5.  Find your files in the `downloads/` folder.

## Contribute
Contributions are welcome! If you have suggestions for new features or bug fixes:
1.  Fork the repository.
2.  Create a feature branch (`git checkout -b feature/CoolNewFeature`).
3.  Commit your changes (`git commit -m 'Add some feature'`).
4.  Push to the branch (`git push origin feature/CoolNewFeature`).
5.  Open a Pull Request.

## License
This project is licensed under the **GNU General Public License v3.0**. See the header of source files for details.

## Credits
Developed by **Octavio Rossell Tabet**
- Email: [octavio.rossell@gmail.com](mailto:octavio.rossell@gmail.com)
- GitHub: [github.com/octaviotron/yutub](https://github.com/octaviotron/yutub)
