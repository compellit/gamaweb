from collections import OrderedDict
import logging
import re
import sys

from normalization import normconfig as tc


ed_logger = logging.getLogger("main.editor")


class EdManager:
    """Computes correction-candidates for a term, and edit-distances between
       the term and the candidate. Requires info about correction weights (arg cws)
       and an IV dictionary (ivdico)"""

    def __init__(self, editcosts, ivdico):
        self.editcosts = editcosts
        self.ivdico = ivdico

    alphabet = None
    accents_dico = {"a": "á", "e": "é", "i": "í", "n": "ñ", "o": "ó", "u": "ú"}

    def prep_alphabet(self, alphabet=tc.alphabet):
        """ Get alphabet for edit distance ready"""
        alphabet_all = list(alphabet[0])
        #alphabet_all.extend([a.decode("utf-8") for a in alphabet[1]]) # py2
        alphabet_all.extend(alphabet[1])
        self.alphabet = alphabet_all

    def accent_check(self, cand_form, oov_form):
        # This seems to be for comío (OOV) to comido
        # Not needed for Galician
        if not tc.accent_check_in_regexes:
            return False
        iniform = cand_form
        for key in self.accents_dico:
            if re.search(r"id[oa]$", cand_form):
                accented_cand = re.sub(key, self.accents_dico[key], oov_form)
                if accented_cand != iniform and accented_cand in self.ivdico:
                    return accented_cand
                    break
        return False

    def generate_regex_candidates(self, oov):
        """Regex-based candidates. If OOV matches certain contexts, a given regex
        will most likely correct it.
           <oov> refers to the .form property, not the the instance of OOV itself
           Return tuple with
               [1] hash, keys: candidates, values: distances
               [2] hash, keys: candidates, values: times cand has been matched by a regex
        """
        #TODO most of this seems not useful for Galician case (not Twitter)
        oov_before_rgdist = oov
        if False and len(oov) > 3 and oov.isupper():
            oov = oov.lower()
            ed_logger.debug("Lowercasing for regex candidates [{0}] to [{1}]".format(oov_before_rgdist, oov))

        # Ordered regexes. Format: (incorrect, correct)
        subs_tups = [('ceon$', 'ción'), ('ion$', 'ión')]
        subs = OrderedDict({ke: va for (ke, va) in subs_tups})

        apptimes = {}
        result = {}
        cand = oov
        for reg, rep in sorted(subs.items()):
            cand_bef = cand
            patt = re.compile(reg, re.IGNORECASE | re.UNICODE)
            # recursive            
            cand = re.sub(patt, subs[reg], cand)
            if not cand == cand_bef:
                apptimes.setdefault(cand, 0)
                # record how many times a rule has applied for cand
                apptimes[cand] += 1
                try:
                    apptimes[cand] += apptimes[cand_bef]
                except KeyError:
                    pass
                result.setdefault(cand, 0)
                result[cand] = -0.1 * apptimes[cand]
        result_valid = {}
        for cand in result.keys():
            # seems useless for Galician
            # if tc.accent_check_in_regexes:
            #     acc_cand = self.accent_check(cand, oov)
            #     if acc_cand:
            #         bkp_times = result[cand]
            #         del result[cand]
            #         print("ED (Rg) Deleted [{0}] from regex cands, Reason, Acc Cand [{1}]".format(
            #             repr(cand), repr(acc_cand)))
            #         result[acc_cand] = bkp_times
            #         result[acc_cand] += -0.25
            # relaxing constraint to be IV because the rule works metrically
            # any ion$ gotta be stressed, be it IV or still OOV
            #if cand not in self.ivdico and cand in result:
            #    continue
            if cand == oov and cand in result:
                continue
            else:
                result_valid[cand] = result[cand]
        #print("RED RES {0}, APPT {1}".format(repr(result), repr(apptimes)))
        return {"cands": result_valid, "apptimes": apptimes}


    def edits1(self, word):
        """Generate candidates at Lev distance 1. From Norvig speller."""
        orig_word = word
        if len(word) > 3 and word.isupper():
            word = word.lower()
            ed_logger.debug("Lowercasing for dist cands [{0}] to [{1}]".format(orig_word, word))
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes = [a + b[1:] for a, b in splits if b]
        replaces = [a + c + b[1:] for a, b in splits for c in self.alphabet if b]
        inserts = [a + c + b for a, b in splits for c in self.alphabet]
        edits1 = set(deletes + replaces + inserts)
        # print("++ All generated Edits1: %s" % repr(generated_edits1)) #large
        return edits1

    def generate_levdist_candidates(self, word):
        """Generate candidates at Lev distance 2 based on distance 1 edits,
           and return only those in known-words dictionary. Based on Norvig."""
        known2 = set([e2 for e1 in self.edits1(word) for e2 in self.edits1(e1)
                      if e2 in self.ivdico])
        cands = self.known(self.edits1(word)).union(known2)
        return cands

    def known(self, words):
        """Filter a list of words, returning only those in known-words dico.
           From Norvig."""
        return set(w for w in words if w in self.ivdico)

    def find_cost(self, a, b):
        """<b> OOV, <a> Cand. Return single-character-edit cost for changing
           'b' (from oov under study) into 'a' (from edit-candidate under study)
           The cost-matrix is organized as mat[corr][incorr]
           Assumes that "a" and "b" are utf8-decoded"""
        if a == b:
            cost = 0
        else:
            try:
                cost = self.editcosts[a.lower()][b.lower()]
            except KeyError as msg:
                # if a != "zero" and b != "zero":
                #    print "KeyError, a: %s, b: %s || Bad Key: %s" % (a, b, msg) #debug
                cost = -1
        # TODO: case-sensitivity how?
        # if a.lower() == b or b.lower() and not a== b:
        #    cost += -0.5

        # print "looking for costs between", repr(a), repr(b) #debug
        return 0 - cost  # matrix has neg numbers, min() below won't work if not do "0 -" here

    def levdist(self, s1, s2):
        """Create edit candidates and give Lev distance between them and arg oov.
           Lev dista computed with weights, given in constructor for class
           s1 is the candidate under consideration, s2 is the oov under study"""
        d = {}
        lenstr1 = len(s1)
        lenstr2 = len(s2)
        for i in range(-1, lenstr1 + 1):
            d[(i, -1)] = i + 1
        for j in range(-1, lenstr2 + 1):
            d[(-1, j)] = j + 1
        for i in range(lenstr1):
            for j in range(lenstr2):
                d[(i, j)] = min(
                    d[(i - 1, j)] + self.find_cost(s1[i], "zero"),  # deletion
                    d[(i, j - 1)] + self.find_cost("zero", s2[j]),  # insertion
                    d[(i - 1, j - 1)] + self.find_cost(s1[i], s2[j])  # substitution
                )
                # TODO: make positive if work with positive values 
        return 0 - d[lenstr1 - 1, lenstr2 - 1]

    def set_ivdico(self, ivdico):
        """# TODO: Not coherent cos using ivdico for initiation"""
        self.ivdico = ivdico


class EdScoreMatrix:
    """Methods to read cost matrix from module in arg cost_module
       and to find costs for individual character-edits."""

    def __init__(self, cost_module):
        self.costm = cost_module

    # `accented_chars` is used to penalize corrections that delete an accent
    #   can't include ñ and ç unlike for Spanish tweets, cos
    #   we need some diacritic deletion costs to be low (ç=>z, ñ=>n)
    #accented_chars = ['á', 'é', 'í', 'ñ', 'ó', 'ú', 'ç'] # old, Spanish tweets
    accented_chars = ['á', 'é', 'í', 'ó', 'ú']
    matrix_stats = {"max": None, "min": None, "ave": None}

    def read_cost_matrix(self):
        """Read cost matrix into a hash. Set instance values for them"""
        row_names = self.costm.row_names.strip().split("\t")
        col_names = self.costm.col_names.strip().split("\t")
        costs = self.costm.costs

        # matrix_cont is list of lists
        #   cost_lines[x] is row nbr, cost_lines[y] is col nbr
        matrix_conts = [line.split("\t") for line in costs.split("\n")]

        # check row and col lengths
        lens = set([len(line) for line in matrix_conts])
        if len(list(lens)) > 1:
            ed_logger.error("!! Cost lines have unequal length")
            sys.exit(2)

        if list(lens)[0] != len(col_names):
            ed_logger.error("!! Amount of column names does not match amount of columns")
            sys.exit(2)

        if list(lens)[0] != len(matrix_conts):
            ed_logger.error("!! Amount of row names does not match amount of rows")

        # set values
        #TODO why was this not set when declaring the variables?
        self.row_names = row_names
        self.col_names = col_names
        self.matrix_conts = matrix_conts

    def find_matrix_stats(self):
        """Calculate and set max, min, ave for cost-matrix values"""
        all_costs = []
        for line in self.matrix_conts:
            for cost in line:
                all_costs.append(float(cost))
        min_cost = min(all_costs)
        # TODO: may need to change cost < 0 if make costs positive
        max_cost = max([cost for cost in all_costs if cost < 0])
        ave_cost = float(sum(all_costs)) / len(all_costs)
        # set vals
        self.matrix_stats["min"] = min_cost
        self.matrix_stats["max"] = max_cost
        self.matrix_stats["ave"] = ave_cost

    def create_matrix_hash(self):
        """Hash cost-matrix contents. ic stands for incorrect character, cc stands for
           correct character"""
        skip_chars = ["SP"]
        names_map = {"YCorrNULL": "zero", "XErrNULL": "zero"}
        cost_dico = {}
        colno = 0
        for cc in self.col_names:
            #ccd = cc.decode("utf8") #py2
            ccd = cc
            rowno = 0
            if cc in skip_chars:
                colno += 1
                continue
            if cc in names_map:
                cc = names_map[cc]
            cost_dico[ccd] = {}
            for ic in self.row_names:
                if ic in skip_chars:
                    rowno += 1
                    continue
                if ic in names_map:
                    ic = names_map[ic]
                #icd = ic.decode("utf8") #py2
                icd = ic
                if float(self.matrix_conts[rowno][colno]) == 0 and cc != ic:
                    # TODO: what's this case for?
                    cost_dico[ccd][icd] = self.matrix_stats["ave"]
                else:
                    cost_dico[ccd][icd] = float(self.matrix_conts[rowno][colno])
                # extra-penalize corrections that delete an accent
                #     i.e. that consider the accented character to be incorrect
                if icd in self.accented_chars:
                    cost_dico[ccd][icd] += tc.acc_ins_penalty
                rowno += 1
            colno += 1
        return cost_dico
