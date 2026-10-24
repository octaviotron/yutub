# Yutub - YouTube Downloader
# Copyright (C) 2025 Octavio Rossell Tabet <octavio.rossell@gmail.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# 
# Developed by Octavio Rossell Tabet octavio.rossell@gmail.com 
# https://github.com/octaviotron/yutub

import subprocess
import re
import os
import platform
import urllib.request
import stat
import threading
import sys

def ensure_yt_dlp(progress_callback=None, debug=False):
    """Ensure yt-dlp executable exists in the lib folder. Download if missing."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    lib_path = os.path.join(project_root, "lib")
    yt_dlp_path = os.path.join(lib_path, "yt-dlp")
    
    if os.path.exists(yt_dlp_path):
        return yt_dlp_path

    if progress_callback:
        progress_callback("Downloading yt-dlp...")
        
    if debug: print("yt-dlp not found in lib. Downloading latest version from GitHub...")
    # URL for the latest stable Linux binary
    url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp"
    
    try:
        os.makedirs(lib_path, exist_ok=True)
        def reporthook(blocknum, blocksize, totalsize):
            if progress_callback and totalsize > 0:
                percent = min(100, int(blocknum * blocksize * 100 / totalsize))
                progress_callback(f"Downloading yt-dlp: {percent}%")

        # Download the file
        urllib.request.urlretrieve(url, yt_dlp_path, reporthook=reporthook)
        
        # Set execute permissions (chmod +x)
        st = os.stat(yt_dlp_path)
        os.chmod(yt_dlp_path, st.st_mode | stat.S_IEXEC)
        
        if debug: print("yt-dlp downloaded and permissions set.")
        return yt_dlp_path
    except Exception as e:
        if debug: print(f"Error downloading yt-dlp: {e}")
        return None

def update_yt_dlp(debug=False):
    """Force update yt-dlp binary."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    yt_dlp_path = os.path.join(project_root, "lib", "yt-dlp")
    if not os.path.exists(yt_dlp_path):
        return ensure_yt_dlp(debug=debug)
    
    try:
        if debug: print("Updating yt-dlp...")
        subprocess.check_call([yt_dlp_path, "-U"], stdout=subprocess.DEVNULL if not debug else None)
        return yt_dlp_path
    except Exception as e:
        if debug: print(f"Error updating yt-dlp: {e}")
        return yt_dlp_path

def ensure_dependencies(progress_callback=None, debug=False):
    """Ensure secretstorage is installed in local lib folder for Linux auth."""
    if platform.system() != "Linux":
        return True

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    lib_path = os.path.join(project_root, "lib")
    # Check for a key file inside secretstorage pkg
    ss_path = os.path.join(lib_path, "secretstorage")
    
    if os.path.exists(ss_path):
        return True

    if progress_callback:
        progress_callback("Installing dependencies (secretstorage)...")
        
    if debug: print("Installing secretstorage to local lib...")
    
    try:
        os.makedirs(lib_path, exist_ok=True)
        # Use subprocess to pip install
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-t", lib_path, "secretstorage"], 
                              stdout=subprocess.DEVNULL if not debug else None,
                              stderr=subprocess.DEVNULL if not debug else None)
        if debug: print("Dependencies installed.")
        return True
    except Exception as e:
        if debug: print(f"Error installing dependencies: {e}")
        return False

def get_default_browser():
    """Attempt to detect the default browser name for yt-dlp."""
    try:
        if platform.system() == 'Linux':
            # Try to get default browser via xdg-settings
            try:
                browser_cmd = subprocess.check_output(['xdg-settings', 'get', 'default-web-browser'], stderr=subprocess.STDOUT).decode().strip()
                if 'chrome' in browser_cmd.lower(): return 'chrome'
                if 'firefox' in browser_cmd.lower(): return 'firefox'
                if 'brave' in browser_cmd.lower(): return 'brave'
                if 'opera' in browser_cmd.lower(): return 'opera'
                if 'edge' in browser_cmd.lower(): return 'edge'
            except:
                pass
        elif platform.system() == 'Darwin':
            return 'safari'
        elif platform.system() == 'Windows':
            return 'chrome'
    except:
        pass
    # Fallback to firefox as requested in previous iterations if detection fails
    return 'firefox'

def get_video_info(url, debug=False):
    """
    Fetch video metadata and formats using the LOCAL yt-dlp executable.
    Dynamically identifies the correct browser/cookie strategy and returns it.
    """
    try:
        ensure_yt_dlp(debug=debug)
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cookies_file = os.path.join(project_root, "cookies.txt")
        browser = get_default_browser()
        
        # Standard Desktop User-Agent
        user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        
        # Helper to construct args
        def build_full_cmd(base_cmd, c_path=None, b_name=None):
            cmd = list(base_cmd)
            cmd.extend(["--user-agent", user_agent, "--no-check-certificates"])
            auth = []
            if c_path and os.path.exists(c_path):
                auth = ["--cookies", c_path]
            elif b_name:
                auth = ["--cookies-from-browser", b_name]
            return cmd + auth, auth

        yt_cmd = os.path.join(project_root, "lib", "yt-dlp")
        format_base = [
            yt_cmd,
            "--js-runtimes", "node",
            "--print", "TITLE:%(title)s",
            "-F",
            "--no-warnings",
            "--force-ipv4",
            "--no-check-certificates",
            "--geo-bypass",
            "--ignore-config",
            "--no-playlist"
        ]
        
        # Define strategies in order:
        # 1. Custom cookies.txt if present
        # 2. Unauthenticated / No cookies (fastest, immune to web-client SABR streaming)
        # 3. Detected default browser
        # 4. Other Linux browsers
        strategies = []
        if os.path.exists(cookies_file):
            strategies.append((cookies_file, None))
        strategies.append((None, None))
        if browser:
            strategies.append((None, browser))
        if platform.system() == 'Linux':
            for b in ['firefox', 'chrome', 'brave', 'edge', 'chromium', 'opera']:
                if b != browser:
                    strategies.append((None, b))
        
        # Prepare environment with PYTHONPATH for custom libs (secretstorage)
        env = os.environ.copy()
        lib_path = os.path.join(project_root, "lib")
        if os.path.exists(lib_path):
            current_pythonpath = env.get("PYTHONPATH", "")
            env["PYTHONPATH"] = f"{lib_path}{os.pathsep}{current_pythonpath}"

        working_auth_args = []
        title = None
        video_formats = []
        audio_formats = []
        err_msg = ""

        # Execute strategies and validate that playable formats are returned
        for c_path, b_name in strategies:
            try:
                full_cmd, auth_args = build_full_cmd(format_base, c_path, b_name)
                full_cmd.append(url)
                res = subprocess.run(full_cmd, capture_output=True, text=True, timeout=90, env=env)
                
                if res.returncode == 0 and res.stdout.strip():
                    output = res.stdout
                    cur_title = None
                    cur_video = []
                    cur_audio = []
                    
                    lines = output.splitlines()
                    parsing = False
                    for line in lines:
                        if line.startswith("TITLE:"):
                            cur_title = line[6:].strip()
                            continue
                        if line.startswith('ID'):
                            parsing = True
                            continue
                        
                        if not parsing or '---' in line or '───' in line or not line.strip():
                            continue

                        parts = line.split()
                        if len(parts) < 3:
                            continue
                            
                        f_id = parts[0]
                        extension = parts[1]
                        
                        # Skip image storyboards
                        if 'images' in line.lower() or 'storyboard' in line.lower():
                            continue

                        # Identify audio only formats
                        is_audio = any(kw in line.lower() for kw in ['audio only', 'audio-only']) or \
                                   extension.lower() in ['m4a', 'mp3', 'ogg', 'wav', 'flac', 'opus'] or \
                                   (len(parts) > 2 and 'audio' in parts[2].lower())
                        
                        # Extract size (supports KiB, MiB, GiB)
                        size_match = re.search(r'(\d+\.?\d*)\s*([kKmMgGtT][iI]?[bB])', line)
                        filesize = size_match.group(0) if size_match else "Unknown"
                        
                        if is_audio:
                            k_values = re.findall(r'(\d+)k', line)
                            hz_match = re.search(r'(\d+)Hz', line)
                            
                            abr = "N/A"
                            asr = "N/A"
                            
                            if hz_match:
                                try:
                                    khz = int(hz_match.group(1)) // 1000
                                    asr = f"{khz}k"
                                except:
                                    asr = hz_match.group(0)
                                if k_values:
                                    abr = f"{k_values[-1]}k"
                            elif len(k_values) >= 2:
                                asr = f"{k_values[-1]}k"
                                abr = f"{k_values[-2]}k"
                            elif k_values:
                                abr = f"{k_values[0]}k"
                            
                            quality = f"{abr} - {asr}" if (abr != "N/A" or asr != "N/A") else "N/A"
                            
                            entry = {
                                'format_id': f_id,
                                'ext': extension,
                                'quality': quality,
                                'size': filesize
                            }
                            cur_audio.append(entry)
                        else:
                            if extension.lower() not in ['mp4', 'webm', 'mkv']:
                                continue
                            
                            res_match = re.search(r'(\d+x\d+)|(\d+p)', line)
                            resolution = res_match.group(0) if res_match else parts[2]
                            if resolution.lower() in ['audio', 'images']:
                                continue
                            
                            entry = {
                                'format_id': f_id,
                                'ext': extension,
                                'res': resolution,
                                'size': filesize
                            }
                            cur_video.append(entry)
                    
                    # Accept strategy if a title and formats (especially audio or video) were found
                    if cur_title and (cur_audio or cur_video):
                        title = cur_title
                        audio_formats = cur_audio
                        video_formats = cur_video
                        working_auth_args = auth_args
                        if debug:
                            print(f"Strategy worked: cookies={c_path}, browser={b_name} (audio={len(audio_formats)}, video={len(video_formats)})")
                            with open(os.path.join(project_root, "debug_output.txt"), "w") as f:
                                f.write(output)
                        break
                    else:
                        if debug:
                            print(f"Strategy yielded no playable formats: cookies={c_path}, browser={b_name}")
                else:
                    err_msg = res.stderr.strip() if res.stderr else "Unknown error"
                    if debug:
                        print(f"Strategy failed (c={c_path}, b={b_name}): rc={res.returncode}, err={err_msg[:200]}...")

            except subprocess.TimeoutExpired:
                if debug: print(f"Strategy timed out: c={c_path}, b={b_name}")
            except Exception as e:
                if debug: print(f"Strategy exception (c={c_path}, b={b_name}): {str(e)}")
                continue

        if not title:
            last_err = err_msg if 'err_msg' in locals() and err_msg else "No details available."
            return {'error': f"Could not fetch video info. All authentication strategies failed.\n\nLast Error: {last_err[:300]}\n\nSuggestions:\n- Check your internet connection.\n- Ensure you are logged in to YouTube in your browser.\n- If using Linux, try 'pip install secretstorage'."}

        return {
            'title': title,
            'video': video_formats,
            'audio': audio_formats,
            'auth_args': working_auth_args
        }
        
    except Exception as e:
        if debug: print(f"get_video_info exception: {e}")
        return {'error': str(e)}

def download_format(url, format_id, progress_callback=None, conv_mode=None, auth_args=None, is_audio=False, debug=False):
    """
    Download a specific format using the LOCAL yt-dlp executable.
    Saves to the 'downloads' folder.
    """
    try:
        ensure_yt_dlp(debug=debug)
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cookies_file = os.path.join(project_root, "cookies.txt")
        browser = get_default_browser()
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        
        yt_cmd = os.path.join(project_root, "lib", "yt-dlp")
        
        # When downloading video, mux with best audio stream so video files have sound
        if is_audio or conv_mode is not None:
            f_spec = format_id
        else:
            f_spec = f"{format_id}+bestaudio/{format_id}"

        # Command setup
        cmd = [
            yt_cmd,
            "--js-runtimes", "node",
            "-f", f_spec,
            "-o", "downloads/%(title)s.%(ext)s",
            "--no-warnings",
            "--user-agent", user_agent,
            "--no-check-certificates"
        ]

        if auth_args is not None:
            # Use the specific auth arguments that worked during Explore
            cmd.extend(auth_args)
        elif os.path.exists(cookies_file):
            cmd.extend(["--cookies", cookies_file])
        elif browser:
            # Fallback if no specific auth_args passed (shouldn't happen with updated app.py)
            cmd.extend(["--cookies-from-browser", browser])

        # Add conversion flags if requested
        if conv_mode == "Convert to MP3":
            cmd.extend(["--extract-audio", "--audio-format", "mp3"])
        elif conv_mode == "Convert to WAV":
            cmd.extend(["--extract-audio", "--audio-format", "wav"])
            
        cmd.append(url)

        # Prepare environment with PYTHONPATH
        env = os.environ.copy()
        lib_path = os.path.join(project_root, "lib")
        if os.path.exists(lib_path):
            current_pythonpath = env.get("PYTHONPATH", "")
            env["PYTHONPATH"] = f"{lib_path}{os.pathsep}{current_pythonpath}"

        # Start process
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, env=env)
        
        error_output = []
        
        # Thread to read stderr
        def read_stderr():
            for err_line in process.stderr:
                if err_line.strip():
                    error_output.append(err_line.strip())
        
        stderr_thread = threading.Thread(target=read_stderr, daemon=True)
        stderr_thread.start()

        for line in process.stdout:
            # Look for lines like "[download]  25.0% of ..."
            if "[download]" in line and "%" in line:
                match = re.search(r'(\d+\.?\d*%)', line)
                if match and progress_callback:
                    progress_callback(match.group(1))
            elif "[ExtractAudio]" in line:
                if progress_callback:
                    progress_callback("Converting...")
        
        process.wait()
        stderr_thread.join(timeout=1.0)
        
        if process.returncode == 0:
            return True, "Done"
        else:
            err_summary = "\n".join(error_output)
            return False, f"yt-dlp exited with code {process.returncode}\n{err_summary}"
        
    except Exception as e:
        return False, str(e)
