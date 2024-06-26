from src.Operators.OperatorBase import Operator
from typing import List, Optional, Tuple
from abc import ABC


class Combiner(Operator, ABC):
    def __init__(self, k: int = 10) -> None:
        super().__init__(k)

        self._inputs: Optional[List[Operator]] = None
        

    def set_inputs(self, inputs: List[Operator]) -> None:
        if inputs is None or len(inputs) == 0:
            raise ValueError("Combiner must have at least one input.")
        if any(not isinstance(input_, Operator) for input_ in inputs):
            raise TypeError("All inputs must be Operators.")
        
        self._inputs: List[Operator] = inputs


    def cost(self) -> int:
        return sum(input_.cost() for input_ in self._inputs)
    
    def ml_cost(self, db) -> float:
        return sum(input_.ml_cost(db) for input_ in self._inputs)
