import math
import time
import numpy as np
from src.Tasks.NegativeExampleSearch import NegativeExampleSearch
import glob
import pandas as pd
from pathlib import Path


# data_dir = Path('data/benchmarks/NegativeExampleSearch/data/santos/')
runtime = []
TPs = []
total_table_count = []
precisions = []
for counter in np.arange(0, 803):
    inclusive_rows = pd.read_csv(f'data/benchmarks/NegativeExampleSearch/data/santos/inclusive_{counter}.csv').apply(lambda x: x.astype(str).str.lower())
    exclusive_rows = pd.read_csv(f'data/benchmarks/NegativeExampleSearch/data/santos/exclusive_{counter}.csv').apply(lambda x: x.astype(str).str.lower())

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
    TPs += [TP]
    total_table_count += [len(results)]
    print('-------------------------')
    print(counter)
    print(TP, len(results))
    if len(results) > 0:
        precisions += [TP/len(results)]
print(f'FINAL PRECISION (AVERAGE): {np.mean(precisions)}')



