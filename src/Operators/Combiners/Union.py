from src.Operators.OperatorBase import Operator


class Union(Operator):
    def __init__(self, k=10):
        Operator.__init__(self)
        self.type = 'set_union'
        self.input = []
        self.k = k
