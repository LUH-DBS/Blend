from src.Operators.OperatorBase import Operator
from typing import List, Optional, Tuple
from abc import ABC


class Combiner(Operator, ABC):
    def __init__(self, *inputs: Tuple[Operator], k: int = 10) -> None:
        super().__init__(k)
        if inputs is None or len(inputs) == 0:
            raise ValueError("Combiner must have at least one input.")
        if any(not isinstance(input_, Operator) for input_ in inputs):
            error_hint = ""
            if isinstance(inputs[-1], int):
                error_hint = "Please make sure that k is specified as a keyword argument."

            if isinstance(inputs[0], list):
                error_hint = "Please make sure that the inputs are passed as separate arguments."

            raise ValueError(f"Positional init arguments of Combiner must be of type Operator. {error_hint}")

        
        self.inputs: List[Operator] = list(inputs)

    def cost(self) -> int:
        return sum(input_.cost() for input_ in self.inputs)
    
    def ml_cost(self, db) -> float:
        return sum(input_.ml_cost(db) for input_ in self.inputs)
