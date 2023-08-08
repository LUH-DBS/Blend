from src.Operators.OperatorBase import Operator

class Seeker(Operator):
    def __init__(self, k: int) -> None:
        super().__init__(k)

