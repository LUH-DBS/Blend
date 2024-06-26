from src.Operators.Combiners.CombinerBase import Combiner

# Typing imports
from src.DBHandler import DBHandler
from src.Operators.OperatorBase import Operator
from typing import Tuple


class Counter(Combiner):
    def create_sql_query(self, db: DBHandler, additionals: str = "") -> str:
        sql = """
        SELECT TableId FROM (
        (
        """
        for i, input_ in enumerate(self._inputs):
            sql += input_.create_sql_query(db, additionals=additionals)
            sql += ")"
            if i < len(self._inputs) - 1:
                sql += " UNION ALL "
                sql += "("
        sql += f"""
        ) AS {db.random_subquery_name()}
        GROUP BY TableId
        ORDER BY COUNT(TableId) DESC
        LIMIT {self.k}
        """

        return sql
