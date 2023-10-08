from src.Operators.Seekers.SeekerBase import Seeker
import numpy as np
import pandas as pd

# Typing imports
from src.DBHandler import DBHandler
from typing import List
from numbers import Number


class Correlation(Seeker):

    def __init__(self, source_values: List[str], target_values: List[Number], k: int = 10) -> None:
        super().__init__(k)

        grouped = pd.DataFrame({'source': source_values, 'target': target_values}).dropna().groupby('source').mean()
        self.input_source = grouped.index.values
        self.input_target = grouped['target'].values
        self.hash_size = 10

        self.base_sql = f"""
        SELECT TableId
        FROM (
            SELECT * FROM (
                SELECT TableId, sum((CellValue IN ($TRUETOKENS$) = Quadrant)::int) * 2 - count(*) as score
                FROM (
                    SELECT
                        categorical.CellValue,
                        categorical.TableId,
                        categorical.ColumnId catcol,
                        numerical.ColumnId numcol,
                        sum(numerical.Quadrant::int) / count(*) > 0.5 as Quadrant,
                        count(distinct numerical.CellValue) as num_unique,
                        min(numerical.CellValue) as any_cellvalue
                    FROM (SELECT * FROM AllTables WHERE rowid < {self.hash_size} AND (CellValue IN ($FALSETOKENS$)
                                                        OR CellValue IN ($TRUETOKENS$)) $ADDITIONALS$) categorical
                    JOIN (SELECT * FROM AllTables WHERE rowid < {self.hash_size} AND Quadrant is not NULL $ADDITIONALS$) numerical
                        ON categorical.TableId = numerical.TableId AND categorical.RowId = numerical.RowId
                    GROUP BY categorical.TableId, categorical.ColumnId, numerical.ColumnId, categorical.CellValue
                ) grouped_cellvalues
                GROUP BY TableId, catcol, numcol
                HAVING count(*) > 1 and (count(distinct any_cellvalue) > 1 or sum(num_unique) > count(*))
            ) scores
            ORDER BY abs(score) DESC
            LIMIT $TOPK$
        ) inner_union
        """

    def create_sql_query(self, db: DBHandler, additionals: str = "") -> str:
        self.input_target = self.input_target.astype(float)
        target_average = np.mean(self.input_target)
        target_int = np.where(self.input_target >= target_average, 1, 0)
        target_int = target_int.astype(int)
        self.input_source = db.clean_value_collection(self.input_source)
        source_0 = db.create_sql_list_str(
            [key for key, qdr in zip(self.input_source, target_int) if qdr == 0])
        source_1 = db.create_sql_list_str(
            [key for key, qdr in zip(self.input_source, target_int) if qdr == 1])
        
        sql = self.base_sql.replace("$TOPK$", f"{self.k}")
        sql = sql.replace("$ADDITIONALS$", additionals)
        sql = sql.replace("$FALSETOKENS$", source_0)
        sql = sql.replace("$TRUETOKENS$", source_1)

        return sql

    def cost(self) -> int:
        return 10
