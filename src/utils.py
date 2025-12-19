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
    """Ensure yt-dlp executable exists in the project root. Download if missing."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    yt_dlp_path = os.path.join(project_root, "yt-dlp")
    
    if os.path.exists(yt_dlp_path):
        return yt_dlp_path

    if progress_callback:
        progress_callback("Downloading yt-dlp...")
        
    if debug: print("yt-dlp not found. Downloading latest version from GitHub...")
    # URL for the latest stable Linux binary
    url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp"
    
    try:
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
        
        # Common User-Agent to mimic a real browser
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        
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

        # 1. Identify working auth strategy using Title check
        title_base = ["./yt-dlp", "--js-runtimes", "node", "--get-title", "--no-warnings"]
        
        working_auth_args = []
        title = None
        
        # Define strategies: list of (cookies_path, browser_name)
        strategies = []
        if os.path.exists(cookies_file):
            strategies.append((cookies_file, None))
        strategies.append((None, browser))                # default detected
        if platform.system() == 'Linux':
            # order matters: try likely candidates that might work without secretstorage if default fails
            for b in ['firefox', 'chrome', 'brave', 'edge', 'chromium', 'opera']:
                if b != browser: strategies.append((None, b))
        strategies.append((None, None))                   # no cookies (last resort)
        
        # Prepare environment with PYTHONPATH for custom libs (secretstorage)
        env = os.environ.copy()
        lib_path = os.path.join(project_root, "lib")
        if os.path.exists(lib_path):
            current_pythonpath = env.get("PYTHONPATH", "")
            env["PYTHONPATH"] = f"{lib_path}{os.pathsep}{current_pythonpath}"

        # Execute strategies
        for c_path, b_name in strategies:
            try:
                full_cmd, auth_args = build_full_cmd(title_base, c_path, b_name)
                full_cmd.append(url) # Add URL to the command
                # We use subprocess.run to catch errors easily
                # timeout increased to 90s
                res = subprocess.run(full_cmd, capture_output=True, text=True, timeout=90, env=env)
                
                if res.returncode == 0 and res.stdout.strip():
                    title = res.stdout.strip()
                    working_auth_args = auth_args
                    if debug: print(f"Strategy worked: cookies={c_path}, browser={b_name}")
                    break
                else:
                    # Collect error for debugging if all fail
                    err_msg = res.stderr.strip() if res.stderr else "Unknown error"
                    if debug: print(f"Strategy failed (c={c_path}, b={b_name}): rc={res.returncode}, err={err_msg[:200]}...")

            except subprocess.TimeoutExpired:
                if debug: print(f"Strategy timed out: c={c_path}, b={b_name}")
            except Exception as e:
                # strategy failed, try next
                if debug: print(f"Strategy exception (c={c_path}, b={b_name}): {str(e)}")
                continue

        if not title:
            # Re-construct a helpful error message from the last failure but generally
            # imply that no valid auth method was found.
            return {'error': "Could not fetch video info. All authentication strategies failed.\n- Check your internet connection.\n- Ensure you are logged in to YouTube in your browser.\n- If using Linux, try 'pip install secretstorage'."}

        # 2. Get Formats using the SUCCESSFUL strategy
        format_base = ["./yt-dlp", "--js-runtimes", "node", "-F", "--no-warnings"]
        # Basic args + working auth
        final_format_cmd = list(format_base)
        final_format_cmd.extend(["--user-agent", user_agent, "--no-check-certificates"])
        final_format_cmd.extend(working_auth_args)
        final_format_cmd.append(url) # append URL at the end
        
        try:
             output = subprocess.check_output(final_format_cmd, stderr=subprocess.STDOUT, env=env).decode()
        except subprocess.CalledProcessError as e:
             return {'error': f"Failed to fetch formats: {e.output.decode() if e.output else str(e)}"}
        
        # 3. Parse formats
        video_formats = []
        audio_formats = []
        
        lines = output.splitlines()
        parsing = False
        for line in lines:
            if line.startswith('ID') or '---' in line:
                if '---' in line: parsing = True
                continue
            
            if not parsing:
                continue
                
            parts = line.split()
            if len(parts) < 3:
                continue
                
            f_id = parts[0]
            extension = parts[1]
            
            # Identify audio only formats
            is_audio = 'audio only' in line or (parts[2] == 'audio' and parts[3] == 'only')
            
            # Extract size
            size_match = re.search(r'(\d+\.?\d*)\s*([mMgG][iI]?[bB])', line)
            filesize = size_match.group(0) if size_match else "Unknown"
            
            if is_audio:
                # Extract all 'k' values (like 129k, 44k, etc)
                k_values = re.findall(r'(\d+)k', line)
                hz_match = re.search(r'(\d+)Hz', line)
                
                # Default values
                abr = "N/A"
                asr = "N/A"
                
                if hz_match:
                    # Case 1: Sampling rate is in Hz (e.g. 44100Hz)
                    try:
                        khz = int(hz_match.group(1)) // 1000
                        asr = f"{khz}k"
                    except:
                        asr = hz_match.group(0)
                        
                    # If we have Hz, then the last 'k' value is usually ABR
                    if k_values:
                        abr = f"{k_values[-1]}k"
                elif len(k_values) >= 2:
                    # Case 2: Both ABR and ASR are in 'k' format (e.g. 129k 44k)
                    # For audio only, the last two are usually ABR and ASR
                    asr = f"{k_values[-1]}k"
                    abr = f"{k_values[-2]}k"
                elif k_values:
                    # Fallback
                    abr = f"{k_values[0]}k"
                
                quality = f"{abr} - {asr}"
                
                entry = {
                    'format_id': f_id,
                    'ext': extension,
                    'quality': quality or "N/A",
                    'size': filesize
                }
                audio_formats.append(entry)
            else:
                # Filter video by extension and exclude "video only"
                if extension.lower() not in ['mp4', 'webm'] or 'video only' in line:
                    continue
                
                # Extract resolution
                res_match = re.search(r'(\d+x\d+)|(\d+p)', line)
                resolution = res_match.group(0) if res_match else parts[2]
                
                entry = {
                    'format_id': f_id,
                    'ext': extension,
                    'res': resolution,
                    'size': filesize
                }
                video_formats.append(entry)
                
        return {
            'title': title,
            'video': video_formats,
            'audio': audio_formats,
            'auth_args': working_auth_args
        }
        
    except Exception as e:
        if debug: print(f"get_video_info exception: {e}")
        return {'error': str(e)}

def download_format(url, format_id, progress_callback=None, conv_mode=None, auth_args=None, debug=False):
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
        
        # Command setup
        cmd = [
            "./yt-dlp",
            "--js-runtimes", "node",
            "-f", format_id,
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
