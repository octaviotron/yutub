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

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import os
from .theme import *
from .utils import get_video_info, download_format, ensure_yt_dlp
from .languages import STRINGS

class YutubApp(tk.Tk):
    def __init__(self, debug=False):
        super().__init__()
        
        self.debug = debug
        self.current_lang = "EN"
        self.title("Yutub - YouTube Downloader")
        self.auth_args = None
        
        # Immediate check for yt-dlp to skip splash if possible
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if os.path.exists(os.path.join(project_root, "yt-dlp")):
            self.finalize_setup()
        else:
            self.withdraw() # Hide main window for splash
            self.setup_initialization()

    def setup_initialization(self):
        """Splash screen for checking/downloading yt-dlp"""
        self.splash = tk.Toplevel(self)
        self.splash.title(self.get_text("init_title"))
        self.splash.geometry("400x150")
        self.splash.configure(bg=BG_DARK)
        self.splash.overrideredirect(True) # No window border
        
        # Center splash
        screen_w = self.splash.winfo_screenwidth()
        screen_h = self.splash.winfo_screenheight()
        x = (screen_w // 2) - 200
        y = (screen_h // 2) - 75
        self.splash.geometry(f"+{x}+{y}")

        ttk.Label(self.splash, text="Yutub", style="Title.TLabel").pack(pady=(20, 5))
        self.init_label = ttk.Label(self.splash, text=self.get_text("checking"), style="Footer.TLabel")
        self.init_label.pack()

        # Run initialization in background
        threading.Thread(target=self.run_init, daemon=True).start()

    def run_init(self):
        def update_label(txt):
            self.after(0, lambda: self.init_label.config(text=txt))

        success = ensure_yt_dlp(update_label, debug=self.debug)
        
        if success:
            self.after(0, self.finalize_setup)
        else:
            self.after(0, lambda: messagebox.showerror(self.get_text("err_title"), self.get_text("err_init")))
            self.after(0, self.destroy)

    def finalize_setup(self):
        """Show main UI once dependencies are ready"""
        if hasattr(self, 'splash'):
            self.splash.destroy()
        
        self.geometry("800x650")
        self.configure(bg=BG_DARK)
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        
        self.setup_ui()
        self.deiconify() # Show main window

    def configure_styles(self):
        self.style.configure("TFrame", background=BG_DARK)
        self.style.configure("TLabel", background=BG_DARK, foreground=TEXT_MAIN, font=FONT_NORMAL)
        self.style.configure("Title.TLabel", background=BG_DARK, foreground=ACCENT, font=FONT_TITLE)
        self.style.configure("Header.TLabel", background=BG_DARK, foreground=TEXT_MAIN, font=FONT_HEADER)
        self.style.configure("Footer.TLabel", background=BG_DARK, foreground=TEXT_DIM, font=FONT_FOOTER)
        
        self.style.configure("TButton", background=ACCENT, foreground=TEXT_MAIN, borderwidth=0, padding=10, font=FONT_BOLD)
        self.style.map("TButton", background=[("active", ACCENT_HOVER)])
        
        self.style.configure("Download.TButton", background=SUCCESS, font=FONT_HEADER)
        self.style.map("Download.TButton", background=[("active", SUCCESS_HOVER), ("disabled", TEXT_DIM)])

        # Disabled Styles
        self.style.configure("Disabled.Treeview", background="#334155", foreground=TEXT_DIM, fieldbackground="#334155")
        self.style.configure("Disabled.TButton", background=TEXT_DIM)

        self.style.configure("TCombobox", fieldbackground=BG_CARD, background=ACCENT, foreground=TEXT_MAIN, arrowcolor=TEXT_MAIN)
        self.style.map("TCombobox", 
            fieldbackground=[("readonly", BG_CARD), ("disabled", BG_DARK)], 
            foreground=[("readonly", TEXT_MAIN), ("disabled", TEXT_DIM)],
            arrowcolor=[("disabled", TEXT_DIM)])

        self.style.configure("Treeview", background=BG_CARD, foreground=TEXT_MAIN, fieldbackground=BG_CARD, borderwidth=0, font=FONT_NORMAL)
        self.style.map("Treeview", background=[("selected", ACCENT)])

        # Language Button Style (Round-ish, Black/White)
        self.style.configure("Lang.TButton", 
            background="#000000", 
            foreground="#FFFFFF", 
            borderwidth=0, 
            padding=3,
            font=("Helvetica", 10, "bold"),
            anchor="center",
            width=3
        )
        self.style.map("Lang.TButton", 
            background=[("active", "#333333")], 
            foreground=[("active", "#FFFFFF")]
        )

        self.style.map("Treeview", background=[("selected", ACCENT)])

    def get_text(self, key):
        return STRINGS[self.current_lang].get(key, key)

    def toggle_language(self):
        self.current_lang = "ES" if self.current_lang == "EN" else "EN"
        self.update_texts()

    def update_texts(self):
        # Update Main Window Title
        self.title(self.get_text("title"))
        
        # Labels
        self.lbl_title.config(text=self.get_text("header_title"))
        self.lbl_url.config(text=self.get_text("url_label"))
        self.explore_btn.config(text=self.get_text("explore"))
        self.lbl_video.config(text=self.get_text("video_header"))
        self.lbl_audio.config(text=self.get_text("audio_header"))
        self.lbl_convert.config(text=self.get_text("convert_label"))
        self.lbl_footer.config(text=self.get_text("footer"))
        
        # Buttons
        self.get_video_btn.config(text=self.get_text("get_video"))
        self.get_audio_btn.config(text=self.get_text("get_audio"))
        
        # Treeviews columns
        self.video_tree.heading("format", text=self.get_text("col_format"))
        self.video_tree.heading("res", text=self.get_text("col_res"))
        self.video_tree.heading("size", text=self.get_text("col_size"))
        
        self.audio_tree.heading("ext", text=self.get_text("col_format"))
        self.audio_tree.heading("quality", text=self.get_text("col_quality"))
        self.audio_tree.heading("size", text=self.get_text("col_size"))

        # Lang button
        self.lang_btn.config(text="ES" if self.current_lang == "EN" else "EN")

        # Update combo values mapping
        # We need to preserve selection logic if possible or reset it
        current_idx = self.audio_conv_combo.current()
        self.audio_conv_combo['values'] = self.get_text("convert_opts")
        if current_idx != -1:
             self.audio_conv_combo.current(current_idx)
        else:
             self.audio_conv_combo.current(0)
             
    def setup_ui(self):
        # 1. Header Bar
        header_frame = ttk.Frame(self, padding=(0, 20))
        header_frame.pack(fill="x")
        
        # Grid layout for header to ensure center title
        header_frame.columnconfigure(0, weight=1)
        header_frame.columnconfigure(1, weight=1)
        header_frame.columnconfigure(2, weight=1)
        
        # Empty left column filler
        ttk.Frame(header_frame).grid(row=0, column=0, sticky="w")
        
        self.lbl_title = ttk.Label(header_frame, text=self.get_text("header_title"), style="Title.TLabel", anchor="center")
        self.lbl_title.grid(row=0, column=1)
        
        self.lang_btn = ttk.Button(header_frame, text="ES", style="Lang.TButton", command=self.toggle_language)
        self.lang_btn.grid(row=0, column=2, sticky="e", padx=(0, 20))
        
        # 2. Body
        body_frame = ttk.Frame(self, padding=20)
        body_frame.pack(fill="both", expand=True)
        
        # 2.1 Top Body - URL Input
        url_section = ttk.Frame(body_frame)
        url_section.pack(fill="x", pady=(0, 20))
        
        self.lbl_url = ttk.Label(url_section, text=self.get_text("url_label"), style="Header.TLabel")
        self.lbl_url.pack(anchor="w", pady=(0, 5))
        
        url_input_row = ttk.Frame(url_section)
        url_input_row.pack(fill="x")
        
        self.url_entry = tk.Entry(url_input_row, bg=BG_CARD, fg=TEXT_MAIN, insertbackground=TEXT_MAIN, font=FONT_NORMAL, border=0, highlightthickness=1, highlightbackground=ACCENT)
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 10), ipady=8)
        
        self.explore_btn = ttk.Button(url_input_row, text=self.get_text("explore"), command=self.handle_explore)
        self.explore_btn.pack(side="right")
        
        # Status Label
        self.status_label = ttk.Label(body_frame, text="", font=FONT_FOOTER, foreground=TEXT_DIM)
        self.status_label.pack(fill="x", pady=(0, 5))
        
        # 2.2 Center Body - Formats
        formats_frame = ttk.Frame(body_frame)
        formats_frame.pack(fill="both", expand=True)
        
        # Video List
        video_wrap = ttk.Frame(formats_frame)
        video_wrap.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self.lbl_video = ttk.Label(video_wrap, text=self.get_text("video_header"), style="Header.TLabel")
        self.lbl_video.pack(anchor="w", pady=(0, 5))
        
        self.video_tree = ttk.Treeview(video_wrap, columns=("format", "res", "size"), show="headings", height=10, selectmode="browse")
        self.video_tree.heading("format", text=self.get_text("col_format"))
        self.video_tree.heading("res", text=self.get_text("col_res"))
        self.video_tree.heading("size", text=self.get_text("col_size"))
        self.video_tree.column("format", width=100)
        self.video_tree.column("res", width=150)
        self.video_tree.column("size", width=100)
        self.video_tree.pack(fill="both", expand=True)
        self.video_tree.bind("<<TreeviewSelect>>", self.on_video_select)
        
        self.get_video_btn = ttk.Button(video_wrap, text=self.get_text("get_video"), style="Download.TButton", command=self.handle_get_video, state="disabled")
        self.get_video_btn.pack(pady=10)
        
        # Audio List
        self.audio_wrap = ttk.Frame(formats_frame)
        self.audio_wrap.pack(side="right", fill="both", expand=True, padx=(10, 0))
        self.lbl_audio = ttk.Label(self.audio_wrap, text=self.get_text("audio_header"), style="Header.TLabel")
        self.lbl_audio.pack(anchor="w", pady=(0, 5))
        
        self.audio_tree = ttk.Treeview(self.audio_wrap, columns=("ext", "quality", "size"), show="headings", height=10, selectmode="browse")
        self.audio_tree.heading("ext", text=self.get_text("col_format"))
        self.audio_tree.heading("quality", text=self.get_text("col_quality"))
        self.audio_tree.heading("size", text=self.get_text("col_size"))
        self.audio_tree.column("ext", width=80)
        self.audio_tree.column("quality", width=170)
        self.audio_tree.column("size", width=100)
        self.audio_tree.pack(fill="both", expand=True)
        self.audio_tree.bind("<<TreeviewSelect>>", self.on_audio_select)
        
        # Audio Actions Row
        audio_actions = ttk.Frame(self.audio_wrap)
        audio_actions.pack(fill="x", pady=10)
        
        self.get_audio_btn = ttk.Button(audio_actions, text=self.get_text("get_audio"), style="Download.TButton", command=self.handle_get_audio, state="disabled")
        self.get_audio_btn.pack(side="left", pady=(18, 0))
        
        conv_container = ttk.Frame(audio_actions)
        conv_container.pack(side="left", padx=15)
        
        self.lbl_convert = ttk.Label(conv_container, text=self.get_text("convert_label"), style="Footer.TLabel")
        self.lbl_convert.pack(anchor="w")
        
        self.audio_conv_combo = ttk.Combobox(conv_container, state="disabled", width=15)
        self.audio_conv_combo['values'] = self.get_text("convert_opts")
        self.audio_conv_combo.current(0)
        self.audio_conv_combo.pack(pady=(2, 0))
        
        # 3. Bottom Bar
        footer_frame = ttk.Frame(self, padding=10)
        footer_frame.pack(fill="x", side="bottom")
        self.lbl_footer = ttk.Label(footer_frame, text=self.get_text("footer"), style="Footer.TLabel", anchor="center")
        self.lbl_footer.pack(fill="x")

    def handle_explore(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showwarning(self.get_text("w_input"), self.get_text("m_input"))
            return

        self.status_label.config(text=self.get_text("exploring"), foreground=ACCENT)
        self.explore_btn.config(state="disabled")

        def task():
            data = get_video_info(url, debug=self.debug)
            self.after(0, lambda: self.update_ui_with_data(data))

        threading.Thread(target=task, daemon=True).start()

    def update_ui_with_data(self, data):
        self.explore_btn.config(state="normal")
        if 'error' in data:
            self.status_label.config(text=self.get_text("explore_failed"), foreground="red")
            self.show_error(self.get_text("err_title"), data['error'])
            return

        self.auth_args = data.get('auth_args')
        self.status_label.config(text=f"{self.get_text('fetched')}{data['title']}", foreground=SUCCESS)
        
        # Clear trees
        for tree in (self.video_tree, self.audio_tree):
            for item in tree.get_children(): 
                tree.delete(item)
                
        # Insert Video (Format, Resolution, Size)
        for f in data['video']: 
            self.video_tree.insert("", "end", iid=f['format_id'], values=(f['ext'], f['res'], f['size']))
            
        # Insert Audio (Ext, Quality, Size)
        for f in data['audio']: 
            self.audio_tree.insert("", "end", iid=f['format_id'], values=(f['ext'], f['quality'], f['size']))

    def on_video_select(self, event):
        """When selecting video, enable video btn, disable audio side."""
        if self.video_tree.selection():
            self.audio_tree.selection_remove(self.audio_tree.selection())
            # Update states
            self.get_video_btn.config(state="normal")
            self.get_audio_btn.config(state="disabled")
            self.audio_conv_combo.config(state="disabled")
            # Update visual themes
            self.video_tree.config(style="Treeview")
            self.audio_tree.config(style="Disabled.Treeview")

    def on_audio_select(self, event):
        """When selecting audio, enable audio btn, disable video side."""
        if self.audio_tree.selection():
            self.video_tree.selection_remove(self.video_tree.selection())
            # Update states
            self.get_audio_btn.config(state="normal")
            self.audio_conv_combo.config(state="readonly")
            self.get_video_btn.config(state="disabled")
            # Update visual themes
            self.audio_tree.config(style="Treeview")
            self.video_tree.config(style="Disabled.Treeview")

    def show_error(self, title, message):
        print(f"[{title}] {message}")
        err_win = tk.Toplevel(self)
        err_win.title(title)
        err_win.geometry("500x300")
        err_win.configure(bg=BG_CARD)
        ttk.Label(err_win, text=f"Error: {title}", style="Header.TLabel", padding=10).pack(fill="x")
        txt = tk.Text(err_win, bg=BG_DARK, fg="red", font=FONT_NORMAL, wrap="word", borderwidth=0)
        txt.insert("1.0", message)
        txt.config(state="disabled")
        txt.pack(fill="both", expand=True, padx=10, pady=10)
        ttk.Button(err_win, text="Close", command=err_win.destroy).pack(pady=10)

    def handle_get_video(self):
        selection = self.video_tree.selection()
        if not selection:
            messagebox.showwarning(self.get_text("w_select"), self.get_text("m_select_video"))
            return
        
        format_id = selection[0]
        self.start_download(format_id)

    def handle_get_audio(self):
        selection = self.audio_tree.selection()
        if not selection:
            messagebox.showwarning(self.get_text("w_select"), self.get_text("m_select_audio"))
            return
        
        format_id = selection[0]
        # Map localized selection back to EN logic if needed, or simple index logic
        # Current logic passes the string directly. If we translate the dropdown, we must handle the mapping.
        # "Convert to MP3" -> logic expects "Convert to MP3".
        # We need to map the display string back to the logic string OR update utils to accept keywords.
        # Easiest: get index and map to canonical EN list.
        idx = self.audio_conv_combo.current()
        en_opts = ["Original Format", "Convert to MP3", "Convert to WAV"]
        conv_mode = en_opts[idx] if idx >= 0 else None
        
        self.start_download(format_id, conv_mode)

    def start_download(self, format_id, conv_mode=None):
        # Create downloads folder
        os.makedirs("downloads", exist_ok=True)
        
        self.get_video_btn.config(state="disabled")
        self.get_audio_btn.config(state="disabled")
        self.audio_conv_combo.config(state="disabled")
        self.status_label.config(text=self.get_text("status_start"), foreground=ACCENT)

        def progress_update(p):
            if p == "Converting...":
                 txt = self.get_text("status_converting")
            else:
                 txt = f"{self.get_text('status_downloading')}{p}"
            self.after(0, lambda: self.status_label.config(text=txt))

        def task():
            success, msg = download_format(self.url_entry.get(), format_id, progress_update, conv_mode, self.auth_args, debug=self.debug)
            self.after(0, lambda: self.on_download_complete(success, msg))
            
        threading.Thread(target=task, daemon=True).start()

    def on_download_complete(self, success, msg=""):
        self.status_label.config(text=self.get_text("status_done") if success else self.get_text("status_fail"), 
                                 foreground=SUCCESS if success else "red")
        
        # Reset buttons to correct state based on selection
        if self.video_tree.selection():
            self.get_video_btn.config(state="normal")
        if self.audio_tree.selection():
            self.get_audio_btn.config(state="normal")
            self.audio_conv_combo.config(state="readonly")

        if success:
            messagebox.showinfo(self.get_text("s_success"), self.get_text("m_success"))
        else:
            self.show_error(self.get_text("err_title"), msg)
