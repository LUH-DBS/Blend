from src.Operators import Combiners, Seekers
from src.Plan import Plan

# Typing imports
import pandas as pd
from typing import Iterable


def ComplexSearch(examples: pd.DataFrame, queries: Iterable[str], target: Iterable[float], k: int = 2) -> Plan:
    plan = Plan()

    # imputation sub-pipline
    # plan.add("imputation_example", Seekers.MC(examples, k * 10))
    # plan.add("imputation_query", Seekers.SC(queries, k * 30))
    # plan.add("imputation_combiner", Combiners.Intersection(k=k), inputs=["imputation_example", "imputation_query"])


    # union sub-pipline
    for clm_name in examples.columns:
        plan.add(clm_name, Seekers.SC(examples[clm_name], k * 10))
    plan.add("union_counter", Combiners.Counter(k=k), inputs=examples.columns)

    # join sub_pipeline
    plan.add("join_query", Seekers.SC(examples[examples.columns[0]], k))

    # correlation sub_pipeline
    plan.add("correlation_query", Seekers.Correlation(examples[examples.columns[0]], target, k))

    # final combiner
    plan.add("final_union", Combiners.Union(k=k*4), inputs=["union_counter", "join_query", "correlation_query"])

    return plan
