# Retroarch_TUI
Terminal user interface for launching games via Retroarch

![Retroarch_TUI](https://github.com/jhkeller/retroarch_tui/blob/main/screenshots/retroarch_tui_screenshot.png?raw=true)

Download cores from within retroarch.

###Setup 

config.json with path to retroarch/cores/roms

```json
{
  "retroarch_path": "retroarch",
  "systems": [
    {
      "name": "SNES",
      "core": "~/.config/retroarch/cores/snes9x_libretro.so",
      "roms": "/mnt/Emulators/roms/snes/roms"
    },
    {
      "name": "PlayStation",
      "core": "~/.config/retroarch/cores/mednafen_psx_hw_libretro.so",
      "roms": "/mnt/Emulators/roms/ps/roms",
      "folder_mode": true
    }
  ]
}


### Features

Search within roms to filter, add "/" before search for inclusive search.

