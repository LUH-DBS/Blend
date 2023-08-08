from src.Operators.Combiners.CombinerBase import Combiner

# Typing imports
from src.DBHandler import DBHandler


class Union(Combiner):
    def __init__(self, k: int = 10):
        super().__init__(k)

    def create_sql_query(self, db: DBHandler, additionals: str = "") -> str:
        sql = """
        (
        """
        for i, input_ in enumerate(self.inputs):
            sql += input_.create_sql_query(db, additionals=additionals)
            sql += ")"
            if i < len(self.inputs) - 1:
                sql += " UNION "
                sql += "("
        sql += f"""
        LIMIT {self.k}
        """

        return sql
