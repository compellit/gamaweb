import argparse
import pickle


def parse_args():
    parser = argparse.ArgumentParser(description="Pickle vocabulary from a word list.")
    parser.add_argument("in_file", type=str, help="Path to the word list file (UTF-8, one word per line).")
    parser.add_argument("out_file", type=str, help="Path to save the Pickle file (binary mode).")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    with open(args.in_file, "r", encoding="utf-8") as infi:
        word_list = set([line.strip() for line in infi if line.strip()])

    print(f"Loaded {len(word_list)} words")

    # Save to Pickle file (binary mode)
    with open(args.out_file, "wb") as oufi:
        # Protocol 4: good for cross-platform, large files
        pickle.dump(word_list, oufi, protocol=4)