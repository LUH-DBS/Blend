import math
import time
import numpy as np
from src.Tasks.NegativeExampleSearch import NegativeExampleSearch
import glob
import pandas as pd
from tqdm import tqdm
from pathlib import Path
from src.utils import Logger


logger = Logger(clear_logs=True)
log_name = 'NegativeExampleLogs'
runtime = []
TPs = []
total_table_count = []
precisions = []
negative_example_size = []
for counter in tqdm(np.arange(0, 403)):
    try:
        inclusive_rows = pd.read_csv(f'data/benchmarks/NegativeExampleSearch/data/santos/inclusive_{counter}.csv').apply(lambda x: x.astype(str).str.lower())
        exclusive_rows = pd.read_csv(f'data/benchmarks/NegativeExampleSearch/data/santos/exclusive_{counter}.csv').apply(lambda x: x.astype(str).str.lower())
    except FileNotFoundError:
        continue

    task = NegativeExampleSearch(inclusive_rows, inclusive_rows.columns.values[0], inclusive_rows.columns.values[1], exclusive_rows, exclusive_rows.columns.values[0], exclusive_rows.columns.values[1], k=10)
    task.DB.index_table = "santos_small_super_key"
    start_time = time.time()
    try:
        result_ids = task.run()
    except:
        continue
    runtime += [time.time() - start_time]

    
    logger.log(log_name, {
        "query_id": counter,
        "time": runtime[-1],
    })


print(np.mean(runtime))


