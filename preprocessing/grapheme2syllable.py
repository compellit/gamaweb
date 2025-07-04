#!/usr/bin/python
# -*- coding: utf-8 -*-

#Copyright (C) 2007  Rafael C. Carrasco
#This program is free software; you can redistribute it and/or
#modify it under the terms of   the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.
#Adapted from José A. Mañas in Communications of the ACM 30(7), 1987.


# A class that performs simple hypenation of Spanish words.
# It does not work with foreign words as pa-ra-psi-co-lo-gía:
# hyphenated as in cáp-su-la.

#Implementado en Pytho por Javier Sober

from copy import copy
import logging
import re
import utils as ut


g2s_logger = logging.getLogger("main.g2s")
#g2s_logger.setLevel(logging.DEBUG)

v = "[aáeéiíoóuúü]"            # vowels
a = "[aáeéíoóú]"               # open vowels
i = "[iuü]"                    # closed vowels
c = "[bcdfghjklmnñpqrstvxyz]"  # consonants
r = "[hlr]"                    # liquid and mute consonants
b = "[bcdfgjkmnñpqstvxyz]"     # non-liquid consonants

P = []
P.append("(" + i + "h" + i + ")")
P.append("(" + a + "h" + i + ")")
P.append("(" + i + "h" + a + ")")
P.append("(" + "." + c + r + v + ")")
P.append("(" + c + r + v + ")")
P.append("(" + "." + c + v + ")")
P.append("(" + a + a + ")")
P.append("(" + "." + ")")


allpats =  P[0] + "|"  + P[1] + "|" + P[2] + "|" + P[3] +  "|"+ P[4] + "|" + P[5] + "|"  + P[6] + "|" + P[7]
prog = re.compile(allpats, re.I|re.U)


# In Galician, falling diphthongs do not get a stress mark in a stressed final syllable, list them here
UNACCENTED_DIPHTHONGS_GL = {"ai", "au", "ei", "ey", "eu", "oi", "ou"}

# Return separator if matching pattern is 4,6 or 7
def getGroup( x ):
    switcher = {
        4: '-',
        6: '-',
        7: '-',
    }
    return switcher.get(x, "")


## Hyphenates a word.
## @param The word to be hyphenated.
## @return hyphenation.
def parse ( input ):
    output = ""
    while (len(input)>0):
        output += input[0]
        ## Return first matching pattern.
        m = prog.search(input)
        output += getGroup(m.lastindex)
        input = input[1:]
    return output


def buscarTilde( silabas ):
    """
    Given a list of str or unicodes representing a syllable,
    return position in the list of a syllable bearing
    orthographic stress (with the acute accent mark in Spanish)
    @param silabas: list of syllables as str or unicode each
    @return: position or -1 if no orthographic stress
    @rtype int
    """
    tildes = "[áéíóú]"
    reg = re.compile(tildes, re.I|re.U)
    pos = 0
    for sil in silabas:
        if (reg.search(sil)):
            return pos
        pos += 1

    return -1


def buscarTonica( silabas ):
    # if find that in last syllable, penult is stressed
    # (since buscarTilde takes care of antepenult)
    tonica = r"(([aeiou])|(n)|([aeiou]s))\Z"
    reg = re.compile(tonica, re.I|re.U)
    if (reg.search(silabas[len(silabas)-1])):
        return True
    else:
        return False


def _has_unaccented_diphthong(syll):
    """
    Check whether a rising (unaccented) diphthong is in the final syllable.
    """
    for di in UNACCENTED_DIPHTHONGS_GL:
        if di in syll.lower():
            return True
    return False


def acentuacion ( silabas, diacritic="´" , spanishfy=False ):
    #TODO here can see the index in silabas and return it
    #TODO so that don't have to rely on uppercase ...
    orig_syll = copy(silabas)
    # here the stressed syllable will be marked with the value of the diacritic keyword a
    silabas_diac = copy(silabas) 
    stressposi = None
    if (len(silabas) == 1):
        silabas[0] = silabas[0].upper()
        silabas_diac[0] = diacritic + silabas_diac[0]
        stressposi = 0
    else:
        tilde = buscarTilde(silabas)
        stressposi = tilde
        if (tilde != -1):
            silabas[tilde] = silabas[tilde].upper()
            silabas_diac[tilde] = diacritic + silabas_diac[tilde]
        # exception for Galician's falling diphthongs (get no stress mark in final stressed syllable)
        elif _has_unaccented_diphthong(silabas[-1]):
            #TODO why is this indexed c/o len(x)? (and not just use the index)?
            #breakpoint()
            if spanishfy and len(silabas) > 1:
                silabas[len(silabas) - 1] = ut._spanishfy(silabas[len(silabas) - 1], silabas)
                silabas_diac = copy(silabas) # to update after spanishfy
                #g2s_logger.debug(f"Spanishfied: original [{"-".join(orig_syll)}] postprocessed [{"-".join(silabas)}]")
            silabas[len(silabas) - 1] = silabas[len(silabas) - 1].upper()
            silabas_diac[len(silabas) - 1] = diacritic + silabas_diac[len(silabas) - 1]
            stressposi = len(silabas) - 1
        elif (buscarTonica(silabas)):
            #TODO why is this indexed c/o len(x)? (and not just use the index)?
            silabas[len(silabas)-2] = silabas[len(silabas)-2].upper()
            silabas_diac[len(silabas)-2] = diacritic + silabas_diac[len(silabas)-2]
            stressposi = len(silabas) - 2
        else:
            silabas[len(silabas)-1] = silabas[len(silabas)-1].upper()
            silabas_diac[len(silabas)-1] = diacritic + silabas_diac[len(silabas)-1]
            stressposi = len(silabas) -1

    # normalize stressed position to a negative index
    # (since we speak of final, penult, or antepenult etc. stress)
    stressposi = 0 - (len(silabas) - stressposi)

    palabra = "-".join(x for x in silabas)
    palabra_diac = "-".join(x for x in silabas_diac)
    orig_word = "-".join(x for x in silabas_diac).replace(diacritic, "")
    return palabra, palabra_diac, orig_word, stressposi


def _resyllabify_close_sequence(sl):
    """
    Sequences like uu, ii, UU, II must be syllabified
    in two different syllables.
    @param sl: syllable list
    """
    for idx, sy in enumerate(sl):
        symatch = re.match(r"^(.*?([iu]))(\2.*?)$", sy)
        if symatch:
            # print sl, sy
            sl[idx] = symatch.group(1)
            sl.insert(idx+1, symatch.group(3))
    return sl


def _resyllabify_homogeneous_diphthong_(sl):
    """
    Resyllabify closed vowels the second of which bears a stress mark
    (e.g. Galician "muíño" goes to "mu-í-ño")
    @param sl: syllable list
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


def _resyllabify_osbstruent_liquid(sl):
    """
    Obstruent-liquid onsets were sometimes syllabified wrongly when applied
    this to a large corpus. Fix here.
    @param sl: list of syllables
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


def _resyllabify_double_l(sl):
    """
    The "ll" digraph for the lateral palatal were sometimes syllabified
    into two syllables when ran this with a full corpus.
    Fix here, adding it as onset to the second one.
    @param sl: list of syllables
    """
    sl_copy = copy(sl)
    for idx, sy in enumerate(sl):
        try:
            if (re.match(r"^l$", sy.lower())
                and sl[idx+1][0].lower() == "l"):
                sl_copy[idx+1] = "".join((sl[idx][-1], sl[idx+1]))
                del sl_copy[idx]
        except IndexError:
            pass
    return sl_copy


def _resyllabify_ch(sl):
    """
    The "ch" digraph for the postalveolar affricate was sometimes syllabified
    into two syllables when applied this to a large corpus.
    Fix here, adding it as onset to the second one.
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
    sl = _resyllabify_close_sequence(sl)
    sl = _resyllabify_homogeneous_diphthong_(sl)
    #TODO are fixes below here relevant or not?
    # these errors occcurred when applying to DISCO, not when
    # testing with the test items in tests ...
    # the 'close_sequence' one must be kept, occurs even in tests
    sl = _resyllabify_osbstruent_liquid(sl)
    sl = _resyllabify_double_l(sl)
    sl = _resyllabify_ch(sl)
    return sl


def silabeo(word, diacritic="´", spanishfy=False):
    out = ''
    # avoid variables to be not assigned if wordre is empty
    diac = orig = stressposi = None
    
    wordre = word.split(" ")

    for m in wordre:
        l = parse(m).split("-")
        l = _apply_fixes(l)
        t, diac, orig, stressposi = acentuacion(l, diacritic=diacritic, spanishfy=spanishfy)
        out += (t)+" "
    out = out[:len(out)-1]
    return out, diac, orig, stressposi


if __name__ == "__main__":
    # print(silabeo("aéreo"))
    # print(silabeo("casa"))
    # print(silabeo("subrayar"))
    for x in silabeo("Ángel"): print(x,"|",)
    # print(silabeo("aéreo"))
    # print(silabeo("casa"))
    # print(silabeo("subrayar"))
