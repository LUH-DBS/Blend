from src.Operators.OperatorBase import Operator

# Typing imports
from src.DBHandler import DBHandler

class Input(Operator):
    def __init__(self, _) -> None:
        super().__init__(0)

    def cost(self) -> int:
        return 0
    
    def create_sql_query(self, DB: DBHandler, additionals: str="") -> str:
        raise NotImplementedError("Input operator cannot be used in SQL query.")
