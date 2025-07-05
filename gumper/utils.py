from collections import OrderedDict
import re
# imports work this way when importing :func:`gumper_client_web.main` from :mod:`gama.views`
from gumper import config as cf


def cleanup_text(text, replacements=None):
    """
    Cleans up the text by removing unwanted characters and formatting
    and applying some replacements for single words and expresions.
    """
    if replacements is not None:
        for key, value in replacements.items():
            text = re.sub(key, value, text)
    text = text.replace("'", "")
    text = text.replace("’", "")
    text = text.replace("‘", "")
    text = text.strip()
    return text


def load_w_replacements(config):
    """
    Loads replacements for a file, they affect a single word.
    """
    replacements = OrderedDict()
    with open(config.word_bound_replacements, "r", encoding="utf-8") as f:
        for line in f:
            key, value = line.strip().split("\t")
            replacements[re.compile(fr"\b{key}\b", re.I)] = value
    return replacements


def load_t_replacements(config):
    """
    Loads the replacements from a file. The replacements may affect multiple words.
    """
    replacements = OrderedDict()
    with open(config.text_level_replacements, "r", encoding="utf-8") as f:
        for line in f:
            key, value = line.strip().split("\t")
            replacements[re.compile(fr"{key}", re.I)] = value
    return replacements


def write_output_file(poem_lines, outinfo, poem_id):
    """
    Writes the output to a file.
    """
    # outinfo is Jumper output format (list of lists)
    out_lines = []
    for outer_idx, info_list in enumerate(outinfo):
        for idx, info in enumerate(info_list):
            postpro_text = info[1]
            keeps = [poem_lines[outer_idx][idx], postpro_text,  # orig lines + my own postpro
                     info[2],                                   # nbSyll, met, met no antirhythmic
                     " ".join([str(x) for x in info[3]]),
                     " ".join([str(x) for x in info[4]]),
                     f"{100*info[-1]:.2f}",                     # match ratio with pattern
                     info[-2]]                                  # meter name
            out_lines.append(keeps)
    ouname = cf.oufi.stem + f"_{str.zfill(poem_id, 3)}" + cf.oufi.suffix
    with open(cf.oufi.with_name(ouname), "w", encoding="utf-8") as oufh:
        for line in out_lines:
            oufh.write("\t".join([str(x) for x in line]) + "\n")
    
def read_gold_stress_patterns(gold_location):
    """
    Reads the gold stress patterns from a file.
    """
    gold = []
    with open(gold_location, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            if idx == 0 or line.startswith("#"):
                continue
            orig_text, nb_syll_gold, met_gold = line.strip().split("\t")
            gold.append((orig_text, nb_syll_gold, met_gold))
    return gold