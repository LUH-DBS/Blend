from src.Operators.Combiners.CombinerBase import Combiner

# Typing imports
from src.DBHandler import DBHandler


class Union(Combiner):

    def create_sql_query(self, db: DBHandler, additionals: str = "") -> str:
        sql = """
        (
        """
        for i, input_ in enumerate(self._inputs):
            sql += input_.create_sql_query(db, additionals=additionals)
            sql += ")"
            if i < len(self._inputs) - 1:
                sql += " UNION "
                sql += "("
        sql += f"""
        LIMIT {self.k}
        """

        return sql
