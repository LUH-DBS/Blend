from src.Operators.Combiners.CombinerBase import Combiner

# Typing imports
from src.Operators.OperatorBase import Operator
from src.DBHandler import DBHandler
from typing import List

class Difference(Combiner):
    def __init__(self, k: int=10):
        super().__init__(k)
    
    def create_sql_query(self, DB: DBHandler, additionals: str="") -> str:
        minus_results = self.inputs[1].run(DB, additionals=additionals)
        additionals += f" AND TableId NOT IN ({DB.create_sql_where_condition_from_numerical_value_list(minus_results)}) " if len(minus_results) > 0 else ""
        sql = self.inputs[0].create_sql_query(DB, additionals=additionals)

        return sql
    
    def set_inputs(self, inputs: List[Operator]) -> None:
        if len(inputs) != 2:
            raise ValueError(f'Difference combiner must have exactly two inputs.')
        return super().set_inputs(inputs)
