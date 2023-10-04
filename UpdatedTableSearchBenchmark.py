from src.Tasks.NegativeExampleSearch import UpdatedTableSearch

import pandas as pd
from pathlib import Path


data_dir = Path('data/benchmarks/UpdatedTableSearch/data/')

query = pd.read_csv(data_dir / 'players_2008.csv').apply(lambda x: x.astype(str).str.lower())
updates = pd.read_csv(data_dir / 'updates_2008_2012.csv').apply(lambda x: x.astype(str).str.lower())
ground_truth = pd.read_csv(data_dir / 'players_2012.csv').apply(lambda x: x.astype(str).str.lower())



updated_query = query.merge(updates, how='left', on='player_name')
old_and_outdated = query[updated_query.notna().all(axis=1)]
updated_query.iloc[:, 2].fillna(updated_query.iloc[:, 1], inplace=True)
updated_query = updated_query.drop(columns=[updated_query.columns[1]])

task = UpdatedTableSearch(updated_query.iloc[:, 0], updated_query.iloc[:, 1], old_and_outdated.iloc[:, 0], old_and_outdated.iloc[:, 1], k=10)
result_ids = task.run()
print(result_ids)

results = []
for result_id in result_ids:
    results.append(task.DB.get_table_from_index(result_id))
    print(results[-1])



