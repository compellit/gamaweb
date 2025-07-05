import argparse
from importlib import reload
from pathlib import Path

import gumper

# imports work this way when importing :func:`main` from :mod:`gama.views`
from gumper.gumper import escandir_texto
from gumper import config as cf
from gumper import utils as ut


def parse_args():
    parser = argparse.ArgumentParser(description="Gumper client for analyzing poems.")
    parser.add_argument(
        "infile",
        type=str,
        help="ID for the directory with the input to analyze.",
    )
    parser.add_argument("--hide_post", action="store_true")
    return parser.parse_args()

def main(cf, origfile, infile):
    reps_w = ut.load_w_replacements(cf)
    reps_t = ut.load_t_replacements(cf)

    all_scansion_out = []

    with open(origfile, encoding="utf8") as f:
        # lines are obtained instead of just reading the text for compatibility with old code below
        orig_lines = [line.strip() for line in f]

    with open(infile, encoding="utf8") as f:
        # lines are obtained instead of just reading the text for compatibility with old code below
        poem_lines = [line.strip() for line in f]
        poem_text = "\n".join(poem_lines)
        poem_text = ut.cleanup_text(poem_text, reps_t)
        poem_text = ut.cleanup_text(poem_text, reps_w)
        esc = escandir_texto(poem_text)
        for idx, result in enumerate(esc):
            #TODO give possibility to hid postprocessed text via the web form,
            #this was done as below with CLI arguments
            #postpro_txt = "" if args.hide_post else f"{result[1]:<50}"
            # Write output table lines
            postpro_txt = f"{result[1]:<50}"
            out_format = (f"<tr><td>{orig_lines[idx]:<50}</td><td>{postpro_txt}" +\
                  f"</td><td style='padding-left:3em;text-align:right'>{result[2]:>3}") +\
                  f"</td><td style='padding-left:3em;text-align:right'>\t{' '.join([str(x) for x in result[3]]):>16}" +\
                  f"</td><td style='padding-left:3em;text-align:right'>\t{' '.join([str(x) for x in result[4]]):>16}</td></tr>\n" 
            print(out_format)
            all_scansion_out.append(out_format)
    #ut.write_output_file(all_poem_lines_out, all_scansion_out, f"001")
    return all_scansion_out

if __name__ == "__main__":
    for mod in [gumper, ut, cf]:
        reload(mod)
    args = parse_args()
    infile = Path(args.infile)
    print("infile", infile)
    out_str = main(infile)

