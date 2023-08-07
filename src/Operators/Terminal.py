from src.Operators.OperatorBase import Operator

class Terminal(Operator):
    def __init__(self):
        Operator.__init__(self)
        self.type = 'terminal'
