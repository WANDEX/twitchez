# twitchez

<a href="https://betterttv.com/emotes/shared/search?query=hackermans">
<img src="https://cdn.betterttv.net/emote/5b490e73cf46791f8491f6f4/3x"
align="right" title="HACKERMANS" alt="The famous HACKERMANS twitch.tv emote"
style="width: 112px; height: 112px">
</a>

![PyPI - Status](https://img.shields.io/pypi/status/twitchez?style=flat-square)
![PyPI](https://img.shields.io/pypi/v/twitchez?style=flat-square)
![PyPI - License](https://img.shields.io/pypi/l/twitchez?style=flat-square)
<a href="https://pypistats.org/packages/twitchez">
![PyPI - Downloads](https://img.shields.io/pypi/dm/twitchez?style=flat-square)
</a>

twitchez - TUI client for twitch.tv with thumbnails support that works right in your terminal.

Support of rendering images by the terminal is not required, ueberzugpp will handle that.\
You may ask -- **"Is this magic?"** -- Well **YES**, the black magic! Welcome to the club!

Since **v0.0.7** twitchez supports **ueberzugpp** -- this expands list of supported platforms:\
**linux / macOS / windows / freeBSD / X11 / Wayland /** any terminal with **SIXEL** support e.g.
[WezTerm](https://github.com/wez/wezterm)

### Leave a star to show interest in further development of the project ⭐️

https://user-images.githubusercontent.com/15724752/152787467-dc2a8871-43e5-4530-94b1-e14383c8b18e.mp4

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
* Thumbnails are drawn by the [ueberzugpp](https://github.com/jstkdng/ueberzugpp) (optional dependency)

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

#### Install ueberzugpp to display thumbnails (Optional)
If [ueberzugpp](https://github.com/jstkdng/ueberzugpp?tab=readme-ov-file#install)
is not installed **text mode without thumbnails** will be used.

You also can [build from source](https://github.com/jstkdng/ueberzugpp?tab=readme-ov-file#build-from-source)
and install **build dir** e.g. `# sudo cmake --install build`

## Troubleshooting
##### If you installed ueberzugpp but still not see thumbnails:
* override default ueberzugpp output **via twitchez user config** *(check **default.conf** it has example)*
* check available **output** options in **ueberzugpp** via `$ ueberzugpp layer --help`
* x11 and/or wayland (may not be available if disabled in compilation) -- build ueberzugpp from source
* if you want to draw via e.g. sixel, make sure that your terminal have such capability
* [WezTerm](https://github.com/wez/wezterm) has sixel support, try to launch twitchez in it

##### If thumbnails partially overlap underlying text (it is very font dependent):
* set width/height modifier in user config
* adjust your terminal font size by +1 etc
* try different terminal font

## License
[GPL-3.0](https://choosealicense.com/licenses/gpl-3.0/)
