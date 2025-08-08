import argparse
from importlib import reload
from pathlib import Path

import gumper

# imports work this way when importing :func:`main` from :mod:`gama.views`
from gumper.gumper import escandir_texto
from gumper import config as cf
from gumper import utils as ut


DBG = False


def parse_args():
    parser = argparse.ArgumentParser(description="Gumper client for analyzing poems.")
    parser.add_argument(
        "infile",
        type=str,
        help="ID for the directory with the input to analyze.",
    )
    parser.add_argument("--hide_post", action="store_true")
    return parser.parse_args()


def _identify_extrarhythmic_positions(scan1: list[int|str], scan2: list[int|str]) -> list[str]:
    """
    Compare scan1 (with extrarhythmic positions) and scan2 (without).
    The scans will be integers unless they are "-".
    Output the syllables that are in scan1 but not in scan2.
    """
    extra_sylls = []
    scan1 = [syll for syll in scan1 if syll != "-"]
    scan2 = [syll for syll in scan2 if syll != "-"]
    for syll in scan1:
        if syll not in scan2:
            extra_sylls.append(syll)
    return extra_sylls


def main(cf, origfile, infile):
    reps_w = ut.load_w_replacements(cf)
    reps_t = ut.load_t_replacements(cf)

    all_scansion_out = {"desktop": [], "mobile": []}
    results_data = []

    with open(origfile, encoding="utf8") as f:
        # lines are obtained instead of just reading the text for compatibility with old code below
        orig_lines = [line.strip() for line in f if line.strip() != ""]

    with open(infile, encoding="utf8") as f:
        # lines are obtained instead of just reading the text for compatibility with old code below
        poem_lines = [line.strip() for line in f]
        poem_text = "\n".join(poem_lines)
        poem_text = ut.cleanup_text(poem_text, reps_t)
        poem_text = ut.cleanup_text(poem_text, reps_w)
        esc = escandir_texto(poem_text)
        for idx, result in enumerate(esc):

            # get extrarhythmic syllables so that can be highlighted in the output
            ex_sylls = _identify_extrarhythmic_positions(result[3], result[4])
            #print(idx, ex_sylls)
            # Write output table lines
            postpro_txt = f"{result[1]}"
            # format for desktop output
            out_format = (f"<tr><td style='text-align:right'><span style='display:none'>{idx+1}</span>{idx+1}.</td>"
                  f"<td style='padding-left:1em'>{orig_lines[idx]}</td>" 
                  f"<td class='col-preprocessing'>{postpro_txt}"
                  f"</td><td style='padding-left:3em;text-align:right'>{result[2]}"
                  f"</td><td style='padding-left:3em;text-align:right'>\t{' '.join([str(x) for x in result[3]])}"
                  f"</td><td style='padding-left:3em;text-align:right'>\t{' '.join([str(x) for x in result[4]])}</td></tr>\n")
            # Format for mobile output. Note that DataTables has no col/rowspan (outside the header https://datatables.net/manual/tech-notes/18)
            # and won't sort if number has a prefix/suffix like 1.
            # Preprocessed text is repeated in second row for each line (but hidden) so that search finds both rows.
            # Syllable count and stressed positions are on same cell, but each aligns to one side c/o display: flex
            # and justify-content: space-between
            out_format_mobile = (f"<tr><td style='text-align:right;border:0'><span style='display:none'>{idx+1}</span>{idx+1}.</td>"
                  f"<td>{orig_lines[idx]}<br/>" 
                  f"<span class='inline-prepro' style='color:darkgray;display:none'>{postpro_txt}</span></td></tr>\n"
                  f"<tr><td><span style='display:none'>{idx+1.5}</span></td><td style='display: flex; justify-content: space-between; width: 100%;'><span style='text-align:left;padding-left:1.5em;'>{result[2]}<span style='display:none'>{postpro_txt}</span></span>"
                  f"<span style='text-align:right;padding-right:2em;'>\t{' '.join([str(x) if x not in ex_sylls else f'<span style="color:darkgray">({x})</span>' for x in result[3]])}</td></tr>\n") 

            DBG and print(out_format)
            all_scansion_out["desktop"].append(out_format)
            all_scansion_out["mobile"].append(out_format_mobile)
            # `results_data` is used for exporting results
            results_data.append({
                "line": idx + 1,
                "original_text": orig_lines[idx],
                "preprocessing": result[1],
                "metrical_syllables": result[2],
                "stressed_syllables": " ".join(map(str, result[3])),
                "no_extra_rhythmic": " ".join(map(str, result[4]))
            })
    return all_scansion_out, results_data

if __name__ == "__main__":
    for mod in [gumper, ut, cf]:
        reload(mod)
    args = parse_args()
    infile = Path(args.infile)
    print("infile", infile)
    #out_str = main(infile)

