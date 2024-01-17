from src.Operators.OperatorBase import Operator
from typing import List, Optional
from abc import ABC


class Combiner(Operator, ABC):
    def __init__(self, k: int) -> None:
        super().__init__(k)
        self.inputs: Optional[List[Operator]] = None
    
    def set_inputs(self, inputs: List[Operator]) -> None:
        if inputs is None or len(inputs) == 0:
            raise ValueError("Combiner must have at least one input.")
        self.inputs = inputs.copy()

    def cost(self) -> int:
        return sum(input_.cost() for input_ in self.inputs)
    
    def ml_cost(self, db) -> float:
        return sum(input_.ml_cost(db) for input_ in self.inputs)
