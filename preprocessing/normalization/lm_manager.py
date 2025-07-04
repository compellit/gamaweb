"""To work with n-gram language models"""

import kenlm

from normalization import normconfig as nc


class KenLMManager:
    def __init__(self, bin_path=nc.LMPATH, fragment_mode=True):
        """Initialize KenLMManager with the path to the binary language model."""
        self.bin_path = bin_path
        print("Loading KenLM model from:", bin_path)
        self.model = kenlm.LanguageModel(str(self.bin_path))
        self.fragment_mode = fragment_mode
        
    
    def find_context_for_token(self, tok, idx, toklist, window=nc.lm_window):
        """Find left-context for the given OOV term in the token list."""
        #idx = toklist.index(oov)
        # if idx < window < 0:
        #     leftcon = toklist[0:idx]
        # else:
        #     leftcon = toklist[idx-window:idx]
        assert toklist[idx] == tok, "Token at index does not match the provided token"
        leftcon = toklist[0:idx] if idx < window else toklist[idx-window:idx]
        rightcon = toklist[idx+1:idx+window+1] if idx + window + 1 <= len(toklist) else toklist[idx+1:]
        token_in_context = leftcon + [tok] + rightcon        
        return leftcon, rightcon


    def find_logprob_in_context(self, tok, context):
        """KenLM logprob with Python API"""
        fragment_to_score = context[0] + [tok] + context[1]
        scoring_args = {"bos": False, "eos": False} if self.fragment_mode else {}
        return self.model.score(" ".join(fragment_to_score), **scoring_args)  # No BOS/EOS for context scoring


    