# twitchez

<img src="https://cdn.betterttv.net/emote/5b490e73cf46791f8491f6f4/3x"
align="right" title="HACKERMANS" alt="The famous HACKERMANS twitch.tv emote"
style="width: 112px; height: 112px">

![PyPI - Status](https://img.shields.io/pypi/status/twitchez?style=flat-square)
![PyPI](https://img.shields.io/pypi/v/twitchez?style=flat-square)
![PyPI - License](https://img.shields.io/pypi/l/twitchez?style=flat-square)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/twitchez?style=flat-square)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/WANDEX/twitchez?style=flat-square)
![GitHub last commit](https://img.shields.io/github/last-commit/WANDEX/twitchez?style=flat-square)

twitchez - TUI client for twitch.tv with thumbnails support that works right in your terminal.

Support of rendering images by the terminal is not required, ueberzug will handle that.\
You may ask -- **"Is this magic?"** -- Well **YES**, the black magic! Welcome to the club!

https://user-images.githubusercontent.com/15724752/152787467-dc2a8871-43e5-4530-94b1-e14383c8b18e.mp4

#### [alpha] WIP NOTICE: project development stage
This project is still in the early stage of development,
you may, and probably will, experience corrupted terminal state,
so run this client in a separate terminal window
so you don't get frustrated if the client accidentally crashes.

## Features
* Explore twitch without leaving your terminal
* Flexible configuration via user config (including custom cmd)
* Completely keyboard driven workflow
    * Zero mouse interaction. `F1 / ?` for help about key mappings
    * Redefine keys and hint chars for your keyboard layout
    * Link hints similar as in (Vimium, Surfingkeys, etc.)
    * Interactive select of one entry from all
([fzf](https://github.com/junegunn/fzf),
[dmenu](https://tools.suckless.org/dmenu/),
or any other program via custom cmd)
* Bookmarks & Tabs (add, delete, next/prev, jump to tab by name)
    * Following live channels
    * Streams per category
    * Videos per channel (archive/past broadcasts, clips, highlights, uploads)
* Open video/stream url in external video player
([streamlink](https://github.com/streamlink/streamlink),
[mpv](https://github.com/mpv-player/mpv),
or any other program via custom cmd)
    * Three independent user cmd and keys to open url as (stream, video, extra)
    * Copy url to clipboard
    * Open chat url in default browser or via custom cmd
* Thumbnails are drawn by [ueberzug](https://github.com/seebye/ueberzug) (**X11 only**)
(ueberzug is an **optional dependency**)
    * If ueberzug is not installed **text mode without thumbnails** will be used

###### *If you do not know what X11 is - for you this means thumbnails will be drawn on Linux only (not exactly)*

## Configuration
Look inside `twitchez/config/` dir to see all available settings, those are defaults.\
**Do not change default config files**, create new in the user config dir: `config.conf`, `keys.conf`.\
The default user config dir is `$XDG_CONFIG_HOME/twitchez/`, or `$HOME/.config/twitchez/` by default.\
Settings from default config files are used as fallback for settings you haven't changed in your user config.

## Install
### Pip
Install [twitchez](https://pypi.org/project/twitchez/) via [pip](https://pip.pypa.io/en/stable/)
into user-wide environment:
```
$ pip3 install --user twitchez
```
or system-wide environment:
```
# pip3 install twitchez
```
To update, add the `--upgrade` or `-U` option.

### Install ueberzug (Optional)
#### ueberzug must be additionally installed to display thumbnails!
If [ueberzug](https://github.com/seebye/ueberzug#installation)
is not installed or not supported by your platform  **text mode without thumbnails** will be used.

## Troubleshooting
##### If thumbnails partially overlap underlying text (it is very font dependent):
* set width/height modifier in user config
* adjust your terminal font size by +1 etc
* try different terminal font

## License
[GPL-3.0](https://choosealicense.com/licenses/gpl-3.0/)
