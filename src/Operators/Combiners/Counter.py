from src.Operators.OperatorBase import Operator


class Counter(Operator):
    def __init__(self, k=10):
        Operator.__init__(self)
        self.type = 'set_counter'
        self.input = []
        self.k = k
