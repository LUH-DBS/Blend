import math
import time
import numpy as np
from src.Tasks.NegativeExampleSearch import NegativeExampleSearch
import glob
import pandas as pd
from tqdm import tqdm
from pathlib import Path
from src.utils import Logger

def validate(candidate_table, exclusive_rows):
    exclusive_values = exclusive_rows.values
    candidate_columns_0 = []
    candidate_columns_1 = []

    candidate_column_sets = dict()
    exclusive_column_sets = dict()

    for column in candidate_table.columns:
        candidate_column_sets[column] = set(candidate_table[column].values)

    for i, column in enumerate(exclusive_rows.columns):
        exclusive_column_sets[i] = set(exclusive_rows[column].values)

    for column in candidate_column_sets:
        if exclusive_column_sets[0].intersection(candidate_column_sets[column]):
            candidate_columns_0.append(column)
        if exclusive_column_sets[1].intersection(candidate_column_sets[column]):
            candidate_columns_1.append(column)

    from itertools import product
    tuples_exclusive = set(exclusive_rows.itertuples(index=False, name=None))
    for column_0, column_1 in product(candidate_columns_0, candidate_columns_1):
        if column_0 == column_1:
            continue
        tuples_candidate = set(candidate_table[[column_0, column_1]].itertuples(index=False, name=None))
        if len(tuples_candidate.intersection(tuples_exclusive)) > 0:
            return False

    return True
# data_dir = Path('data/benchmarks/NegativeExampleSearch/data/santos/')


logger = Logger(clear_logs=True)
log_name = 'NegativeExampleLogs'
runtime = []
TPs = []
total_table_count = []
precisions = []
for counter in tqdm(np.arange(0, 803)):
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
        flag = validate(candidate_table, exclusive_rows)
        if flag:
            TP += 1
    TPs += [TP]
    total_table_count += [len(results)]
    print('-------------------------')
    logger.log(log_name, {
        "query_id": counter,
        "precision": TP/len(results),
        "time": runtime[-1],
    })
    print(counter)
    print(TP, len(results))
    if len(results) > 0:
        precisions += [TP/len(results)]
print(f'FINAL PRECISION (AVERAGE): {np.mean(precisions)}')
print(np.mean(runtime))


