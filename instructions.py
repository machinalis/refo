class Instruction(object):
    """
    Non-opaque class to represent RE VM instructions.
    Instructions join among themselves to form code (a program).
    Instructions are joined like a linked list usign the `next` and `split`
    attributes, thus forming a directed graph.
    """


class Atom(Instruction):
    def __init__(self, comparison_function, next=None):
        self.comparison_function = comparison_function
        if next != None:
            self.next = next

    def __repr__(self):
        return "Atom({0})".format(repr(self.comparison_function))


class Accept(Instruction):
    next = None

    def __repr__(self):
        return "Accept"


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
