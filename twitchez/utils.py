#!/usr/bin/env python3
# coding=utf-8

from . import conf
from datetime import datetime
from difflib import SequenceMatcher
from os.path import getmtime
from re import compile
from threading import Thread
import textwrap
import time


# visible length of one emoji in terminal cells
EMOJI_CELLS = int(conf.setting("emoji_cells"))

EMOJI_PATTERN = compile(
    "["
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F700-\U0001F77F"  # alchemical symbols
    "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
    "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
    "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
    "\U0001FA00-\U0001FA6F"  # Chess Symbols
    "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
    "\U00002702-\U000027B0"  # Dingbats
    "\U000024C2-\U0001F251"
    "]+"
)


def tryencoding(string: str) -> str:
    """Return string in default encoding or
    if not printable -> try to re-encode into utf-16."""
    if not string.isprintable():
        try:
            string = string.encode('utf-16', 'surrogatepass').decode("utf-16", "ignore")
        except (UnicodeEncodeError, UnicodeDecodeError) as e:
            string = str(e)
    return string


def demojize(str: str) -> str:
    """Return string without emojis."""
    return EMOJI_PATTERN.sub(r'', str)


def emoji_count(str: str) -> int:
    """Returns the count of emojis in a string."""
    return len(str) - len(demojize(str))


def tlen(str: str) -> int:
    """Return len of str respecting emoji visible length in terminal cells.
    EMOJI_CELLS: visible length of one emoji in terminal cells.
    """
    if EMOJI_CELLS < 2:
        return len(str)
    else:
        return EMOJI_CELLS * emoji_count(str) + len(demojize(str))


def secs_since_mtime(path):
    """time_now - target_mtime = int(secs)."""
    return int(time.time() - getmtime(path))


def replace_pattern_in_all(inputlist, oldstr, newstr) -> list:
    """Replace oldstr with newstr in all items from a list."""
    outputlist = []
    for e in inputlist:
        outputlist.append(str(e).replace(oldstr, newstr))
    return outputlist


def add_str_to_list(input_list, string) -> list:
    """Add string to the end of all elements in a list."""
    outputlist = [e + str(string) for e in input_list]
    return outputlist


def insert_to_all(list, string, opt_sep="") -> list:
    """ Insert the string at the beginning of all items in a list. """
    string = str(string)
    if opt_sep:
        string = f"{string}{opt_sep}"
    string += '% s'
    list = [string % i for i in list]
    return list


def strws(str: str) -> str:
    """Return a str with whitespace characters replaced by '_'."""
    return str.strip().replace(" ", "_")


def strclean(str: str) -> str:
    """return slightly cleaner string."""
    # remove unneeded characters from string
    s = str.replace("\n", " ").replace("\t", " ")
    # replace repeating whitespaces by single whitespace
    s = ' '.join(s.split())
    s = s.strip()
    return s


def strtoolong(str: str, width: int, indicator="..") -> str:
    """Return str slice of width with indicator at the end.
    (to show that the string cannot fit completely in width)
    """
    if tlen(str) > width:
        str_fit_in_width = str[:width]
        # visible width in terminal cells that str occupies
        terminal_cells = tlen(str_fit_in_width)
        if terminal_cells > width:
            ec = emoji_count(str_fit_in_width)
            cut = ec + len(indicator)
            out_str = str_fit_in_width[:-cut] + indicator
        else:
            out_str = str_fit_in_width[:-len(indicator)] + indicator
        return out_str
    else:
        return str


def word_wrap_title(string: str, width: int, max_len: int, max_lines=3) -> str:
    """Word wrap title string."""
    string = strclean(string)
    if tlen(string) <= width:
        return string
    title_lines = textwrap.wrap(
        string, width, max_lines=max_lines,
        expand_tabs=False, replace_whitespace=True,
        break_long_words=True, break_on_hyphens=True, drop_whitespace=True
    )
    out_str = ""
    cline = 0
    for line in title_lines:
        cline += 1
        if len(line) == width:
            out_str += line
        else:
            out_str += f"{line}\n"
    # limit string len
    if len(out_str) > max_len:
        out_str = out_str[:max_len]
    # add mask only if length of last line met condition
    if len(title_lines[-1]) < width // 2:
        mask = "  "  # mask to differentiate from underlying text
        out_str = out_str[:-len(mask) + 1] + mask
    return out_str


def sdate(isodate: str) -> str:
    """Take iso date str and return shorten date str."""
    # remove Z character from default twitch date (2021-12-08T11:43:43Z)
    idate = isodate.replace("Z", "")
    vdate = datetime.fromisoformat(idate).isoformat(' ', 'minutes')
    today = datetime.today().isoformat(' ', 'minutes')
    current_year = today[:4]
    if current_year not in vdate:
        pattern = vdate[-6:]  # cut off only time
    else:
        sm = SequenceMatcher(None, vdate, today)
        match = sm.find_longest_match(0, len(vdate), 0, len(today))
        # longest common string between two
        pattern = vdate[match.a: match.a + match.size - 1]
    # remove pattern, cut leading '-' and strip whitespaces
    sdate = str(vdate).replace(pattern, "").strip("-").strip()
    return sdate


def duration(duration: str, simple=False, noprocessing=False) -> str:
    """Take twitch duration str and return duration with : as separators.
    Can optionally return a str without processing or with simple str processing.
    """
    if noprocessing:
        return duration
    if simple:
        # downside is very variable length of str and subjective ugliness of result.
        return duration.replace("h", ":").replace("m", ":").replace("s", ":").strip(":")
    # Don't see any real benefit of the following code over a silly simple one-liner :)
    # Result of the following algorithm are prettier, but also produces longer str.
    if "h" in duration:
        # extract hours from string
        H, _, _ = duration.partition("h")
        H = int(H.strip())
        # fix: if hours > 23 => put hours as simple str into format
        if H > 23:
            ifmt = f"{H}h%Mm%Ss"
            ofmt = f"{H}:%M:%S"
        else:
            ifmt = "%Hh%Mm%Ss"
            ofmt = "%H:%M:%S"
    elif "m" in duration:
        ifmt = "%Mm%Ss"
        ofmt = "%M:%S"
    else:
        return duration
    idur = datetime.strptime(duration, ifmt)
    odur = str(idur.strftime(ofmt))
    return odur


def background(func):
    """use @background decorator above the function to run in the background."""
    def background_func(*args, **kwargs):
        Thread(target=func, args=args, kwargs=kwargs).start()
    return background_func
