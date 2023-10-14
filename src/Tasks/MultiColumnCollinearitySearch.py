from src.Plan import Plan
from src.Operators import Terminal, Input, Combiners
from src.Operators.Seekers import Correlation, MultiColumnOverlap


# typing imports
import pandas as pd
from typing import List


def MultiColumnCollinearitySearch(query_dataset: pd.DataFrame, source_column_name: str, target_column_name: str, numerical_feature_column_name: str, multi_column_column_names: List[str], k: int = 10) -> Plan:
    plan = Plan()
    input_element = Input(query_dataset)
    plan.add('input', input_element, [])
    element_included = Correlation(query_dataset[source_column_name], query_dataset[target_column_name], k)
    plan.add('query_included', element_included, ['input'])
    element_excluded = Correlation(query_dataset[source_column_name], query_dataset[numerical_feature_column_name], k)
    plan.add('query_excluded', element_excluded, ['input'])
    plan.add('difference', Combiners.Difference(k), ['query_included', 'query_excluded'])
    mc_seeker = MultiColumnOverlap(query_dataset[[source_column_name, target_column_name]], k*2)
    plan.add('query_mc', mc_seeker, ['input'])
    intersection = Combiners.Intersection(k)
    plan.add('intersection', intersection, ['query_mc', 'difference'])
    plan.add('terminal', Terminal(), ['intersection'])
    return plan
