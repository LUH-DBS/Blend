import math
import time

from src.Tasks.UnionSearch import UnionSearch
from src.Tasks.SingleColumnJoinSearch import SingleColumnJoinSearch
from src.Tasks.CorrelationSearch import CorrelationSearch
from src.Tasks.MultiColumnJoinSearch import MultiColumnJoinSearch
from src.Tasks.ComplexSearch import ComplexSearch

import pandas as pd
from collections import Counter


def main():
    # Load query
    df = pd.read_csv('data/benchmarks/ComplexTask/imdb.csv')[['movie_title', 'director_name', 'imdb_score']]
    examples = df.head(math.ceil(len(df)/2)).iloc[:, :2].apply(lambda x: x.astype(str).str.lower())
    query = df.tail(math.floor(len(df)/2)).apply(lambda x: x.astype(str).str.lower())[df.columns[0]]
    target = df[df.columns[-1]]

    # Search for unionable tables
    task = ComplexSearch(examples, query, target, k=10)
    task.DB.index_table = 'santos_small_blend'
    t = time.time()
    result_ids = task.run()
    print(f'runtime: {time.time() - t}')
    task.DB.close()
    print(result_ids)

if __name__ == "__main__":
    main()