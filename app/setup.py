import sys, os
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"includes": ["tkinter"],
                     "include_files": ["tcl86t.dll", "tk86t.dll", "icon.ico"],
                     "excludes": ["email", "html", "http", "pydoc_data", "unittest", "xml", "urllib"]}

# Definition of shortcuts created during installation
shortcut_table = [
        ("DesktopShortcut",        # Shortcut
         "DesktopFolder",          # Directory_
         "GBC-Reader",             # Name
         "TARGETDIR",              # Component_
         "[TARGETDIR]/gbc-reader.exe",   # Target
         None,                     # Arguments
         None,                     # Description
         None,                     # Hotkey
         None,                     # Icon
         None,                     # IconIndex
         None,                     # ShowCmd
         'TARGETDIR'               # WkDir
         ),
        ("StartMenuShortcut",      # Shortcut
         "StartMenuFolder",        # Directory_
         "GBC-Reader",             # Name
         "TARGETDIR",              # Component_
         "[TARGETDIR]/gbc-reader.exe",   # Target
         None,                     # Arguments
         None,                     # Description
         None,                     # Hotkey
         None,                     # Icon
         None,                     # IconIndex
         None,                     # ShowCmd
         'TARGETDIR'               # WkDir
         ),
    ]

msi_data = {"Shortcut": shortcut_table}
bdist_msi_options = {"data": msi_data}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(name = "GBC-Reader",
      version = "0.1",
      description = "Game Boy Cartridge Reader Software",
      author="Fabian Friedl", author_email="tiacs@tiacs.net",
      options = {"build_exe": build_exe_options, "bdist_msi": bdist_msi_options},
      executables = [Executable("main.py", base=base, icon="icon.ico", targetName="gbc-reader.exe",
                                copyright="(c) Fabian Friedl 2017")])
