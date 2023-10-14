from src.Plan import Plan
from src.Operators import Terminal, Input, Combiners
from src.Operators.Seekers import SingleColumnOverlap

from typing import List
# typing imports
import pandas as pd


def FeatureForMLSearch(query_dataset: pd.DataFrame, dependent_column_names_1: List[str], dependent_column_names_2: List[str], k: int = 10) -> Plan:
    plan = Plan()
    input_element = Input(query_dataset)
    plan.add('input', input_element, [])
    element_c1 = SingleColumnOverlap(query_dataset[dependent_column_names_1][0], k)
    element_c2 = SingleColumnOverlap(query_dataset[dependent_column_names_1][1], k)
    element_c3 = SingleColumnOverlap(query_dataset[dependent_column_names_2][0], k)
    element_c4 = SingleColumnOverlap(query_dataset[dependent_column_names_2][1], k)
    plan.add('query_c1', element_c1, ['input'])
    plan.add('query_c2', element_c2, ['input'])
    plan.add('query_c3', element_c3, ['input'])
    plan.add('query_c4', element_c4, ['input'])

    plan.add('intersection_1', Combiners.Intersection(k), ['query_c1', 'query_c2'])
    plan.add('intersection_2', Combiners.Intersection(k), ['query_c3', 'query_c4'])
    plan.add('union', Combiners.Union(k), ['intersection_1', 'intersection_2'])
    plan.add('terminal', Terminal(), ['union'])
    return plan
