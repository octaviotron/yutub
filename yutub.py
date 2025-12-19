#!/usr/bin/env python3
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

import sys
import os

# Add local lib folder to path for dependencies like secretstorage
lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib")
if os.path.exists(lib_path):
    sys.path.insert(0, lib_path)

from src.app import YutubApp

if __name__ == "__main__":
    # Set to True to enable STDOUT and STDERR messages for debugging
    DEBUG = False
    app = YutubApp(debug=DEBUG)
    app.mainloop()
