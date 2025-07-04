from importlib import reload
from pathlib import Path

import config as cf
import grapheme2syllable as g2s


if __name__ == "__main__":
    reload(g2s)
    reload(cf)

    # Example usage
    text = "Hello, world!"
    syllables = g2s.silabeo(text)
    print(f"Syllables in '{text}': {syllables}")

    if True:# Example usage with a list of words
        # Example usage with a file
        input_file = Path("texts") / "examples-for-syll.txt"
        #output_file = Path("output.txt")

        with input_file.open("r", encoding="utf8") as f:
            for line in f:
                text = line.strip()
                # if text == "cambiou":
                #     breakpoint()
                syllables = g2s.silabeo(text)
                print(f"'{text}' -> {syllables}")

        # syllables = g2s.grapheme_to_syllable(text)
        #
        # with output_file.open("w") as f:
        #     f.write("\n".join(syllables))

