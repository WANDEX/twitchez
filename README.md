# twitchez
TUI client for twitch with thumbnails.

#### [pre-alpha] WIP NOTICE: project development stage
This project is still in the early stage of development,
you may, and probably will, experience corrupted terminal state,
so run this client in a separate terminal window
so you don't get frustrated if the client accidentally crashes.

## Features
* Explore twitch without leaving your terminal. HACKERMANS B)
* Flexible configuration via user config (including custom cmd)
* Completely keyboard driven workflow
    * Zero mouse interaction
    * Redefine keys and hint chars for your keyboard layout
    * Link hints similar as in (Vimium, Surfingkeys, etc.)
    * Interactive select of one entry from all
([fzf](https://github.com/junegunn/fzf),
[dmenu](https://tools.suckless.org/dmenu/),
or any other program via custom cmd)
* Tabs (add, delete, next/prev, jump to tab by name)
    * Following live channels
    * Streams per category
    * Videos per channel (archive/past broadcasts, clips, highlights, uploads)
* Open video/stream url in external video player
([streamlink](https://github.com/streamlink/streamlink),
[mpv](https://github.com/mpv-player/mpv),
or any other program via custom cmd)
    * Three independent user cmd and keys to open url as (stream, video, extra)
    * Copy url to clipboard
* Thumbnails are drawn by [ueberzug](https://github.com/seebye/ueberzug) (**X11 only**)\
*If you do not know what X11 is - for you this means thumbnails will be drawn on Linux only (not exactly).*

## Configuration
Look inside `config/` dir to see all available settings, those are defaults.\
**Do not change default config files**, create new in the user config dir: `config.conf`, `keys.conf`.\
The default user config dir is `$XDG_CONFIG_HOME/twitchez/`, or `$HOME/.config/twitchez/` by default.\
Settings from default config files are used as fallback for settings you haven't changed in your user config.

## Usage (temporary for pre-alpha stage)
```sh
# (you need to do this step every time your auth token expires)
# get your twitch auth token:
python auth.py
# after successful generation of .private file with valid twitch.tv auth token
# client will be able to get twitch data via API requests, run client:
python init.py
```

## Troubleshooting
###### If you tried to run client without auth token or if your auth token expired:
* You are required to get new twitch auth token via `python auth.py`
* You are required to wait default twitch data update time (5 min)\
in order to update data for page requested previously without valid auth token.

## License
[GPL-3.0](https://choosealicense.com/licenses/gpl-3.0/)
