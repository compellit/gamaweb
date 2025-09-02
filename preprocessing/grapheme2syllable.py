"""
Simple hyphenation of Galician words.
It does not handle foreign prefixes, e.g. pa-ra-psi-co-lo-xía is 
hyphenated as in cáp-su-la.
"""

# Copyright (C) 2007  Rafael C. Carrasco for the initial Java implementation,
# see https://www.dlsi.ua.es/%7Ecarrasco/progs/Hyphenator.java
# This program is free software; you can redistribute it and/or
# modify it under the terms of   the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# Adapted from José A. Mañas in Communications of the ACM 30(7), 1987.

# Initial Python by Javier Sober
# Current modifications by Pablo Ruiz

from copy import copy
import logging
import re
import utils as ut


g2s_logger = logging.getLogger("main.g2s")
#g2s_logger.setLevel(logging.DEBUG)

V = "[aáeéiíoóuúü]"            # vowels
A = "[aáeéíoóú]"               # open vowels
I = "[iuü]"                    # closed vowels
C = "[bcdfghjklmnñpqrstvxyz]"  # consonants
R = "[hlr]"                    # liquid and mute consonants
B = "[bcdfgjkmnñpqstvxyz]"     # non-liquid consonants

# patterns for syllabification
PATS = []
PATS.append("(" + I + "h" + I + ")")
PATS.append("(" + A + "h" + I + ")")
PATS.append("(" + I + "h" + A + ")")
PATS.append("(" + "." + C + R + V + ")")
PATS.append("(" + C + R + V + ")")
PATS.append("(" + "." + C + V + ")")
PATS.append("(" + A + A + ")")
PATS.append("(" + "." + ")")

# main regex combining all patterns
ALLPATS = PATS[0] + "|" + PATS[1] + "|" + PATS[2] + "|" + PATS[3] + "|" + PATS[4] + "|" + PATS[5] + "|" + PATS[6] + "|" + PATS[7]
PROG = re.compile(ALLPATS, re.I | re.U)

# In Galician, falling diphthongs do not get a stress mark in a stressed final syllable, list them here
UNACCENTED_DIPHTHONGS_GL = {"ai", "au", "ei", "ey", "eu", "oi", "ou"}


def get_matching_pat(pat_nbr: int) -> str:
    """
    Returns the separator (dash) if the matching pattern in `ALLPATS` above
    is 4, 6 or 7, otherwise returns an empty string.
    """
    switcher = {
        4: '-',
        6: '-',
        7: '-',
    }
    return switcher.get(pat_nbr, "")


def syllabify_core(input: str)-> str:
    """
    Syllabifies a word based on regex patterns.
    
    Args:
        input (str): The word to be syllabified.
    
    Returns:
        str: The syllabified word with dashes between syllables.
    """
    output = ""
    while len(input) > 0:
        output += input[0]
        # Return first matching pattern.
        m = PROG.search(input)
        output += get_matching_pat(m.lastindex)
        input = input[1:]
    return output


def search_stress_mark(silabas: list) -> int:
    """
    Given a list of strings where each string represents a syllable,
    return position in the list of a syllable bearing orthographic stress
    (the one with the acute accent mark in Galician or Spanish)

    Args:
        silabas (list): list of syllables as str
    Returns:
        int: position of the syllable with orthographic stress or -1 if none found
    """
    vowels_with_stress_mark = "[áéíóú]"
    reg = re.compile(vowels_with_stress_mark, re.I|re.U)
    for idx, syl in enumerate(silabas):
        if reg.search(syl):
            return idx
    return -1


def search_stressed_syll(silabas: list) -> bool:
    """
    The patterns in `unstressed_re` are searched in the last member of a list
    of strings each of which represents a syllable. If it matches, it means that
    the word has antepenult stress, because words whose final syllable matches
    the pattern do not have final stress, and antepenult or earlier stress are
    already detected by :func:`search_stress_mark`.
    
    Args:
        silabas (list): list of syllables as str

    Returns:
        bool: True if the last syllable matches the unstressed pattern (i.e.
              word has penult stress), False otherwise
    """
    unstressed_re = r"(([aeiou])|(n)|([aeiou]s))\Z"
    reg = re.compile(unstressed_re, re.I|re.U)
    if reg.search(silabas[-1]):
        return True
    else:
        return False


def _has_unaccented_diphthong(syll: str) -> bool:
    """
    Check whether a falling diphthong (without a stress mark) is in the final syllable.

    Args:
        syll (str): The syllable to check.

    Returns:
        bool: True if the syllable contains an unaccented diphthong, False otherwise.
    """
    for di in UNACCENTED_DIPHTHONGS_GL:
        if di in syll.lower():
            return True
    return False


def mark_stress(sylls: list[str], diacritic: str = "´", spanishfy: bool = False) -> tuple[str, str, str, int]:
    """
    Given a list of syllables for a word, marks the stressed syllable position
    in several ways.
    
    Args:
        sylls (list[str]): List of syllables as strings.
        diacritic (str): Diacritic to prefix the stressed syllable in the output.
            Default is "´" (acute accent).
        spanishfy (bool): If True, adds a stress mark to final syllables with a falling
            diphthong. These bear no stress mark in Galician, but in Spanish they do. Since
            some of our tools are meant for Spanish, this option is useful
    
    Returns:
        tuple: The first member contains the stressed syllable in allcaps,
               the second has the stressed syllable prefixed with a diacritic,
               the third one is the original syllabification without extra stress marks,
               the last one is the position of the stressed syllable, indexed from the end of the word
    """
    orig_syll = copy(sylls)
    # in `sylls_diac` the stressed syllable will be marked with the value of `diacritic`
    sylls_diac = copy(sylls)
    stressposi = None
    if len(sylls) == 1:
        sylls[0] = sylls[0].upper()
        sylls_diac[0] = diacritic + sylls_diac[0]
        stressposi = 0
    else:
        last = len(sylls) - 1
        penult = len(sylls) - 2
        stress_mark = search_stress_mark(sylls)
        stressposi = stress_mark
        if stress_mark != -1:
            sylls[stress_mark] = sylls[stress_mark].upper()
            sylls_diac[stress_mark] = diacritic + sylls_diac[stress_mark]
        # exception for Galician's falling diphthongs
        # (get no stress mark in final stressed syllable)
        elif _has_unaccented_diphthong(sylls[-1]):
            if spanishfy and len(sylls) > 1:
                sylls[last] = ut._spanishfy(sylls[last], sylls)
                sylls_diac = copy(sylls) # to update after spanishfy
            sylls[last] = sylls[last].upper()
            sylls_diac[last] = diacritic + sylls_diac[last]
            stressposi = len(sylls) - 1
        elif search_stressed_syll(sylls):
            sylls[penult] = sylls[penult].upper()
            sylls_diac[penult] = diacritic + sylls_diac[penult]
            stressposi = len(sylls) - 2
        else:
            sylls[last] = sylls[last].upper()
            sylls_diac[last] = diacritic + sylls_diac[last]
            stressposi = len(sylls) - 1

    # normalize stressed position to a negative index
    # (since we speak of final, penult, or antepenult etc. stress)
    stressposi = 0 - (len(sylls) - stressposi)

    word = "-".join(x for x in sylls)
    word_diac = "-".join(x for x in sylls_diac)
    orig_word = "-".join(x for x in sylls_diac).replace(diacritic, "")
    return word, word_diac, orig_word, stressposi


def _resyllabify_close_sequence(sl: list) -> list:
    """
    Makes sure that sequences like uu, ii, UU, II are be syllabified
    in two different syllables.
    
    Args:
        sl (list): list of syllables as strings
    
    Returns:
        list: a copy of the syllable list with close vowerl sequences
              resyllabified correctly
    """
    for idx, sy in enumerate(sl):
        symatch = re.match(r"^(.*?([iu]))(\2.*?)$", sy)
        if symatch:
            sl[idx] = symatch.group(1)
            sl.insert(idx+1, symatch.group(3))
    return sl


def _resyllabify_homogeneous_diphthong_(sl: list)-> list:
    """
    Resyllabifies  closed vowels the second of which bears a stress mark
    (e.g. Galician "muíño" goes to "mu-í-ño")
    
    Args:
        sl (list): list of syllables as strings
    Returns:
        list: a copy of the syllable list with homogeneous diphthongs
              resyllabified correctly
    """
    for idx, sy in enumerate(sl):
        symatch = re.match(r"^(.*?[^gq])([iu])([íú])(.*?)$", sy)
        if symatch:
            # print sl, sy
            sl[idx] = symatch.group(1) + symatch.group(2)
            sl.insert(idx+1, symatch.group(3))
            if symatch.group(4):
                sl.insert(idx+2, symatch.group(4))
    return sl


def _resyllabify_osbstruent_liquid(sl: list) -> list:
    """
    Obstruent-liquid onsets were sometimes syllabified wrongly when applied
    `syllabify_core` to a large corpus. This is fixed here.
    
    Args:
        sl (list): list of syllables as strings
    Returns:
        list: a copy of the syllable list with obstruent-liquid onsets
    """
    sl_copy = copy(sl)
    for idx, sy in enumerate(sl):
        try:
            if (re.match(r"^[pbftdkcg]$", sy.lower())
                and sl[idx+1][0].lower() in {"l", "r"}):
                sl_copy[idx+1] = "".join((sl[idx][-1], sl[idx+1]))
                del sl_copy[idx]
        except IndexError:
            pass
    return sl_copy


def _resyllabify_double_l(sl: list) -> list:
    """
    The "ll" digraph for the lateral palatal were sometimes syllabified
    into two syllables when applied `syllabify_core` to a large corpus.
    This is fixed here, adding it as onset to the second one.

    Args:
        sl (list): list of syllables as strings
    Returns:
        list: a copy of the syllable list with obstruent-liquid onsets
    """
    sl_copy = copy(sl)
    for idx, sy in enumerate(sl):
        try:
            # I'm not sure why did it this way (back in 2017). 
            # From the rgx, what seems to be happening is that 
            # the first "syllable" is just a single "l", perhaps
            # there were missyllabifications with such (incorrect) "syllables"
            # and this function was meant to fix them.
            if (re.match(r"^l$", sy.lower())
                and sl[idx+1][0].lower() == "l"):
                sl_copy[idx+1] = "".join((sl[idx][-1], sl[idx+1]))
                del sl_copy[idx]
        except IndexError:
            pass
    return sl_copy


def _resyllabify_liquids(sl: list) -> list:
    """
    This fixes cases where words like "burla" or "bulra" are 
    syllabified as "bu-rla" and "bu-lra" instead of "bur-la" and "bul-ra".

    Args:
        sl (list): list of syllables as strings

    Returns:
        list: a copy of the syllable list with the liquids
              resyllabified correctly
    """
    sl_copy = copy(sl)
    for idx, sy in enumerate(sl):
        try:
            liquid_seq_in_same_syllable = r"^(?:lr|rl|nr)"
            if re.search(liquid_seq_in_same_syllable, sy.lower()):
                sl_copy[idx] = sy[1:]
                sl_copy[idx-1] = sl_copy[idx-1] + sy[0]
        except IndexError:
            pass
    return sl_copy


def _resyllabify_ch(sl: list) -> list:
    """
    The "ch" digraph for the postalveolar affricate was sometimes syllabified
    into two syllables when applied `syllabify_core` to a large corpus.
    This is fixed here, adding it as onset to the second one.

    Args:
        sl (list): list of syllables as strings
    Returns:
        list: a copy of the syllable list with obstruent-liquid onsets
    """
    sl_copy = copy(sl)
    for idx, sy in enumerate(sl):
        try:
            if (re.match(r"^c$", sy.lower())
                and sl[idx+1][0].lower() == "h"):
                sl_copy[idx+1] = "".join((sl[idx][-1], sl[idx+1]))
                del sl_copy[idx]
        except IndexError:
            pass
    return sl_copy


def _apply_fixes(sl):
    sl = _resyllabify_close_sequence(sl) # this applies
    sl = _resyllabify_homogeneous_diphthong_(sl) # this applies
    sl = _resyllabify_osbstruent_liquid(sl)
    sl = _resyllabify_double_l(sl) # this works
    sl = _resyllabify_liquids(sl) # this one is relevant
    sl = _resyllabify_ch(sl) # this applies
    return sl


def syllabify_full(word, diacritic="´", spanishfy=False):
    """
    Syllabification with the main algorithm plus stress marking and some
    postprocessing fixes. 
    """
    # in case more than one word, out will have them all, with the stressed syllable
    # in upper case
    out = ''
    # avoid variables to be not assigned if wordre is empty
    wdiac = worig = stressposi = None    
    wordre = word.split(" ")
    for m in wordre:
        sylls_pre = syllabify_core(m).split("-")
        sylls_post = _apply_fixes(sylls_pre)
        wupper, wdiac, worig, stressposi = mark_stress(sylls_post, diacritic=diacritic, spanishfy=spanishfy)
        out += wupper + " "
    # TODO: only the 'wupper' version makes it to `out`, should add a check that no spaces
    # in input string actually, to parse only one word at a time and have all output variants
    out = out[:-1]
    return out, wdiac, worig, stressposi


if __name__ == "__main__":
    for x in syllabify_full("Ángel"): print(x, "|", )
