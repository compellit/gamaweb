from pathlib import Path

# base dir = dossier où est ce fichier config.py
BASE_DIR = Path(__file__).resolve().parent

# data
#word_bound_replacements = Path("../gumper/data") / "replacements_w.txt"
#text_level_replacements = Path("../gumper/data") / "replacements_t.txt"

word_bound_replacements = BASE_DIR / "data" / "replacements_w.txt"
text_level_replacements = BASE_DIR / "data" / "replacements_t.txt"

# IO
oudir = Path("out")
oufi = oudir / "scansion.tsv"
logdir = Path("logs")
indir = Path("input")

for dname in [oudir, logdir]:
    if not Path(dname).exists():
        Path(dname).mkdir(parents=True)

