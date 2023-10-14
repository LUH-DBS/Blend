from src.Tasks.UnionSearch import UnionSearch
from src.Tasks.SingleColumnJoinSearch import SingleColumnJoinSearch
from src.Tasks.CorrelationSearch import CorrelationSearch
from src.Tasks.MultiColumnJoinSearch import MultiColumnJoinSearch

import pandas as pd
from collections import Counter


def main():
    
    # Load query
    query = pd.read_csv('data/benchmarks/ComplexTask/data/query.csv')

    # Search for unionable tables
    task = UnionSearch(query, k=2)
    task.DB.index_table = 'santos_small_super_key'
    result_ids = task.run()
    results = [task.DB.get_table_from_index(table_id) for table_id in result_ids]
    task.DB.close()

    ## Union the tables
    query_columns = list(query.columns)
    unionable_results = []
    for result in results:
        union_columns = []
        for query_column in query_columns:
            overlaps = Counter()
            for result_column in result.columns:
                overlaps[result_column] = len(set(result[result_column].unique()).intersection(set(query[query_column].unique())))
            union_columns.append(overlaps.most_common(1)[0][0])
        unionable_results.append(result[union_columns])

    intermediate_results_after_union = []
    for result in unionable_results:
        result.columns = query_columns

        intermediate_result = pd.concat([query, result], axis=0, ignore_index=True)
        intermediate_result = intermediate_result[intermediate_result['GRADE'].isin(['a', 'b', 'c'])]
        intermediate_result = intermediate_result.groupby('DBA').agg(lambda x: m.iloc[0] if (m := x.mode()).size else x.iloc[0]).reset_index()
        intermediate_result.reset_index(drop=True, inplace=True)
        
        intermediate_results_after_union.append(intermediate_result)


            

    # Search for joinable tables
    intermediate_results_after_join = []
    for intermediate_result in intermediate_results_after_union:
        task = SingleColumnJoinSearch(intermediate_result['DBA'], k=2)
        task.DB.index_table = 'santos_small_super_key'
        result_ids = task.run()
        results = [task.DB.get_table_from_index(table_id) for table_id in result_ids]

        ## Join the tables
        for result in results:
            overlaps = Counter()
            for column in result.columns:
                overlaps[column] = len(set(result[column].unique()).intersection(set(intermediate_result['DBA'].unique())))
            join_column = overlaps.most_common(1)[0][0]
            result = result.groupby(join_column).agg(lambda x: m.iloc[0] if (m := x.mode()).size else x.iloc[0]).reset_index()
            
            intermediate_result = pd.merge(intermediate_result, result.add_sufix("_join"), left_on='DBA', right_on=join_column, how='left')
            intermediate_result.reset_index(drop=True, inplace=True)
            intermediate_results_after_join.append(intermediate_result)

    # Search for correlated tables
    intermediate_results_after_correlation = []
    for intermediate_result in intermediate_results_after_join:
        source_column = list(intermediate_result['DBA'])
        intermediate_result['SCORE'] = intermediate_result['GRADE'].map({'a': 10, 'b': 20, 'c': 40})
        target_column = list(intermediate_result['SCORE'])

        task = CorrelationSearch(source_column=source_column, target_column=target_column, k=2)
        task.DB.index_table = 'santos_small_tokenized_quadrants'
        result_ids = task.run()
        results = [task.DB.get_table_from_index(table_id) for table_id in result_ids]

        ## Join the tables
        for result in results:
            overlaps = Counter()
            for column in result.columns:
                overlaps[column] = len(set(result[column].unique()).intersection(set(intermediate_result['DBA'].unique())))
            join_column = overlaps.most_common(1)[0][0]
            for column in result.columns:
                if column != join_column:
                    numeric_column = pd.to_numeric(result[column], errors='coerce')
                    if numeric_column.notnull().any():
                        result[column] = numeric_column
                    else:
                        result.drop(column, axis=1, inplace=True)

            result = result.groupby(join_column).mean().reset_index()
            intermediate_result = pd.merge(intermediate_result, result, left_on='DBA', right_on=join_column, how='left', suffixes=('', '_correlation'))
            intermediate_result.reset_index(drop=True, inplace=True)
            intermediate_results_after_correlation.append(intermediate_result)

    # Evaluate results by hand
    for i, result in enumerate(intermediate_results_after_correlation):
        result.to_csv(f'data/benchmarks/ComplexTask/data/result_{i}.csv', index=False)


if __name__ == "__main__":
    main()