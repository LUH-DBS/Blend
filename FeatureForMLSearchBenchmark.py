from src.Tasks.FeatureForMLSearch import FeatureForMLSearch
import pandas as pd
from collections import Counter

query = pd.read_csv('data/benchmarks/FeatureForMLSearch/data/world_happiness.csv')
query = query[["Country or region", "Score", "GDP per capita"]].apply(lambda x: x.astype(str).str.lower())
query.columns = [0, 1, 2]
query[1] = pd.to_numeric(query[1], errors='coerce')
query[2] = pd.to_numeric(query[2], errors='coerce')


task = FeatureForMLSearch(query, 0, 1, 2, 10)

result_ids = task.run()
# result_ids = [73618111] # , 140502337, 10977367, 10977367, 10977367, 15400287, 140502336, 10977367, 73618056, 59921649]
results = []
print(result_ids)
exit(0)
for result_id in result_ids:
    results.append(task.DB.get_table_from_index(result_id))

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
    to_target = joined.corr(numeric_only=True)[1]
    to_feature = joined.corr(numeric_only=True)[2]

    # Print results
    print(joined)
    print(to_target)
    print(to_feature)
        


