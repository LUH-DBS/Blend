from src.Operators.OperatorBase import Operator


class Intersection(Operator):
    def __init__(self, k=10):
        Operator.__init__(self)
        self.type = 'set_intersection'
        self.input = []
        self.k = k
