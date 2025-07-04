"""Classes for normalization"""

from enum import Enum


class OOV:
    """Out-of-vocabulary (OOV) terms in normalization."""
    
    def __init__(self, form ):
        self.form = form
        self.cands = {}

    def __repr__(self):
        return f"OOV(form={self.form})"


class CandType(str, Enum):
    LEV = "lev"
    RGX = "rgx"


class Candidate:
    """Candidate for normalization."""
    
    def __init__(self, form, cand_type: CandType, levdist=None, rgxscore=None):
        self.form = form
        self.cand_type = cand_type
        self.levdist = levdist
        self.rgxscore = rgxscore
    
    def __repr__(self):
        return f"Candidate(form={self.form}, levdist={self.levdist}, rgxscore={self.rgxscore}, origin={self.cand_type})"
    
    def __lt__(self, other):
        return self.levdist < other.levdist \
            if self.levdist is not None and other.levdist is not None else False

