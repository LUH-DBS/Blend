from src.Operators.OperatorBase import Operator


class Difference(Operator):
    def __init__(self, k=10):
        Operator.__init__(self)
        self.type = 'set_difference'
        self.input = []  # list of two, [A, B]. output A-B
        self.k = k
