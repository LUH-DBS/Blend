from src.DBHandler import DBHandler
from src.Operators import Operator, Combiner, Seeker

# Typing imports
from typing import List, Iterable, Optional, Set


class Plan(object):
    def __init__(self) -> None:
        self.DB = DBHandler()
        self._operators = dict()
        self._terminal_candidates: Set[str] = set()

    def add(self, name: str, operator: Operator, inputs: Optional[Iterable[str]] = None) -> None:
        """Add an operator to the plan."""
        if inputs is None:
            inputs = []
        inputs = list(inputs)

        
        if name in self._operators:
            raise ValueError(f'Operator {name} already exists in the plan.')

        if not isinstance(operator, Operator):
            raise TypeError(f'Expected Operator, got {type(operator)}')        
        
        if isinstance(operator, Seeker):
            if len(inputs) != 0:
                raise ValueError(f'Seeker {name} cannot have inputs.')
        
        if isinstance(operator, Combiner):
            operator: Combiner = operator
            try:
                input_operators = [self._operators[input_name] for input_name in inputs]
            except KeyError as e:
                raise KeyError(
                    f'Operator {name} has an invalid input: {e}. '
                    f'Please add the input operator before adding the combiner.'
                )
            
            operator.set_inputs(input_operators)



        # Add the operator to the plan
        self._operators[name] = operator
        self._terminal_candidates.add(name)
        self._terminal_candidates -= set(inputs)

        
    

    def run(self) -> List[int]:
        """Run the plan."""
        if len(self._terminal_candidates) == 0:
            raise ValueError('No terminal candidates found.')
        
        if len(self._terminal_candidates) > 1:
            raise ValueError('Multiple terminal candidates found.')
        
        terminal = next(iter(self._terminal_candidates))

        return terminal.run()
