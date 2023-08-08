from src.DBHandler import DBHandler
from src.Operators import Operator, Seeker, Combiner, Input, Terminal
from typing import List, Iterable

class Plan(object):
    def __init__(self) -> None:
        self.DB = DBHandler()
        self.operators = dict()
        self.combiners: List[Combiner] = []
        self.terminal: Terminal = None

    def add(self, name: str, operator: Operator, inputs: Iterable[str] = []) -> None:
        """Add an operator to the plan."""
        
        inputs = list(inputs)

        # Check if operator is valid
        if not isinstance(operator, Operator):
            raise TypeError(f'Expected Operator, got {type(operator)}')
        
        self.operators[name] = operator

        if isinstance(operator, Combiner):
            combiner : Combiner = operator
            try:
                input_operators = [self.operators[input_name] for input_name in inputs]
            except KeyError as e:
                raise KeyError(f'Operator {name} has an invalid input: {e}. Please add the input operator before adding the combiner.')
            
            combiner.set_inputs(input_operators)
            self.combiners.append(combiner)
        
        elif isinstance(operator, Terminal):
            self.terminal = operator
            if len(inputs) != 1:
                raise ValueError(f'Terminal {name} must have exactly one input.')
            
            self.terminal.set_input(self.operators[inputs[0]])


    def run(self) -> List[int]:
        """Run the plan."""
        
        return self.terminal.run(self.DB)
