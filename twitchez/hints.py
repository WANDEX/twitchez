#!/usr/bin/env python3
# coding=utf-8

from twitchez import STDSCR
from twitchez import conf
import re


def get_hint_chars() -> str:
    return str(conf.setting("hint_chars"))


def total(items) -> tuple[int, int]:
    """Return (total_seq, hint_length) based on hint_chars,
    individual hint_length formula and len of items.
    total_seq = number of possible sequences,
    hint_length = [1-3] length of each hint.
    """
    hcl = len(get_hint_chars())
    sqr = hcl ** 2
    if hcl >= len(items):
        hint_length = 1
        total_seq = hcl
    elif sqr >= len(items):
        hint_length = 2
        total_seq = sqr
    else:
        hint_length = 3
        total_seq = sqr * 2 - hcl
    return total_seq, hint_length


def shorten_uniq_seq(out_seq):
    """Shorten all unique hint sequences and insert at the beginning."""
    tmp_seq = out_seq.copy()
    # shorten all sequences by one character
    for i, seq in enumerate(tmp_seq):
        wlc = seq[:-1]  # seq without last char
        tmp_seq.pop(i)
        tmp_seq.insert(i, wlc)
    # remove all elements that occurs more than once
    seq_set = set(tmp_seq)  # set() for less loop iterations
    for seq in seq_set:
        occurs = tmp_seq.count(seq)  # the number of times an element occurs
        if occurs > 1:
            while seq in tmp_seq:
                tmp_seq.remove(seq)
    if not tmp_seq:  # short unique sequences not found
        return out_seq
    # each letter associated with its position index
    order = {}
    for i, c in enumerate(get_hint_chars()):
        order[c] = i
    # compute the seq score by the order in which the letters appear in the sequence
    seq_score = {}
    for seq in tmp_seq:
        s1 = order[seq[0]]
        s2 = 0
        if len(seq) > 1:
            s2 = order[seq[1]]
        score = s1 + s2
        seq_score[seq] = score
    # dict of sequences sorted by the sequence score
    sorted_by_score = dict(sorted(seq_score.items(), key=lambda x: x[1]))
    sorted_short_seq = list(sorted_by_score.keys())
    sorted_short_seq.reverse()  # reverse() => we insert at the beginning
    # replace original seq by the shorter sequence as it occurs only once
    for sseq in sorted_short_seq:
        # original long seq found by the short seq
        llseq = [s for s in out_seq if re.search(f"^{sseq}.", s)]
        lseq = str(llseq[0])
        if lseq and lseq in out_seq:
            out_seq.remove(lseq)
        # insert all short sequences at the beginning
        out_seq.insert(0, sseq)
    return out_seq


def gen_hint_seq(items) -> list:
    """Generate from hint_chars list of unique sequences."""
    _, hint_length = total(items)
    hint_chars = get_hint_chars()

    # one letter length hints
    if hint_length == 1:
        return list(hint_chars)[:len(items)]

    # simple repeated values of hint_length
    repeated = []
    for c in hint_chars:
        # nn ee oo ... (if length_chars=2)
        repeated.append(c * hint_length)

    # make unique combinations of letters in strict order
    # generates sequence of 2 or 3 letter length hints
    combinations = []
    for r in repeated:
        new_seq = ""
        for ci in range(hint_length, 1, -1):
            pi = ci - 1
            for c in hint_chars:
                new_seq = r[:pi] + c + r[ci:]
                if new_seq in repeated:
                    continue  # skip
                if new_seq in combinations:
                    continue  # skip
                combinations.append(new_seq)

    hint_sequences = []
    hint_sequences.extend(repeated)
    hint_sequences.extend(combinations)
    # limit by the number of sequences that is enough for all items
    out_seq = hint_sequences[:len(items)]
    # NOTE: short seq are more convenient to type
    out_seq = shorten_uniq_seq(out_seq)
    # limit the number of sequences, strictly after shortening! (just in case)
    if len(out_seq) > len(items):
        return out_seq[:len(items)]
    else:
        return out_seq


def hint(items: list) -> list:
    """Return hint sequences for items."""
    return gen_hint_seq(items)


def find_seq(hints) -> str:
    """Input characters until only one hint sequence is found."""
    cinput = ""
    select = hints
    while len(select) > 1:
        c = str(STDSCR.get_wch())
        cinput += c
        select = [s for s in select if re.search(f"^{cinput}", s)]
    if not select:
        return ""
    if len(select) != 1:
        raise ValueError(f"len:({len(select)}) Only one item should be in the list:\n{select}")
    return str(select[0])
