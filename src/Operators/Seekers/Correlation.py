from src.Operators.OperatorBase import Operator
import numpy as np
import pandas as pd


class Correlation(Operator):

    def __init__(self, source_values, target_values, k=10):
        Operator.__init__(self)
        self.type = 'quadrantapproximation'

        grouped = pd.DataFrame({'source': source_values, 'target': target_values}).dropna().groupby('source').mean()

        self.input_source = grouped.index.values
        self.input_target = grouped['target'].values
        self.k = k
        self.base_sql = f"""
        $INIT$
        SELECT TableId
        FROM (
            SELECT * FROM (
                SELECT TableId, sum((CellValue IN ($TRUETOKENS$) = QDR)::int) * 2 - count(*) as score
                FROM (
                    SELECT
                        categorical.CellValue,
                        categorical.TableId,
                        categorical.ColumnId catcol,
                        numerical.ColumnId numcol,
                        sum(numerical.QDR::int) / count(*) > 0.5 as QDR,
                        count(distinct numerical.CellValue) as num_unique,
                        min(numerical.CellValue) as any_cellvalue
                    FROM (SELECT * FROM AllTables WHERE rowid < 256 AND (CellValue IN ($FALSETOKENS$) OR CellValue IN ($TRUETOKENS$)) $ADDITIONALS$) categorical
                    JOIN (SELECT * FROM AllTables WHERE rowid < 256 AND QDR is not NULL $ADDITIONALS$) numerical
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

    def create_sql_query(self):
        self.input_target = self.input_target.astype(float)
        target_average = np.mean(self.input_target)
        target_int = np.where(self.input_target >= target_average, 1, 0)
        target_int = target_int.astype(int)
        self.input_source = self.clean_value_collection(self.input_source)
        source_0 = self.create_sql_where_condition_from_value_list(
            [key for key, qdr in zip(self.input_source, target_int) if qdr == 0])
        source_1 = self.create_sql_where_condition_from_value_list(
            [key for key, qdr in zip(self.input_source, target_int) if qdr == 1])

        self.sql = self.base_sql\
            .replace('$FALSETOKENS$', source_0).replace('$TRUETOKENS$', source_1).replace('$TOPK$', f'{self.k}')\
            .replace('$INIT$', '').replace('$ADDITIONALS$', '')

    def optimize(self, by, set_operation_type, create_executable_query=False):  # by, is an operator that we would like to optimize the sql based on
        linear = False  # If False means that the optimization merged the nodes and we don't need to linearly connect them together
        if set_operation_type == 'set_intersection':
            if by.type == 'intersection':
                by.create_sql_query()
                self.base_sql = self.base_sql.replace('$ADDITIONALS$', f' AND TableId IN ($PREVIOUSSTEP_MUST$) $ADDITIONALS$')
                self.k = min(self.k, by.k)
            elif by.type == 'multicolumnintersection':
                by.create_sql_query()
                self.base_sql = self.base_sql.replace('$ADDITIONALS$', f' AND TableId IN ($PREVIOUSSTEP_MUST$) $ADDITIONALS$')
            elif by.type == 'quadrantapproximation':
                by.create_sql_query()
                self.base_sql = self.base_sql.replace('$ADDITIONALS$', f' AND TableId IN ($PREVIOUSSTEP_MUST$) $ADDITIONALS$')
            linear = True
        elif set_operation_type == 'set_union':
            if by.type == 'intersection':
                self.base_sql = self.base_sql.replace('$ADDITIONALS$', f' OR CellValue IN ({self.create_sql_where_condition_from_value_list(self.clean_value_collection(by.input))}) $ADDITIONALS$ ')
                self.k = self.k + by.k
            elif by.type == 'multicolumnintersection':
                by.create_sql_query()
                self.base_sql = self.base_sql.replace('$ADDITIONALS$', f' OR TableId IN ($PREVIOUSSTEP_MUST$) $ADDITIONALS$')
                linear = True
            elif by.type == 'quadrantapproximation':
                by.create_sql_query()
                self.base_sql = self.base_sql.replace('$INIT$', f' $INIT$ {by.sql} UNION DISTINCT ')
                self.k = self.k + by.k
        elif set_operation_type == 'set_difference':
            if by.type == 'intersection':
                by.create_sql_query()
                self.base_sql = self.base_sql.replace('$ADDITIONALS$', f' AND TableId NOT IN ($PREVIOUSSTEP_MUST$) $ADDITIONALS$')
            elif by.type == 'multicolumnintersection':
                by.create_sql_query()
                self.base_sql = self.base_sql.replace('$ADDITIONALS$', f' AND TableId NOT IN ($PREVIOUSSTEP_MUST$) $ADDITIONALS$')
            elif by.type == 'quadrantapproximation':
                by.create_sql_query()
                self.base_sql = self.base_sql.replace('$ADDITIONALS$', f' AND TableId NOT IN ($PREVIOUSSTEP_MUST$) $ADDITIONALS$')
            linear = True
        if create_executable_query:
            self.create_sql_query()
        return linear
