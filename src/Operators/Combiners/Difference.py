from src.Operators.Combiners.CombinerBase import Combiner

# Typing imports
from src.Operators.OperatorBase import Operator
from src.DBHandler import DBHandler
from typing import List


class Difference(Combiner):
    def __init__(self, k: int = 10):
        super().__init__(k)

    def cost(self) -> int:
        return self.inputs[1].cost()
    
    def ml_cost(self, db: DBHandler) -> float:
        return self.inputs[1].ml_cost(db)
    
    def create_sql_query(self, db: DBHandler, additionals: str = "") -> str:
        minus_results = self.inputs[1].run(db, additionals=additionals)
        additionals += f" AND TableId NOT IN ({db.create_sql_list_numeric(minus_results)}) " if minus_results else ""
        self.inputs[0].k = self.k
        sql = self.inputs[0].create_sql_query(db, additionals=additionals)

        return sql
    
    def set_inputs(self, inputs: List[Operator]) -> None:
        if len(inputs) != 2:
            raise ValueError(f'Difference combiner must have exactly two inputs.')
        return super().set_inputs(inputs)
