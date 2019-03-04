from collections import defaultdict

class Pos:
    # Special POS are START and END which represent the start of a 
    # sentence and the end of a sentence
    def __init__(self, val=None, count=1,  word_count=0, arc_count=0):
        self.val = val
        self.count = count
        self.word_count = word_count
        self.words = defaultdict(int) # Hash of words counted at this POS
        self.arc_count = arc_count  # arc_count should be the same as words but we keep it for sanity
        self.arcs = defaultdict(int)  # Hash of where this POS state can arc to.
        self.two_arcs = defaultdict(int)
        self.arc_cap = defaultdict(int)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        ret_str = "State: {} {}\n".format(self.val, self.count)
        for k,v in self.arcs.items():
            ret_str += "Arc {}\t{}\n".format(k.val, v)
        for k,v in self.words.items():
            ret_str += "Emit {}\t{}\n".format(k.val, v)
        return ret_str

    def as_JSON(self):
        json_object = dict()

        clean_words = {k.val: v for k,v in self.words.items()}
        clean_arcs = {k.val: v for k,v in self.arcs.items()}
        # clean_tow_arcs = {k.val: v for k,v in self.two_arcs.items()}

        return {
            'words': clean_words,
            'count': self.count,
            'word_count': self.word_count,
            'arcs': clean_arcs,
            'two_arcs': self.two_arcs,
            'arc_count': self.arc_count,
            'arc_cap': self.arc_cap
        }


class Word:
    def __init__(self, val=""):
        self.val = val
        self.count = 1 if self.val else 0
        self.pos = dict()
        self.hasLowerEquiv = 0
        self.hasSingularEquiv = 0

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.val

    def as_JSON(self):
        return {
                'count': self.count, 
                'LowerEquiv' : self.hasLowerEquiv,
                'SingularEquiv': self.hasSingularEquiv
                }