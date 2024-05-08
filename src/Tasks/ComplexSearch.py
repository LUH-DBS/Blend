from src.Operators import Combiners, Seekers
# Typing imports
import pandas as pd
from typing import Iterable
from src.Operators.OperatorBase import Operator


def ComplexSearch(examples: pd.DataFrame, queries: Iterable[str], target: Iterable[float], k: int = 2) -> Operator:
    # imputation sub-pipline
    # imputation_example = Seekers.MC(examples, k * 10)
    # imputation_query = Seekers.SC(queries, k * 30)
    # imputation_combiner = Combiners.Intersection(imputation_example, imputation_query, k=k)


    # union sub-pipline
    union_seekers = []
    for clm_name in examples.columns:
        element = Seekers.SC(examples[clm_name], k * 10)
        union_seekers.append(element)
    union_counter = Combiners.Counter(*union_seekers, k=k)

    # join sub_pipeline
    join_query = Seekers.SC(examples[examples.columns[0]], k)

    # correlation sub_pipeline
    correlation_query = Seekers.Correlation(examples[examples.columns[0]], target, k)

    # final combiner
    final_union = Combiners.Union(union_counter, join_query, correlation_query, k=k*4)

    return final_union
