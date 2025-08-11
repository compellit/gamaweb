"""Utilities for GAMA views"""

import re
import roman

PUNCT_AND_BLANKS = re.compile(r"^['!¡\"#$%&()*+,./:;<=>?¿@\[\]^_`{|}~'—\s-]+$", re.U|re.MULTILINE)  # Matches any character that is not a word character or whitespace


def _preprocess_poem_text(ptext: str) -> str:
    """
    Preprocesses poem text removing lines with only punctuation or blanks,
    and lines that only contain Roman numerals.
    """
    # if want to remove lines with only one token
    # ptext = re.sub(r"(?:^|\n)\s*[^\s]+\s*\n", "", ptext)
    ptext = re.sub(PUNCT_AND_BLANKS, "\n", ptext)
    ptext = _remove_roman_numeral_headings(ptext)
    ptext = "\n".join([ll.strip() for ll in re.split("\r?\n", ptext) if ll])
    return ptext


def _remove_roman_numeral_headings(ptext: str) -> str:
    """
    Remove lines that only have a Roman numeral
    """
    ols = []
    ll = [ll.strip() for ll in re.split("\r?\n", ptext) if ll]
    for line in ll:
        try:
            roman.fromRoman(line)
        except roman.InvalidRomanNumeralError:
            ols.append(line)
    return "\n".join(ols)