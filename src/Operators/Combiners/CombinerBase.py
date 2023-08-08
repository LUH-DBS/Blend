from src.Operators.OperatorBase import Operator
from typing import List, Optional

class Combiner(Operator):
    def __init__(self, k: int) -> None:
        super().__init__(k)
        self.inputs: Optional[List[Operator]] = None
    
    def set_inputs(self, inputs: List[Operator]) -> None:
        if inputs is None or len(inputs) == 0:
            raise ValueError("Combiner must have at least one input.")
        self.inputs = inputs.copy()

    def cost(self) -> int:
        return sum(input.cost() for input in self.inputs)
    

