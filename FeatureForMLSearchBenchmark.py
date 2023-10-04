import glob
import time

from src.Tasks.FeatureForMLSearch import FeatureForMLSearch
import pandas as pd
from collections import Counter
import numpy as np

runtime = []
for input_query_path in glob.glob('data/benchmarks/FeatureForMLSearch/data/*.csv'):
    query = pd.read_csv(input_query_path)
    input_column_names = query.columns.values
    query = query[[input_column_names[0], input_column_names[1], input_column_names[2]]].apply(lambda x: x.astype(str).str.lower())
    query.columns = [0, 1, 2]
    query[1] = pd.to_numeric(query[1], errors='coerce')
    query[2] = pd.to_numeric(query[2], errors='coerce')

# query = pd.read_csv('data/benchmarks/FeatureForMLSearch/data/world_happiness.csv')
# query = query[["Country or region", "Score", "Generosity"]].apply(lambda x: x.astype(str).str.lower())
# query.columns = [0, 1, 2]
# query[1] = pd.to_numeric(query[1], errors='coerce')
# query[2] = pd.to_numeric(query[2], errors='coerce')


    task = FeatureForMLSearch(query, 0, 1, 2, 10)
    start_time = time.time()
    result_ids = task.run()
    runtime += [time.time()-start_time]
    # result_ids = [73618111] # , 73618111, 140502337, 10977367, 10977367, 10977367, 15400287, 140502336, 10977367, 73618056, 59921649]
    results = []
    for result_id in result_ids:
        results.append(task.DB.get_table_from_index(result_id))

    correlating_column_values_to_target = []
    correlating_column_values_to_feature = []
    for result in results:
        result.columns = [i + 3 for i in range(len(result.columns))]
        # Find joinable column
        overlap = Counter()
        for column in result.columns:
            overlap[column] = query.iloc[:, 0].isin(result[column]).sum()
        joinable_column = overlap.most_common(1)[0][0]

        # Convert all other columns to numeric
        for column in result.columns:
            if column != joinable_column:
                result[column] = pd.to_numeric(result[column], errors='coerce')
                # check if column is only NaNs
                if result[column].isnull().all():
                    result = result.drop(columns=[column])

        grouped = result.groupby(joinable_column).mean()
        joined = pd.merge(query, grouped, left_on=0, right_index=True)

        # Calculate correlation
        to_target = joined.corr(numeric_only=True)[1].reset_index(drop=True)
        to_feature = joined.corr(numeric_only=True)[2].reset_index(drop=True)

        # Print results
        # print(joined)
        # print('----------------------------')
        # print(to_target)
        # print(to_feature)
        corr_list = [abs(x) for x in list(to_target.values)[2:]]
        if len(corr_list) < 1:
            continue
        max_correlating_col_index = corr_list.index(max(corr_list))+2
        # print(max_correlating_col_index)
        correlating_column_values_to_target += [abs(to_target[max_correlating_col_index])]
        correlating_column_values_to_feature += [abs(to_feature[max_correlating_col_index])]

    print('-------------------------------------------')
    print(input_query_path)
    correlating_column_values_to_target = [x for x in correlating_column_values_to_target if str(x) != 'nan']
    correlating_column_values_to_feature = [x for x in correlating_column_values_to_feature if str(x) != 'nan']
    print(np.mean(correlating_column_values_to_target))
    print(np.mean(correlating_column_values_to_feature))
    boolean_list = []
    for i in np.arange(len(correlating_column_values_to_target)):
        boolean_list += [correlating_column_values_to_target[i] >= correlating_column_values_to_feature[i]]
    print(f'{np.mean(np.array(boolean_list))} % of {len(correlating_column_values_to_target)} tables', )
print(f'Average Runtime: {np.mean(runtime)}')

