# twitchez
TUI client for twitch with thumbnails.

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
