from src.Operators.OperatorBase import Operator

# Typing imports
from src.DBHandler import DBHandler
from typing import Optional


class Terminal(Operator):
    def __init__(self, k: int = 10, input_: Optional[Operator] = None) -> None:
        super().__init__(k)
        self.input = input_

    def cost(self) -> int:
        return 0
    
    def set_input(self, input_: Operator) -> None:
        if input_ is None:
            raise ValueError(f'Terminal operator must have an input.')
        
        self.input = input_

    def create_sql_query(self, db: DBHandler, additionals: str = "") -> str:
        if self.input is None:
            raise ValueError(f'Terminal operator must have an input.')
        return self.input.create_sql_query(db, additionals=additionals)
    
