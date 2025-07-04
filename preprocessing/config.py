# Syllabification configuration file

from pathlib import Path

# Orthography processing

APOS = r"['‘’]"

#IO

data_dir = Path("data")
text_level_replacements = data_dir / "replacements_text.tsv"
syllable_replacements = data_dir / "syllabification_postprocessing.tsv"
words_with_hyphen_to_keep = data_dir / "hyphens_to_keep.txt" # unused

log_dir = "logs"
log_fn_template = "log_{batch_id}.txt"
if not Path(log_dir).exists():
    Path(log_dir).mkdir(parents=True)

batch_cumulog = "batch_log.txt"

# pos-tagging

pos_model_path = data_dir / "galician-treegal-ud-2.5-191206.udpipe"