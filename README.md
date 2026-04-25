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
- **Python 3.11+**: Ensure Python is installed on your system.
- **Web Browser**: Ensure you are logged into YouTube in a supported browser (Brave, Chrome, Firefox, etc.) so the app can bypass bot detection.

### Installation (Debian/Ubuntu/Linux)
To ensure all features work correctly (including UI, audio conversion, and bot bypass), run the following command to install the required system packages:

```bash
sudo apt update
sudo apt install python3-tk python3-pip nodejs ffmpeg gnome-keyring
```

### Setup
1.  Clone the repository:
    ```bash
    git clone https://github.com/octaviotron/yutub.git
    cd yutub
    ```
2.  Run the application:
    ```bash
    python3 yutub.py
    ```

**Note:** The application will automatically:
- Download the latest `yt-dlp` executable into the `lib/` folder.
- Install local Python dependencies (like `secretstorage`) into the `lib/` folder to handle secure authentication without modifying your system's global Python environment.

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
