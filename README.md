# Retroarch_TUI
Terminal user interface for launching games via Retroarch

![Retroarch_TUI](https://github.com/jhkeller/retroarch_tui/blob/main/screenshots/retroarch_tui_screenshot.png?raw=true)

Download cores from within retroarch.

### Features

Search within roms to filter, add "/" before search for inclusive search.

###Setup 

config.json with path to retroarch/cores/roms



```json
{
  "retroarch_path": "retroarch",
  "systems": [
    {
      "name": "SNES",
      "core": "PATH/TO/CORES/snes9x_libretro.so",
      "roms": "PATH/TO/ROMS"
    },
    {
      "name": "PlayStation",
      "core": "PATH/TO/CORES/mednafen_psx_hw_libretro.so",
      "roms": "PATH/TO/ROMS",
      "folder_mode": true
    }
  ]
}



