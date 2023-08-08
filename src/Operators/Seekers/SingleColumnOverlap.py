from src.Operators.Seekers.SeekerBase import Seeker

# Typing imports
from src.DBHandler import DBHandler
from typing import Iterable

class SingleColumnOverlap(Seeker):
    def __init__(self, input_query_values: Iterable[str], k: int=10) -> None:
        super().__init__(k)
        self.input = set(input_query_values)
        self.base_sql = """
        SELECT TableId FROM AllTables
        WHERE CellValue IN ($TOKENS$) $ADDITIONALS$
        GROUP BY TableId, ColumnId
        ORDER BY COUNT(DISTINCT CellValue) DESC
        LIMIT $TOPK$
        """

    def create_sql_query(self, DB: DBHandler, additionals: str="") -> str:
        sql = self.base_sql.replace('$TOPK$', f'{self.k}')
        sql = sql.replace('$ADDITIONALS$', additionals)
        sql = sql.replace('$TOKENS$', DB.create_sql_where_condition_from_value_list(DB.clean_value_collection(self.input)))

        return sql


    def cost(self) -> int:
        return 4
