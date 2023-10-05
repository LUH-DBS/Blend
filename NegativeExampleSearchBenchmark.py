import math
import time
import numpy as np
from src.Tasks.NegativeExampleSearch import NegativeExampleSearch
import glob
import pandas as pd
from pathlib import Path


data_dir = Path('data/benchmarks/NegativeExampleSearch/data/webtable_benchmark/10/')
runtime = []
for input_query_path in glob.glob('data/benchmarks/NegativeExampleSearch/data/webtable_benchmark/10/72097009*.csv'):

    all = pd.read_csv(input_query_path).apply(lambda x: x.astype(str).str.lower())
    if len(all) < 4:
        continue
    inclusive_row_numbers = math.ceil(len(all)/2)
    exclusive_row_numbers = math.floor(len(all)/2)
    inclusive_rows = all.head(inclusive_row_numbers)
    exclusive_rows = all.tail(exclusive_row_numbers)

    task = NegativeExampleSearch(inclusive_rows, inclusive_rows.columns.values[0], inclusive_rows.columns.values[1], exclusive_rows, exclusive_rows.columns.values[0], exclusive_rows.columns.values[1], k=10)
    start_time = time.time()
    result_ids = task.run()
    runtime += [time.time() - start_time]
    # print(result_ids)

    results = []
    for result_id in result_ids:
        results.append(task.DB.get_table_from_index(result_id))
        # print(results[-1])

    # Validation phase

    TP = 0
    for candidate_table in results:
        exclusive_values = exclusive_rows.values
        flag = True
        for exclusive_value_pair in exclusive_values:
            for candidate_row in candidate_table.values:
                if np.isin(exclusive_value_pair, candidate_row).all():
                   flag = False
                   break;
        if flag:
            TP += 1
    print('-------------------------')
    print(input_query_path)
    print(TP, len(results))



