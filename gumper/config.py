from pathlib import Path

# data
word_bound_replacements = Path("../gumper/data") / "replacements_w.txt"
text_level_replacements = Path("../gumper/data") / "replacements_t.txt"

# IO
oudir = Path("out")
oufi = oudir / "scansion.tsv"
logdir = Path("logs")
indir = Path("input")

for dname in [oudir, logdir]:
    if not Path(dname).exists():
        Path(dname).mkdir(parents=True)

