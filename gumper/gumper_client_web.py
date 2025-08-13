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

def main(cf, origfile, infile):
    reps_w = ut.load_w_replacements(cf)
    reps_t = ut.load_t_replacements(cf)

    all_scansion_out = []
    # Pour construire le fichier results.tsv pour l'export
    # (Sinon les résultats de l'analyse sont sous forme html, compliquée à reformater dans un tsv)
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
            #TODO give possibility to hid postprocessed text via the web form,
            #this was done as below with CLI arguments
            #postpro_txt = "" if args.hide_post else f"{result[1]:<50}"
            # Write output table lines
            postpro_txt = f"{result[1]:<50}"
            out_format = (f"<tr><td style='text-align:right'>{idx+1}.</td>"
                  f"<td style='padding-left:1em'>{orig_lines[idx]:<50}</td>" 
                  f"<td class='col-preprocessing'>{postpro_txt}"    #Ajout class pour fonction Afficher/Cacher colonne
                  f"</td><td style='padding-left:3em;text-align:right'>{result[2]:>3}"
                  f"</td><td style='padding-left:3em;text-align:right'>\t{' '.join([str(x) for x in result[3]]):>16}"
                  f"</td><td style='padding-left:3em;text-align:right'>\t{' '.join([str(x) for x in result[4]]):>16}</td></tr>\n") 
            DBG and print(out_format)
            all_scansion_out.append(out_format)
    #ut.write_output_file(all_poem_lines_out, all_scansion_out, f"001")

            # Stockage données d'analyse pour tsv
            results_data.append({
                "line": idx + 1,
                "original_text": orig_lines[idx],
                "preprocessing": result[1],
                "metrical_syllables": result[2],
                "stressed_syllables": " ".join(map(str, result[3])),
                "no_extra_rhythmic": " ".join(map(str, result[4]))
            })
    # Retourner all_scansion_out (page html) et results_data (export)
    return all_scansion_out, results_data

if __name__ == "__main__":
    for mod in [gumper, ut, cf]:
        reload(mod)
    args = parse_args()
    infile = Path(args.infile)
    print("infile", infile)
    out_str = main(infile)

