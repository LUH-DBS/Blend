from typing import List
from src.Operators.OperatorBase import Operator
from src.Operators.Combiners.CombinerBase import Combiner

# Typing imports
from src.DBHandler import DBHandler


class Distinct(Combiner):
    def __init__(self, input_: Operator, k: int = 10) -> None:
        super().__init__(input_, k=k)

    def create_sql_query(self, db: DBHandler, additionals: str = "") -> str:
        sql = """SELECT DISTINCT TableId FROM (
        """
        sql += self.inputs[0].create_sql_query(db, additionals=additionals)
        sql += f""") AS {db.random_subquery_name()} LIMIT {self.k}
        """

        return sql
    