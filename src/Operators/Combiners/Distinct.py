from typing import List
from src.Operators.OperatorBase import Operator
from src.Operators.Combiners.CombinerBase import Combiner

# Typing imports
from src.DBHandler import DBHandler


class Distinct(Combiner):
    def __init__(self, k: int = 10):
        super().__init__(k)

    def create_sql_query(self, db: DBHandler, additionals: str = "") -> str:
        sql = """SELECT DISTINCT TableId FROM (
        """
        sql += self.inputs[0].create_sql_query(db, additionals=additionals)
        sql += f""") AS {db.random_subquery_name()} LIMIT {self.k}
        """

        return sql
    
    def set_inputs(self, inputs: List[Operator]) -> None:
        if len(inputs) != 1:
            raise ValueError(f'Distinct combiner must have exactly one input.')
        
        return super().set_inputs(inputs)
        
