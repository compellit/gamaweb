"""
Collect tokens with apostrophes from a file.
"""

from collections import Counter
import re
from pathlib import Path
import sys


def collect_tokens_with_apostrophes(input_file: Path, output_file: Path):
    """
    Collect tokens with apostrophes from the input file and write them to the output file.

    Args:
        input_file (Path): Path to the input file containing text.
        output_file (Path): Path to the output file where results will be saved.
    """
    apostrophe_re = re.compile(r"\b\w*['‘’]\w*\b|\b\w*['‘’]\W", re.UNICODE)

    with input_file.open("r", encoding="utf8") as infile,\
            output_file.open("w", encoding="utf8") as outfile:
        outfile.write(f"token\tfreq\n")
        all_counts = Counter()
        for line in infile:
            tokens = apostrophe_re.findall(line)
            if tokens:
                # Remove duplicates and sort tokens by descending frequency
                token_counts = Counter(tokens)
                all_counts.update(token_counts)
        sorted_tokens = sorted(all_counts.items(), key=lambda x: x[1], reverse=True)
        tokens = [f"{token}\t{count}" for token, count in sorted_tokens]
        outfile.write("\n".join(tokens) + "\n")


if __name__ == "__main__":
    input_path = Path(sys.argv[1])
    output_path = Path("wk") / (input_path.stem + "_apos" + input_path.suffix)

    collect_tokens_with_apostrophes(input_path, output_path)
    print(f"Tokens with apostrophes collected in {output_path}")