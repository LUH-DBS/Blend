from src.Operators.Seekers.SeekerBase import Seeker
import numpy as np
from collections import defaultdict
from heapq import heapify, heappush, heappop
from src.utils import calculate_xash

# Typing imports
from src.DBHandler import DBHandler
import pandas as pd
from typing import List


class MultiColumnOverlap(Seeker):
    def __init__(self, input_df: pd.DataFrame, k: int = 10) -> None:
        super().__init__(k)
        self.input = input_df
        self.base_sql = """
            SELECT firstcolumn.TableId, firstcolumn.RowId, firstcolumn.superkey, firstcolumn.CellValue,
                    firstcolumn.ColumnId $OTHER_SELECT_COLUMNS$
            FROM (
                SELECT TableId, RowId, CellValue, ColumnId, TO_BITSTRING(superkey) AS superkey
                FROM AllTables
                WHERE CellValue IN ($TOKENS$) $ADDITIONALS$
                ) AS firstcolumn $INNERJOINS$
        """

    def create_sql_query(self, db: DBHandler, additionals: str = "") -> str:
        firstcolumn_values = self.input[self.input.columns.values[0]]

        sql = self.base_sql.replace('$TOPK$', f'{self.k}')
        sql = sql.replace('$TOKENS$', db.create_sql_list_str(db.clean_value_collection(firstcolumn_values)))

        innerjoins = ''
        for column_index in range(1, len(self.input.columns.values)):
            column_values = self.input[self.input.columns.values[column_index]]
            column_name = self.input.columns.values[column_index]

            innerjoins += f"""
                INNER JOIN
                    (
                        SELECT TableId, RowId, CellValue, ColumnId FROM AllTables
                        WHERE CellValue IN ({db.create_sql_list_str(db.clean_value_collection(column_values))})
                            $ADDITIONALS$
                    ) AS clm_{column_name}
                ON firstcolumn.TableId = clm_{column_name}.TableID AND firstcolumn.RowId = clm_{column_name}.RowId
            """

            # other_select_columns = f' , clm_{column_name}.CellValue, clm_{column_name}.ColumnId $OTHER_SELECT_COLUMNS$ '
            # sql = sql.replace('$OTHER_SELECT_COLUMNS$', other_select_columns)
        
        sql = sql.replace('$OTHER_SELECT_COLUMNS$', '')
        sql = sql.replace('$INNERJOINS$', innerjoins)
        sql = sql.replace('$ADDITIONALS$', additionals)


        candidates = db.execute_and_fetchall(sql)
        results = self.run_filter(candidates, db)

        # Since we need an sql query we need to put the result into a subquery
        if len(results) == 0:
            return "SELECT TableId FROM AllTables WHERE 1=0"
        
        sql = f"""
            SELECT TableId FROM (
            {' UNION ALL '.join([f'SELECT {result} AS TableId' for result in results])}
            ) AS {db.random_subquery_name()}
        """

        return sql

    
    def cost(self) -> int:
        return 6


    def run_filter(self, PLs: List, db: DBHandler) -> List[int]:
        # - Preprocessing
        PL_dictionary = defaultdict(list)
        PL_candidate_structure = {}
        for tablerow_superkey in PLs:
            table = tablerow_superkey[0]
            row = tablerow_superkey[1]
            superkey = tablerow_superkey[2]
            token = tablerow_superkey[3]
            colid = tablerow_superkey[4]
            tokens = [tablerow_superkey[x] for x in np.arange(5, len(tablerow_superkey), 2)]
            cols = [tablerow_superkey[x] for x in np.arange(6, len(tablerow_superkey), 2)]
            PL_dictionary[table].append((row, superkey, token, colid))
            PL_candidate_structure[(table, row)] = [tokens, cols]

        top_joinable_tables = []  # each item includes: Tableid, joinable_rows
        
        query_columns = self.input.columns.values
        # Calculate superkey for all input rows
        self.input['SuperKey'] = self.input.apply(lambda row: self.hash_row_vals(row), axis=1)

        # Get all rows grouped by first token of each row
        g = self.input.groupby([self.input.columns.values[0]])
        gd = {}
        for key, item in g:
            gd[str(key[0])] = g.get_group(key[0]).values

        candidate_external_row_ids = []
        candidate_external_col_ids = []
        candidate_input_rows = []
        candidate_table_rows = []
        candidate_table_ids = []
        all_pls = 0
        total_approved = 0
        total_match = 0
        overlaps_dict = {}
        super_key_index = list(self.input.columns.values).index('SuperKey')
        checked_tables = 0
        max_table_check = 10000000
        for tableid in sorted(PL_dictionary, key=lambda k: len(PL_dictionary[k]), reverse=True)[:max_table_check]:
            checked_tables += 1
            if checked_tables == max_table_check:
                # pruned = True
                break
            set_of_rowids = set()
            hitting_PLs = PL_dictionary[tableid]
            if len(top_joinable_tables) >= self.k and top_joinable_tables[0][0] >= len(hitting_PLs):
                # pruned = True
                break
            already_checked_hits = 0
            for hit in sorted(hitting_PLs):
                if len(top_joinable_tables) >= self.k and (
                        (len(hitting_PLs) - already_checked_hits + len(set_of_rowids)) <
                        top_joinable_tables[0][0]):
                    break
                rowid = hit[0]
                superkey = int(hit[1], 2)
                token = hit[2]
                colid = hit[3]
                relevant_input_rows = gd[token]
                for input_row in relevant_input_rows:
                    all_pls += 1
                    if (input_row[super_key_index] | superkey) == superkey:
                        candidate_external_row_ids += [rowid]
                        set_of_rowids.add(rowid)
                        candidate_external_col_ids += [colid]
                        candidate_input_rows += [input_row]
                        candidate_table_ids += [tableid]
                        candidate_table_rows += [f'{tableid}_{rowid}']
                already_checked_hits += 1
        if len(candidate_external_row_ids) > 0:
            candidate_input_rows = np.array(candidate_input_rows)
            candidate_table_ids = np.array(candidate_table_ids)
            

            joint_distinct_values = '\',\''.join(candidate_table_rows)
            joint_distinct_rows = '\',\''.join(set([str(x) for x in candidate_external_row_ids]))
            joint_distinct_tableids = '\',\''.join(set([str(x) for x in candidate_table_ids]))
            query = 'SELECT CONCAT(CONCAT(TableId, \'_\'), RowId), ColumnId, CellValue FROM (SELECT * from AllTables WHERE TableId in (\'{}\') and RowId in (\'{}\')) AS intermediate WHERE CONCAT(CONCAT(TableId, \'_\'), RowId) IN (\'{}\');'.format(
                joint_distinct_tableids, joint_distinct_rows, joint_distinct_values)

            pls_to_evaluate = db.execute_and_fetchall(query)
            table_row_dict = {}  # contains rowid that each rowid has dict that maps colids to tokenized
            for i in pls_to_evaluate:
                if i[0] not in table_row_dict:
                    table_row_dict[str(i[0])] = {}
                    table_row_dict[str(i[0])][str(i[1])] = str(i[2])
                else:
                    table_row_dict[str(i[0])][str(i[1])] = str(i[2])

            
            for i in np.arange(len(candidate_table_rows)):
                if str(candidate_table_rows[i]) not in table_row_dict:
                    continue
                col_dict = table_row_dict[str(candidate_table_rows[i])]
                match, matched_columns = self.evaluate_rows(candidate_input_rows[i], col_dict, query_columns)
                total_approved += 1
                if match:
                    total_match += 1
                    complete_matched_columns = '{}{}'.format(str(candidate_external_col_ids[i]), matched_columns)
                    if candidate_table_ids[i] not in overlaps_dict:
                        overlaps_dict[candidate_table_ids[i]] = {}

                    if complete_matched_columns in overlaps_dict[candidate_table_ids[i]]:
                        overlaps_dict[candidate_table_ids[i]][complete_matched_columns] += 1
                    else:
                        overlaps_dict[candidate_table_ids[i]][complete_matched_columns] = 1
            for tbl in set(candidate_table_ids):
                if tbl in overlaps_dict and len(overlaps_dict[tbl]) > 0:
                    join_keys = max(overlaps_dict[tbl], key=overlaps_dict[tbl].get)
                    joinability_score = overlaps_dict[tbl][join_keys]
                    if self.k <= len(top_joinable_tables):
                        if top_joinable_tables[0][0] < joinability_score:
                            popped_table = heappop(top_joinable_tables)
                            heappush(top_joinable_tables, [joinability_score, tbl, join_keys])
                    else:
                        heappush(top_joinable_tables, [joinability_score, tbl, join_keys])
        
        return [tableid for _, tableid, _ in top_joinable_tables[::-1]]

    def hash_row_vals(self, row: List[any]) -> int:
        hresult = 0
        for q in row:
            hvalue = calculate_xash(str(q))
            hresult = hresult | hvalue
        return hresult
    

    def evaluate_rows(self, input_row, col_dict, query_columns):
        vals = list(col_dict.values())
        query_cols_arr = np.array(query_columns)
        query_degree = len(query_cols_arr)
        matching_column_order = ''
        for q in query_cols_arr[-(query_degree - 1):]:
            q_index = list(query_columns).index(q)
            if input_row[q_index] not in vals:
                return False, ''
            else:
                for colid, val in col_dict.items():
                    if val == input_row[q_index]:
                        matching_column_order += '_{}'.format(str(colid))
        return True, matching_column_order
