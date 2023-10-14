from src.Plan import Plan
from src.Operators import Terminal, Input, Combiners, Seekers
# Typing imports
import pandas as pd
from typing import Iterable


def ComplexSearch(examples: pd.DataFrame, queries: Iterable[str], target: Iterable[float], k: int = 2) -> Plan:
    plan = Plan()
    inputs = Input([examples, queries])
    plan.add('input', inputs)

    # imputation sub-pipline
    # examples_seeker = Seekers.MC(examples, k * 10)
    # plan.add('imputation_example', examples_seeker, ['input'])
    # query_seeker = Seekers.SC(queries, k * 30)
    # plan.add('imputation_query', query_seeker, ['input'])
    # plan.add('imputation_combiner', Combiners.Intersection(k), ['imputation_example', 'imputation_query'])

    # union sub-pipline
    for clm_name in examples.columns:
        element = Seekers.SC(examples[clm_name], k * 10)
        plan.add('union'+clm_name, element, ['input'])
    plan.add('union_counter', Combiners.Counter(k), ['union'+x for x in examples.columns])

    # join sub_pipeline
    element = Seekers.SC(examples[examples.columns[0]], k)
    plan.add('join_query', element, ['input'])

    # correlation sub_pipeline
    element = Seekers.Correlation(examples[examples.columns[0]], target, k)
    plan.add('correlation_query', element, ['input'])

    # final combiner
    plan.add('final_union', Combiners.Union(k*4), ['union_counter', 'join_query', 'correlation_query'])

    plan.add('terminal', Terminal(), ['final_union'])
    return plan
