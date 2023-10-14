import glob
import time
from tqdm import tqdm
from src.Tasks.MultiColumnCollinearitySearch import MultiColumnCollinearitySearch
import pandas as pd
import numpy as np

runtime = []
for input_query_path in tqdm(list(sorted(glob.glob('data/benchmarks/MultiColumnCollinearity/data/santos_small/*.csv')))):
    # Process input query
    query = pd.read_csv(input_query_path).dropna()
    print(len(query))
    query.columns = [i for i in range(len(query.columns))]
    query = query.apply(lambda x: x.astype(str).str.lower())
    for numeric_column in [2, 3]:
        query[numeric_column] = pd.to_numeric(query[numeric_column], errors='coerce')

    # Run task
    task = MultiColumnCollinearitySearch(query, 0, 2, 3, [0, 1], 10)
    task.DB.index_table = "santos_small_blend"
    start_time = time.time()
    try:
        results = task.run()
    except:
        print(f'Error on {input_query_path}')
        continue
    print(results)
    runtime += [time.time()-start_time]
    task.DB.close()
    
print(f'Average Runtime: {np.mean(runtime)}')
