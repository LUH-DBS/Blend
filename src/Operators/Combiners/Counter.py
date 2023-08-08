from src.Operators.Combiners.CombinerBase import Combiner

# Typing imports
from src.DBHandler import DBHandler

class Counter(Combiner):
    def __init__(self, k: int=10):
        super().__init__(k)

    def create_sql_query(self, DB: DBHandler, additionals: str="") -> str:
        sql = """
        SELECT TableId FROM (
        (
        """
        for i, input in enumerate(self.inputs):
            sql += input.create_sql_query(DB, additionals=additionals)
            sql += ")"
            if i < len(self.inputs) - 1:
                sql += " UNION ALL "
                sql += "("
        sql += f"""
        ) AS {DB.random_subquery_name()}
        GROUP BY TableId
        ORDER BY COUNT(TableId) DESC
        LIMIT {self.k}
        """

        return sql
