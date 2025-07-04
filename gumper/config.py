from pathlib import Path

# data
word_bound_replacements = Path("data") / "replacements_w.txt"
text_level_replacements = Path("data") / "replacements_t.txt"

# IO
oudir = Path("out")
oufi = oudir / "scansion.tsv"
logdir = Path("logs")
indir = Path("input")
in_sheet = indir / "test_corpus.ods"
sheet_name = "sel_20250623"

for dname in [oudir, logdir]:
    if not Path(dname).exists():
        Path(dname).mkdir(parents=True)

