"""Utilities for syllabifiction scripts."""

from collections import OrderedDict
import logging
import re
import types
import unicodedata


utils_logger = logging.getLogger("main.utils")


import grapheme2syllable as g2s


def load_text_replacements(config: types.ModuleType) -> OrderedDict[re.Pattern, str]:
    """
    Loads contexts and replacements from a file whose path is given at :obj:`config`.
    The replacements may affect multiple words.
    """
    replacements: OrderedDict[re.Pattern, str] = OrderedDict()
    with open(config.text_level_replacements, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"):
                continue
            line = re.sub(" #.+", "", line)  # Remove comments
            # replacements may finish with a space, we strip all left, but right only newline
            if line.count("\t") == 2:
                key, value, case_info = line.lstrip().rstrip("\n\r").split("\t")
            else:
                assert line.count("\t") == 1, "Line should contain one or two tab-delimited columns."
                case_info = None
                key, value = line.lstrip().rstrip("\n\r").split("\t")
            if case_info == "cs":
                replacements[re.compile(fr"{key}", re.U)] = value
            else:
                replacements[re.compile(fr"{key}", re.I | re.U)] = value
    return replacements



def load_syllable_replacements(config: types.ModuleType) -> OrderedDict[re.Pattern, tuple[str, str]]:
    """
    Loads replacements for a syllable sequence expressed as a string from a file,
    whose path is given at :obj:`config`.

    Args:
        config: Configuration object containing the path to the syllable replacements file.

    Returns:
        OrderedDict: A dictionary with compiled regex patterns as keys and, as values,
                     a tuple with their replacements and a postprocessing instruction.
    """
    replacements: OrderedDict[re.Pattern, tuple[str, str]] = OrderedDict()
    with open(config.syllable_replacements, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"):
                continue
            line = re.sub(" #.+", "", line)  # Remove comments
            # replacements may finish with a space, we strip all left, but right only newline
            # postpro refers to information to modify postprocessing, see the data file
            # at cf.syllable_replacements
            key, value, postpro = line.lstrip().rstrip("\n\r").split("\t")
            replacements[re.compile(fr"{key}", re.I|re.U)] = (value, postpro)
    return replacements


def load_words_with_hyphen_to_keep(config: types.ModuleType) -> set[re.Pattern]:
    """
    Loads words with hyphen to keep from a file, whose path is given at :obj:`config`.

    Args:
        config: Configuration object containing the path to the file with words to keep.

    Returns:
        set: A set of regular expression patterns words that should be kept with hyphens.
    """
    words_to_keep: set[re.Pattern] = set()
    with open(config.words_with_hyphen_to_keep, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"):
                continue
            line = re.sub(" #.+", "", line)  # Remove comments
            words_to_keep.add(re.compile(line.rstrip().lstrip("\n\r"), re.I | re.U))
    return words_to_keep


def destress_word(word: str, case_mask: list=None) -> str:
    """
    Remove stress marks from a word.

    Args:
        word (str): The word to destress.
        case_mask (list): A list with the same length as the word, with 1 if the character
            at that position should be uppercased, and 0 if it should be lowercased.

    Returns:
        str: The destressed word.
    """
    #TODO shouldn't the stress mark be dynamic c/o cli args?
    word = re.sub(r"[´]", "", word)  # Remove stress marks    
    normalized_word = unicodedata.normalize('NFD', word)
    unaccented_chars = [char for char in normalized_word if unicodedata.combining(char) == 0]
    if case_mask is not None:
        assert len(word) == len(case_mask), "Word and case mask must have the same length."
        final_word = []
        for cidx, cm in enumerate(case_mask):
            final_word.append(unaccented_chars[cidx].lower()) if cm == 0 else \
                final_word.append(unaccented_chars[cidx])
        return "".join(final_word)
    else:
        return "".join(unaccented_chars)


def destress_word_simple(word: str, case_mask: list=None) -> str:
    """
    Remove stress marks from a word, without case masking.
    Note: This is used with syllabified output, where the stress mark has been
    prefixed to the syllable (when applicable), that's why simply removing the stress mark
    is fine rather than removing the diacritic but keeping the vowel.

    Args:
        word (str): The word to destress.

    Returns:
        str: The destressed word.
    """
    #TODO shouldn't the stress mark be dynamic c/o cli args?
    word = re.sub(r"[´]", "", word)  # Remove stress marks
    if case_mask is not None:
        assert len(word) == len(case_mask), "Word and case mask must have the same length."
    final_word = word
    if case_mask is not None:
        final_word = []
        for cidx, cm in enumerate(case_mask):
            final_word.append(word[cidx].lower()) if cm == 0 else final_word.append(word[cidx])
        final_word = "".join(final_word)
    return final_word


def _spanishfy(tok: str, syl_list:list) -> str:
    """
    Apply Spanish orthographic stress rules to a token. Only applying
    it to the last syllable of polysyllabic words, otherwise gave too many errors.
    """
    reps = {"a": "á", "e": "é", "o": "ó"}
    newtok = None
    for diph in g2s.UNACCENTED_DIPHTHONGS_GL:
        if re.search(rf"{diph}s?$", tok.lower()):
            if not re.search(r"[áéíóú]", tok.lower()):
                newdiph = diph
                for key, value in reps.items():
                    newdiph = re.sub(key, value, newdiph)
                newtok = tok.replace(diph, newdiph)
    if newtok is not None and newtok != tok:
        utils_logger.debug(f"Spanishfied: [{tok}] to [{newtok}] context [{''.join(syl_list)}]")
        return newtok
    return tok


def detokenize(tokens):
    opening_punct = {'¡', '¿', '(', '[', '{', '«', '„'}
    closing_punct = {'!', '?', '.', ')', ']', '}', '»', '...'}

    result = []
    for token in tokens:
        if token in opening_punct:
            # attach to next word, so store as pending prefix
            result.append(token)
        elif token in closing_punct or token in {',', ';', ':'}:
            # attach to previous word (no space before)
            if result:
                result[-1] += token
            else:
                result.append(token)
        else:
            # check if last token was an opening punctuation mark
            if result and result[-1] in opening_punct:
                # merge with previous (opening punct)
                result[-1] = result[-1] + token
            else:
                result.append(token)
    return ' '.join(result)