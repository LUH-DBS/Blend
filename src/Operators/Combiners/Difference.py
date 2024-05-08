from src.Operators.Combiners.CombinerBase import Combiner

# Typing imports
from src.Operators.OperatorBase import Operator
from src.DBHandler import DBHandler
from typing import List


class Difference(Combiner):
    def __init__(self, minuend: Operator, subtrahend: Operator, k: int = 10) -> None:
        super().__init__(minuend, subtrahend, k=k)

    def cost(self) -> int:
        return self.inputs[1].cost()
    
    def ml_cost(self, db: DBHandler) -> float:
        return self.inputs[1].ml_cost(db)
    
    def create_sql_query(self, db: DBHandler, additionals: str = "") -> str:
        minus_results = self.inputs[1].run(additionals)
        additionals += f" AND TableId NOT IN ({db.create_sql_list_numeric(minus_results)}) " if minus_results else ""
        self.inputs[0].k = self.k
        sql = self.inputs[0].create_sql_query(db, additionals=additionals)

        return sql
