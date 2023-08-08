from src.Operators.OperatorBase import Operator
from abc import ABC


class Seeker(Operator, ABC):
    def __init__(self, k: int) -> None:
        super().__init__(k)
