import edcosts
import editor
import gzip
from importlib import reload

import normconfig as nc
import sys


if __name__ == "__main__":
    for modu in edcosts, editor, nc:
        reload(modu)

    # example to test with
    oov = sys.argv[1]

    # load edit costs
    lev_score_mat = editor.EdScoreMatrix(edcosts)
    lev_score_mat.read_cost_matrix()
    lev_score_mat.find_matrix_stats()
    # nested dictionary with costs hashed by char1 and then char2
    lev_score_mat_hash = lev_score_mat.create_matrix_hash()

    # load vocabulary (IV tokens)
    #   only load if not already loaded (takes some seconds)
    if "ivs" not in dir(sys.modules["__main__"]):
        with gzip.open(nc.IVDICO, "rt", encoding="utf8") as f:
            ivs = set(line.strip() for line in f if line.strip())
    
    # create EdManager    
    edimgr = editor.EdManager(lev_score_mat_hash, ivs)
    edimgr.prep_alphabet()
    
    # get candidates    
    cands = edimgr.generate_levdist_candidates(oov)
    #cands_and_dists = 
    
    
