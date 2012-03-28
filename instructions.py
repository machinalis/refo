class Instruction(object):
    """
    Non-opaque class to represent RE VM instructions.
    """
    def __init__(self):
        self.next = None
        self.split = None
        self.comparison_function = None
        self.record = None


class Atom(Instruction):
    def __init__(self, comparison_function, next=None):
        self.comparison_function = comparison_function
        if next != None:
            self.next = next

    def __repr__(self):
        return "Atom({0})".format(repr(self.comparison_function))


class Match(Instruction):
    def __repr__(self):
        return "Match"


class Split(Instruction):
    def __init__(self, s1=None, s2=None):
        if s1 != None:
            self.next = s1
        if s2 != None:
            self.split = s2

    def __repr__(self):
        return "Split({0}, {1})".format(repr(self.next), repr(self.split))


class Save(Instruction):
    def __init__(self, record, next=None):
        self.record = record
        if next != None:
            self.next = next

    def __repr__(self):
        return "Save({0})".format(repr(self.record))
